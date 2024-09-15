import os
import logging
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from process import process_adapter, websocket_handler
import uvicorn

logging.basicConfig(level=logging.INFO)

class LineHookData(BaseModel):
    events: list
    destination: str

app = FastAPI(
    title="Line Webhook API",
    description="Line endpoint for webhook and message sending.",
    version="0.0.5",
    docs_url='/',
)

@app.post('/line/hook')
async def line_webhook(data: LineHookData , request: Request):
    try:
        # Now we can directly await process_adapter
        result = await process_adapter(data, request)
        return result
        return {"status": "ok"}, 200

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return {"status": "error", "message": "Internal server error"}, 500   

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    logging.info("New WebSocket connection attempt")
    await websocket_handler(websocket)

if __name__ == "__main__":
    uvicorn.run(app, port=int(os.environ.get("PORT", 8080)), host="0.0.0.0")