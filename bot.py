import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
load_dotenv()
intents = discord.Intents.default()
intents.message_content = True  
intents.members = True  
bot = commands.Bot(command_prefix='!', intents=intents)

async def load_commands():
    for filename in os.listdir('./commands'):
        if filename.endswith('.py'):
            module = __import__(f'commands.{filename[:-3]}', fromlist=['setup'])
            await module.setup(bot)

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Game('github/Apathyy322'))
    print(f'Bot is online as: {bot.user.name}!')
    await load_commands()
token = os.getenv('token')
bot.run(token)
