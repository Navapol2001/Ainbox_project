
import os
import logging
import discord
from dotenv import load_dotenv
import asyncio
from fastapi import FastAPI, WebSocket
from src.process import process_adapter
import uvicorn

logging.basicConfig(level=logging.INFO)
load_dotenv()
app = FastAPI(
    title="Discord_Hook",
    description="Discord endpoint for webhook and message sending.",
    version="0.0.1",
    docs_url='/',
)
TOKEN = os.getenv('TOKEN')
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)
bot_mentions = "<@1284134516490768457>"




@app.on_event("startup")
async def startup_event():
    """Start the Discord bot when FastAPI starts."""
    asyncio.create_task(bot.start(TOKEN))


@app.post('/')
async def main():
    return "Discord Server is running"


@bot.event
async def on_message(message):
    if bot_mentions in message.content:
        clean_content = message.content.replace(bot_mentions, "").strip()
        data = {
            "server_name":message.guild.name,
            "user_name":message.author.global_name,
            "msg":clean_content
        }
        if len(clean_content) != 0:
            msg = await process_adapter(data)
            await message.channel.send(msg)
        else:
            data["msg"] = "hi"
            msg = await process_adapter(data)
            await message.channel.send(msg)



if __name__ == "__main__":
    uvicorn.run(app, port=int(os.environ.get("PORT", 8080)), host="0.0.0.0")
