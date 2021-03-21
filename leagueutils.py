import discord

import time
import datetime
import math

import leaguedata
from packgen import Pack

import valuestore

def getWeekNumber():
    delta = datetime.datetime.now() - valuestore.getValue("START_DATE")
    secondsPerWeek = 7 * 24 * 60 * 60
    return math.floor(delta.total_seconds() / secondsPerWeek) + 1

def getTimeDifferenceFormattedString(timeDifference):
    days = timeDifference.days

    timeString = ""

    if days > 0:
        timeString += str(days) + " day"
        if not days == 1:
            timeString += "s"
        timeString += " "
    
    minutes, seconds = divmod(timeDifference.seconds, 60)
    hours, minutes = divmod(minutes, 60)

    if days > 0 or hours > 0:
        timeString += str(hours) + " hour"
        if not hours == 1:
            timeString += "s"
        timeString += " "

    if days == 0:
        timeString += str(minutes) + " minute"
        if not minutes == 1:
            timeString += "s"
        timeString += " "

    return timeString.strip()


def getDaysLeftInWeek():
    todayDay = datetime.datetime.now().weekday()
    leagueDay = valuestore.getValue("START_DATE").weekday()
    rawDay = 7 - ((todayDay - leagueDay) % 7)
    return rawDay

def getCurrentSet():
    weekNumber = getWeekNumber()
    if weekNumber < leaguedata.FRF_RELEASE_WEEK:
        return Pack.KAHNS_SETCODE
    elif weekNumber < leaguedata.DTK_RELEASE_WEEK:
        return Pack.FATE_SETCODE
    else:
        return Pack.DRAGONS_SETCODE

def getIDFromMention(mention):
    if not mention[-1] == ">":
        return -1
    if not mention[0:2] == "<@":
        return -1
    if mention[2] == "#" or mention [2] == "!" or mention[2] == "&":
        return int(mention[3:-1])
    else:
        return int(mention[2:-1])

async def PMuser(user, message, file=None, filename='AttachedFile'):
    await user.create_dm()
    await sendMessage(user.dm_channel, message, file=file, filename=filename)

async def sendMessage(channel, message, file=None, filename='AttachedFile'):
    if file:
        await channel.send(message, file=discord.File(file, filename))
    else:
        await channel.send(message)

async def sendMessageByContext(ctx, message, file=None, filename='AttachedFile'):
    if file:
        await ctx.send(message, file=discord.File(file, filename))
    else:
        await ctx.send(message)

def isPM(message):
    return message.channel.type == discord.ChannelType.private
