import discord

import os
import sys

import argparse

import configparser

import packgen
import leagueutils
import leaguedata
import commandhandlers

from dotenv import load_dotenv

COMMAND_PHRASE = "!league"

argparser = argparse.ArgumentParser(description="Discord MtG League Bot")
argparser.add_argument("--devmode", help="launches bot in dev mode", action="store_true")
args = argparser.parse_args()

load_dotenv()

if args.devmode:
    TOKEN = os.getenv('DEV_TOKEN')
else:
    TOKEN = os.getenv('NORMAL_TOKEN')

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await client.change_presence(activity=discord.Game(name="Magic the Gathering", type=1))

@client.event
async def on_message(message):

    # filter out messages I have said
    if message.author == client.user:
        return

    # filter out messages that don't have the command phrase
    if not message.content.startswith(COMMAND_PHRASE):
        return

    if leagueutils.getWeekNumber() >= leaguedata.END_WEEK:
        await leagueutils.sendMessage(message.channel, "The league is now over. Thanks for playing!")
        return

    print(message.author, "(", message.author.id , ")", " -- ", message.content)

    command = message.content[len(COMMAND_PHRASE):].strip().lower().split()[0]

    if command == "kill" and leaguedata.isMod(message.author.id):
        leaguedata.kill()
        sys.exit()
    elif command == "help":
        print()
        await commandhandlers.handleHelp(message)
    elif command == "join":
        # "doable in any channel by anyone"
        await commandhandlers.handleJoin(message)
    elif command == "report":
        # "doable in public channel only"
        # format:
        # !league report @otheruser [I/They] won
        # checks if game is within date/time restrictions
        # tells the winner their win count
        # tells the loser their lose count
        # says if the loser gets to open another pack
        await commandhandlers.handleReport(message)
    elif command == "openpack":
        # "doable in public channel only"
        # checks if the user is allowed to open a pack
        # generates a pack
        # sends pack to the public channel
        # adds pack contents to that user's cardpool
        await commandhandlers.handleOpenPack(message)
    elif command == "cardpool":
        # "doable in private channel only, except by mods"
        # format:
        # !league cardpool [target]
        # target is optional, if no target provided, assumed user who is talking
        # displays the target's entire cardpool they have gotten from packs
        await commandhandlers.handleCardpool(message)
    elif command == "leaderboard":
        # "doable in private channel only, except by mods"
        # format:
        # !league leaderboard [days]
        # days is optional and is the number of days to look back
        # if days not provided, counts all wins
        # leaderboard is just sorted by number of wins, uses losses as tiebreaker, UID double tiebreaker
        await commandhandlers.handleLeaderboard(message)
    elif command == "setmod":
        # "doable in any channel by owner only"
        # format:
        # !league set-owner @user [value]
        # value is 0 or 1
        # tells user about the changes (explains differences for mods)
        await commandhandlers.handleSetMod(message)
    elif command == "status":
        await commandhandlers.handleStatus(message)
    elif command == "debug-changestartdate":
        await commandhandlers.handleDebugChangeStartDate(message)
    elif command == "debug-discon-db" and message.author.id == leaguedata.OWNER_ID:
        leaguedata.kill()
    elif command == "debug-recon-db" and message.author.id == leaguedata.OWNER_ID:
        leaguedata.connect()
    else:
        print("Command unrecognized.")
        await leagueutils.sendMessage(message.channel, "Command not recognized.")

client.run(TOKEN)
