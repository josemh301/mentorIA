import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from rag import ask_llm
import asyncio
import hashlib
import time
import re

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Robust duplicate tracking system
processed_messages = {}  # Hash -> timestamp

def smart_chunk(text, max_length=1900):
    """Split text at natural boundaries to avoid cutting words/sentences"""
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    # Try to split at paragraph breaks first
    paragraphs = text.split('\n\n')
    
    for paragraph in paragraphs:
        # If paragraph fits in current chunk, add it
        if len(current_chunk + '\n\n' + paragraph) <= max_length:
            if current_chunk:
                current_chunk += '\n\n' + paragraph
            else:
                current_chunk = paragraph
        else:
            # Save current chunk if it exists
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
            
            # If paragraph itself is too long, split by sentences
            if len(paragraph) > max_length:
                sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                for sentence in sentences:
                    if len(current_chunk + ' ' + sentence) <= max_length:
                        if current_chunk:
                            current_chunk += ' ' + sentence
                        else:
                            current_chunk = sentence
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence
            else:
                current_chunk = paragraph
    
    # Add remaining chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

async def safe_reply(message, content):
    """Safely send message chunks that won't exceed Discord limits"""
    try:
        chunks = smart_chunk(content, 1900)  # Conservative limit for safety
        for i, chunk in enumerate(chunks):
            if i == 0:
                await message.reply(chunk)
            else:
                await message.channel.send(chunk)
    except Exception as e:
        # Fallback for very problematic content
        await message.reply(f"Error enviando respuesta: {str(e)}")

async def safe_send(ctx, content):
    """Safely send message chunks for commands"""
    try:
        chunks = smart_chunk(content, 1900)
        for chunk in chunks:
            await ctx.send(chunk)
    except Exception as e:
        await ctx.send(f"Error enviando respuesta: {str(e)}")

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
                
                # Use safe reply to handle long responses properly
                await safe_reply(message, response)
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
        
        # Use safe send to handle long responses properly
        await safe_send(ctx, response)
            
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
async def pregunta(ctx, *, query: str):
    """Pregunta sobre inversiones inmobiliarias en español"""
    try:
        async with ctx.typing():
            response = await asyncio.to_thread(ask_llm, query)
        
        # Use safe send to handle long responses properly
        await safe_send(ctx, response)
            
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