
import os
import discord
from dotenv import load_dotenv

import random

load_dotenv()
TOKEN = "MTI4NDEzNDUxNjQ5MDc2ODQ1Nw.GGffW_.-EFTOgajUT2UNgjsAvAaX4EZAK987I6gycS_tg"

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_message(message):
    print(message)
    if message.author == client.user:
        return

   

    if message.content == '#99!':
        await message.channel.send("hi")

client.run(TOKEN)