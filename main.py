import importlib
import time
import nextcord 
from nextcord.ext import commands
from dotenv import load_dotenv
import os
from termcolor import cprint
import time

load_dotenv()

# Access the TOKEN variable
token = os.getenv('TOKEN')


bot = commands.Bot(command_prefix='q', intents=nextcord.Intents.all(), activity=nextcord.Activity(type=nextcord.ActivityType.watching, name="your discord server!"))

@bot.event
async def on_ready():

  # Print out server count in a cool style
  guild_count = len(bot.guilds)
  print(f"> Connected to {guild_count} servers!")

  

  # Send a neat embed to log channel
  embed = nextcord.Embed(title="Bot is ready!", color=0x00ff00)
  embed.set_thumbnail(url=bot.user.avatar.url)
  embed.add_field(name="Servers", value=guild_count, inline=True)
  embed.add_field(name="Latency", value=f"{bot.latency*1000:.2f} ms", inline=True)
  
  log_channel = bot.get_channel(1116541851516817469)
  await log_channel.send(embed=embed)

  
  
  print(f"> {bot.user.name} is ready to go!")
    


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

