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
    
    # Clean old messages from set (keep only last 1000, remove oldest 500 when limit reached)
    if len(processed_messages) > 1000:
        # Convert to list, sort by message ID (newer IDs are larger), keep newest 500
        sorted_messages = sorted(processed_messages)
        processed_messages.clear()
        processed_messages.update(sorted_messages[-500:])
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
        
        # Check if the content starts with a command prefix - if so, let command handler process it
        if content.startswith('!'):
            print(f"[DEBUG] Mention contains command, delegating to command processor")
            await bot.process_commands(message)
            return
        
        if content:  # If there's a question after the mention
            try:
                print(f"[DEBUG] Processing mention query: {content[:50]}...")
                async with message.channel.typing():
                    response = await asyncio.to_thread(ask_llm, content)
                
                # Handle long responses (Discord 2000 char limit)
                if len(response) > 2000:
                    chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
                    for chunk in chunks:
                        await message.reply(chunk)
                        print(f"[DEBUG] Sent chunk of length {len(chunk)}")
                else:
                    await message.reply(response)
                    print(f"[DEBUG] Sent response of length {len(response)}")
                    
            except Exception as e:
                print(f"[ERROR] Exception in mention handler: {str(e)}")
                await message.reply(f"Error: {str(e)}")
        else:
            await message.reply("¡Hola! Soy MentorIA. Puedes preguntarme sobre inversiones inmobiliarias usando:\n• `!ask <tu pregunta>`\n• `!pregunta <tu pregunta>`\n• O simplemente mencionarme: `@MentorIA <tu pregunta>`")
        
        # Don't process commands if bot was mentioned (and it wasn't a command)
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
    print(f"[DEBUG] !ask command called by {ctx.author}: {query[:50]}...")
    try:
        async with ctx.typing():
            response = await asyncio.to_thread(ask_llm, query)
        
        # Handle long responses (Discord 2000 char limit)
        if len(response) > 2000:
            chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
            for chunk in chunks:
                await ctx.send(chunk)
                print(f"[DEBUG] !ask sent chunk of length {len(chunk)}")
        else:
            await ctx.send(response)
            print(f"[DEBUG] !ask sent response of length {len(response)}")
            
    except Exception as e:
        print(f"[ERROR] Exception in !ask command: {str(e)}")
        await ctx.send(f"Error: {str(e)}")

# Añadir comando pregunta en español
@bot.command()
async def pregunta(ctx, *, query: str):
    """Pregunta sobre inversiones inmobiliarias en español"""
    print(f"[DEBUG] !pregunta command called by {ctx.author}: {query[:50]}...")
    try:
        async with ctx.typing():
            response = await asyncio.to_thread(ask_llm, query)
        
        # Handle long responses (Discord 2000 char limit)
        if len(response) > 2000:
            chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
            for chunk in chunks:
                await ctx.send(chunk)
                print(f"[DEBUG] !pregunta sent chunk of length {len(chunk)}")
        else:
            await ctx.send(response)
            print(f"[DEBUG] !pregunta sent response of length {len(response)}")
            
    except Exception as e:
        print(f"[ERROR] Exception in !pregunta command: {str(e)}")
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