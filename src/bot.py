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
        print(f"[DEBUG] Skipping already processed message {message.id}")
        return
    
    # Add message to processed set
    processed_messages.add(message.id)
    
    # Clean old messages from set (keep only last 100)
    if len(processed_messages) > 100:
        processed_messages.clear()
        processed_messages.add(message.id)
    
    # Check if the bot is mentioned
    if bot.user in message.mentions:
        print(f"[DEBUG] Bot mentioned by {message.author}: {message.content[:50]}...")
        
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

# Añadir comando pregunta en español
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