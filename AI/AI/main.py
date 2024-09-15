from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import logging
from pydantic import BaseModel
from .llm.llm import ChatAI  # Import your ChatAI class
import os
import asyncio
logging.basicConfig(level=logging.INFO)

# Initialize FastAPI


app = FastAPI()
chat_instance = ChatAI()  # Create a single instance of ChatAI


class Message(BaseModel):
    messages: str
    page_id: str
    user_id: str


# Configuration 
MAX_WORKERS = 2 * os.cpu_count()  
MAX_QUEUE_SIZE = 100  

# Create a bounded Semaphore to limit concurrent tasks
semaphore = asyncio.Semaphore(MAX_WORKERS)




@app.post("/chat/ec/v1/")
async def chat_ec_v1(Message: Message):
    """
    Endpoint for Ecommerce Chat v1
    """
    async with semaphore:  # Acquire semaphore for concurrency control
        try:

            response = await chat_instance.CHAT_EC_V1(Message.messages, Message.page_id, Message.user_id)
            return JSONResponse(content=response)

        except Exception as e:
            logging.error(f"Error in /chat/ec/v1/ endpoint: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/info/v1/")
async def chat_info_v1(Message: Message):
    """
    Endpoint for Information Chat v1
    """
    async with semaphore:  # Acquire semaphore for concurrency control
        try:
            response = await chat_instance.CHAT_INFO_V1(Message.messages, Message.page_id, Message.user_id)
            await quota.decrease_quota(Message.page_id)
            return JSONResponse(content=response)

        except Exception as e:
            logging.error(f"Error in /chat/ec/v1/ endpoint: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# Add more endpoints for CHAT_EC_V2, CHAT_INFO_V2 as needed

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
