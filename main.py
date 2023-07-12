import importlib
import time
import nextcord 
from nextcord.ext import commands
from dotenv import load_dotenv
import os
import psutil
from termcolor import cprint
import time

load_dotenv()

# Access the TOKEN variable
token = os.getenv('TOKEN')


bot = commands.Bot(command_prefix='q', intents=nextcord.Intents.all(), activity=nextcord.Activity(type=nextcord.ActivityType.watching, name="your discord server!"))

@bot.event
async def on_ready():

  print('---------------------------------------')
  
  # Log details on bot user
  bot_user = bot.user
  print(f'Logged in as: {bot_user.name} (ID: {bot_user.id})')

  # Log guild count  
  guild_count = len(bot.guilds)
  print(f'Connected to {guild_count} guilds')

  # Log member count
  member_count = 0
  for guild in bot.guilds:
    member_count += guild.member_count
  print(f'Serving {member_count} members total')

  # Log channels 
  channel_count = 0
  for guild in bot.guilds:
    channel_count += len(guild.channels)
  print(f'Access to {channel_count} channels')

  # Log other detailed analytics
  voice_clients = len(bot.voice_clients)
  print(f'{voice_clients} active voice clients')
  
  uptime = (bot.uptime).strftime("%H:%M:%S")
  print(f'Uptime: {uptime}')

  cpu_usage = psutil.cpu_percent()
  print(f'CPU Usage: {cpu_usage}%')

  memory_usage = psutil.virtual_memory().percent
  print(f'Memory Usage: {memory_usage}%')

  disk_usage = psutil.disk_usage('/').percent
  print(f'Disk Usage: {disk_usage}%')

  print('---------------------------------------')
    


"""
   #* This is the main file of the bot. It loads all the cogs in the commands/cogs directory.
"""
cogs_dir = "commands/cogs"

loaded_cogs = []
loaded_folders = []

for root, dirs, files in os.walk(cogs_dir):
    if root in loaded_folders:
        continue
    for filename in files:
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"{root.replace('/', '.').replace(os.sep, '.')}.{filename[:-3]}"
            bot.load_extension(module_name)
    if "__init__.py" in files:
        loaded_folders.append(root)


   

bot.run(token)

