import discord

import time
from datetime import date
import math

import leaguedata
from packgen import Pack

def getWeekNumber():
    delta = date.today() - leaguedata.START_DATE
    return (math.floor(delta.days / 7) + 1)

def getCurrentSet():
    weekNumber = getWeekNumber()
    if weekNumber < leaguedata.FRF_RELEASE_WEEK:
        return Pack.KAHNS_SETCODE
    elif weekNumber < leaguedata.DTK_RELEASE_WEEK:
        return Pack.FATE_SETCODE
    else:
        return Pack.DRAGONS_SETCODE

def getIDFromMention(mention):
    if len(mention) < 4:
        return None
    

async def PMuser(user, message, file=None, filename='AttachedFile'):
    await user.create_dm()
    await sendMessage(user.dm_channel, message, file=file, filename=filename)

async def sendMessage(channel, message, file=None, filename='AttachedFile'):
    if file:
        await channel.send(message, file=discord.File(file, filename))
    else:
        await channel.send(message)

def isPM(message):
    return message.channel.type == discord.ChannelType.private
