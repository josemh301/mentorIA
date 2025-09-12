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

# Track processed messages to avoid duplicates
processed_messages = set()

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Skip if we've already processed this message
    if message.id in processed_messages:
        return
    
    # Add message to processed set
    processed_messages.add(message.id)
    
    # Clean old messages from set (keep only last 100)
    if len(processed_messages) > 100:
        processed_messages.clear()
    
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