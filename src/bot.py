import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from rag import ask_llm
import asyncio

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Only respond if the bot is mentioned
    if bot.user in message.mentions:
        # Extract the question after the mention
        content = message.content
        # Remove the mention from the content
        for mention in message.mentions:
            if mention == bot.user:
                content = content.replace(f'<@{mention.id}>', '').replace(f'<@!{mention.id}>', '').strip()
        
        if content:  # If there's a question after the mention
            try:
                async with message.channel.typing():
                    response = await asyncio.to_thread(ask_llm, content)
                
                await message.reply(response)
                    
            except Exception as e:
                await message.reply(f"Error: {str(e)}")
        else:
            await message.reply("¡Hola! Soy MentorIA. Pregúntame sobre inversiones inmobiliarias mencionándome: `@MentorIA <tu pregunta>`")

bot.run(TOKEN)