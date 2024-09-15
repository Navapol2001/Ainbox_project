import logging
from llm.message import message_sender
from llm.user_check import QuotaCheck, tier, customer_status
import requests
import asyncio
import os
from time import time
from cachetools import TTLCache
from fastapi import WebSocket, WebSocketDisconnect

msg = message_sender()
quota = QuotaCheck()
tier = tier()
user_status = customer_status()

# Rate limiting and deduplication
user_last_response = {}
event_cache = TTLCache(maxsize=1000, ttl=70)

# Configuration (Experiment with these values)
MAX_WORKERS = 2*os.cpu_count()  # Start with CPU core count
MAX_QUEUE_SIZE = 100  # Adjust based on expected request bursts

# Create a bounded Semaphore to limit concurrent tasks
semaphore = asyncio.Semaphore(MAX_WORKERS)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

def can_respond(user_id, cooldown=5):
    current_time = time()
    if user_id in user_last_response and current_time - user_last_response[user_id] < cooldown:
        return False
    user_last_response[user_id] = current_time
    return True

def is_duplicate_event(event_id):
    if event_id in event_cache:
        return True
    event_cache[event_id] = True
    return False

BACKEND_URL = os.getenv('Signature_Endpoint')    

async def process_adapter(data, request):
    # Check if events list is empty
    if not data.events:
        logging.warning("No events in the request")
        
        # Logic to handle when there are no events
        received_signature = request.headers.get('x-line-signature')
        body = await request.body()
        destinations = data.destination
        forward_data = {
            'body': body.decode('utf-8') if isinstance(body, bytes) else body,
            'signature': received_signature,
            'destination': destinations
        }
        signature_endpoint = f"{BACKEND_URL}/api/getSignature"
        
        try:
            async with semaphore:
                response = await asyncio.to_thread(
                    requests.post,
                    signature_endpoint,
                    json=forward_data,
                    headers={'X-Line-Signature': received_signature},
                    timeout=10
                )
            
            broadcast_body = await request.json()    
            if "destination" in broadcast_body and "events" in broadcast_body and isinstance(broadcast_body["events"], list):
                logging.info(f"Received webhook verification: {broadcast_body}")
                await manager.broadcast(broadcast_body.get("destination"))    
            
            if response.status_code == 200:
                logging.info("Data posted successfully to Signature_Endpoint")
                return {"status": "ok", "message": "No events, data forwarded to Signature_Endpoint"}
            else:
                logging.error(f"Error posting data to Signature_Endpoint. Status code: {response.status_code}")
                return {"status": "error", "message": "Failed to post data to Signature_Endpoint"}       
        except asyncio.QueueFull:
            logging.warning("Request queue full, dropping request.")
            return {"status": "error", "message": "Server overloaded"}, 503         
        except requests.RequestException as e:
            logging.error(f"Exception occurred while posting to Signature_Endpoint: {str(e)}")
            return {"status": "error", "message": "Exception occurred while posting to Signature_Endpoint"}

    # Process events if they exist
    for event in data.events:
        # Deduplication check
        if is_duplicate_event(event.get('webhookEventId')):
            logging.info(f"Duplicate event detected: {event.get('webhookEventId')}")
            continue

        message = event['message']
        user_id = event['source']['userId']
        check_status = quota.check_status(data.destination)
        get_status = user_status.get_status(page_id=data.destination, user_id=user_id)
        rank = tier.get_tier(data.destination)

        if check_status == True:
            if get_status == True:
                check_quota = quota.check_quota(data.destination)
                if message['type'] == 'text':
                    # Rate limiting check
                    if not can_respond(user_id):
                        logging.info(f"Rate limit applied for user: {user_id}")
                        continue

                    if check_quota == True:
                        msg.send_message_line(
                            user_id=user_id,
                            message=message['text'],
                            time_stamp=event['timestamp'],
                            page_id=data.destination,
                            rank=rank
                        )
                        quota.decrease_quota(data.destination)
                    else:
                        logging.info("Quota limit reached")
                        msg.bot_inactive_react(
                            method='line',
                            message=message['text'],
                            user_id=user_id,
                            time_stamp=event['timestamp'],
                            page_id=data.destination
                        )
                else:
                    msg.send_message_not_text(
                        method='line',
                        user_id=user_id,
                        time_stamp=event['timestamp'],
                        page_id=data.destination
                    )
            else:
                logging.info("User is inactive")
                msg.bot_inactive_react(
                    method='line',
                    user_id=user_id,
                    message=message['text'],
                    time_stamp=event['timestamp'],
                    page_id=data.destination
                )
        elif check_status == False:
            logging.info("Bot is inactive")
            msg.bot_inactive_react(
                method='line',
                user_id=user_id,
                message=message['text'],
                time_stamp=event['timestamp'],
                page_id=data.destination
            )
        else:
            logging.error("Unknown error in status check")
            return {"status": "error"}

    return {"status": "ok"}

async def websocket_handler(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)        