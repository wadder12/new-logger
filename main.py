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


bot = commands.Bot(command_prefix='q', intents=nextcord.Intents.all(), activity=nextcord.Activity(type=nextcord.ActivityType.watching, name="the systems | QuantaAI"))

@bot.event
async def on_ready():
    print('---------------------------------------')
    print('          🚀 Bot is now online! 🚀       ')
    print('---------------------------------------')
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('---------------------------------------')

    animation_frames = [
        "█▒▒▒▒▒▒▒▒▒",
        "██▒▒▒▒▒▒▒▒",
        "███▒▒▒▒▒▒▒",
        "████▒▒▒▒▒▒",
        "█████▒▒▒▒▒",
        "██████▒▒▒▒",
        "███████▒▒▒",
        "████████▒▒",
        "█████████▒",
        "██████████",
    ]

    for frame in animation_frames:
        cprint(f"\rHacking in progress... {frame}", "green", attrs=["bold"], end="")
        time.sleep(0.5)

    print("\n---------------------------------------")


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

