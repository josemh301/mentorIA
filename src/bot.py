import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from rag import ask_llm
import asyncio
import hashlib
import time

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Robust duplicate tracking system
processed_messages = {}  # Hash -> timestamp

def is_duplicate_message(message):
    """Check if message is a duplicate using content hash + time window"""
    # Create hash from author + content
    content_hash = hashlib.md5(f"{message.author.id}:{message.content.strip()}".encode()).hexdigest()
    current_time = time.time()
    
    # Check if we've seen this content recently (within 10 seconds)
    if content_hash in processed_messages:
        time_diff = current_time - processed_messages[content_hash]
        if time_diff < 10:  # 10 second window for duplicates
            return True
    
    # Mark this message as processed
    processed_messages[content_hash] = current_time
    
    # Clean old entries (older than 60 seconds)
    expired_keys = [k for k, v in processed_messages.items() if current_time - v > 60]
    for key in expired_keys:
        del processed_messages[key]
    
    return False

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    processed_messages.clear()  # Clear on restart

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Check for duplicates
    if is_duplicate_message(message):
        print(f"[DUPLICATE BLOCKED] {message.author}: {message.content[:30]}...")
        return
    
    # Check if the bot is mentioned
    if bot.user in message.mentions:
        print(f"[PROCESSING] Bot mentioned by {message.author}: {message.content[:50]}...")
        
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
                
                # Handle long responses (Discord 2000 char limit)
                if len(response) > 2000:
                    chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
                    for chunk in chunks:
                        await message.reply(chunk)
                else:
                    await message.reply(response)
                print(f"[SUCCESS] Responded to: {content[:30]}...")
                    
            except Exception as e:
                await message.reply(f"Error: {str(e)}")
        else:
            await message.reply("¡Hola! Soy MentorIA. Puedes preguntarme sobre inversiones inmobiliarias usando:\n• `!ask <tu pregunta>`\n• `!pregunta <tu pregunta>`\n• O simplemente mencionarme: `@MentorIA <tu pregunta>`")
        
        # Don't process commands if bot was mentioned
        return
    
    # Process commands normally (only if not a mention)
    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)  # in milliseconds
    await ctx.send(f"Pong! Latency: {latency}ms")

@bot.command()
async def ask(ctx, *, query: str):
    """Ask questions about real estate investments"""
    try:
        async with ctx.typing():
            response = await asyncio.to_thread(ask_llm, query)
        
        # Handle long responses (Discord 2000 char limit)
        if len(response) > 2000:
            chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
            for chunk in chunks:
                await ctx.send(chunk)
        else:
            await ctx.send(response)
            
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
async def pregunta(ctx, *, query: str):
    """Pregunta sobre inversiones inmobiliarias en español"""
    try:
        async with ctx.typing():
            response = await asyncio.to_thread(ask_llm, query)
        
        # Handle long responses (Discord 2000 char limit)
        if len(response) > 2000:
            chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
            for chunk in chunks:
                await ctx.send(chunk)
        else:
            await ctx.send(response)
            
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command(name='ayuda')
async def help_command(ctx):
    """Comando de ayuda"""
    embed = discord.Embed(
        title="Comandos Disponibles",
        description="Lista de comandos que puedes usar:",
        color=0x00ff00
    )
    embed.add_field(
        name="!ask <tu pregunta>",
        value="Haz una pregunta sobre inversiones inmobiliarias",
        inline=False
    )
    embed.add_field(
        name="!pregunta <tu pregunta>",
        value="Haz una pregunta sobre inversiones inmobiliarias",
        inline=False
    )
    embed.add_field(
        name="!ping",
        value="Verifica la latencia del bot",
        inline=False
    )
    embed.add_field(
        name="!ayuda",
        value="Muestra este mensaje de ayuda",
        inline=False
    )
    await ctx.send(embed=embed)

bot.run(TOKEN)