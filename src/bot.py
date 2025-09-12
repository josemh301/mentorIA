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

# The set for processing messages is now potentially redundant, as
# the architectural fix prevents the double-processing issue.
processed_messages = set()

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

@bot.listen()
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Optional check: skip if we've already processed this message
    # (Note: This is now largely unnecessary with the correct architectural pattern)
    if message.id in processed_messages:
        return
    
    # Add message to processed set (optional)
    processed_messages.add(message.id)
    
    # Clean old messages from set (optional, keep only last 100)
    if len(processed_messages) > 100:
        # Note: A proper deque or LRU cache would be more efficient for this
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

# The command handler for other commands can now be defined separately without conflict.
# For example:
# @bot.command()
# async def help(ctx):
#     await ctx.send("This is a command-based response.")

bot.run(TOKEN)