import discord
from discord.ext import commands

import os
import sys
import argparse

import configparser

import packgen
import leagueutils
import leaguedata
import valuestore

from dotenv import load_dotenv
load_dotenv()

from datetime import datetime
current_time = datetime.now().strftime("%m/%d/%Y @ %H:%M:%S")
print("Bot launched on ", current_time)

from cog.dev.dev import DevCog

COMMAND_PHRASE = "!league"

argparser = argparse.ArgumentParser(description="Discord MtG League Bot")
argparser.add_argument("--devmode", "-d", help="launches bot in dev mode", action="store_true")
argparser.add_argument("--wipe", "-w", help="wipes tables on launch", action="store_true")
args = argparser.parse_args()

DEV_MODE = args.devmode

if DEV_MODE:
    print("Running in DEV_MODE!")
    TOKEN = os.getenv('DEV_TOKEN')
else:
    TOKEN = os.getenv('NORMAL_TOKEN')

leaguedata.connect(args.wipe, True)

DESCRIPTION_TEXT = "A bot that manages a MtG league.\n\n Note: The card \'Fire\' stands for \'Fire \\\\ Ice\'."

bot = commands.Bot(command_prefix=COMMAND_PHRASE + " ", description=DESCRIPTION_TEXT)

valuestore.initialize(os.getenv("OWNER_ID"), DEV_MODE)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await bot.change_presence(activity=discord.Game(name="Magic the Gathering", type=1))

EXTENSIONS = [
"cog.mod.mod",
"cog.user.user",
"cog.join.join",
"cog.owner.owner",
"cog.weekly.weekly"
]

if DEV_MODE:
    EXTENSIONS.append("cog.dev.dev")

@commands.command(aliases=['re'])
@commands.check(lambda ctx: leaguedata.isOwner(ctx.author.id))
async def reloadExtensions(ctx):
    for extensionPath in EXTENSIONS:
        print("Reloading Extension: " + extensionPath)
        bot.reload_extension(extensionPath)
    await ctx.send("Reloaded Extensions")
    print("Reloading Extensions Done!")

bot.add_command(reloadExtensions)

for extensionPath in EXTENSIONS:
    print("Loaded Extension: " + extensionPath)
    bot.load_extension(extensionPath)

print("Loading Extensions Done!")

bot.run(TOKEN)
