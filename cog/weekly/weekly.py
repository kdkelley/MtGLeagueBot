import leagueutils
import leaguedata
import valuestore
import rivalsystem

import asyncio
import os
import sys
import random

import git

from discord.ext import tasks, commands
import datetime
from datetime import timedelta

class WeeklyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.handleWeeklyUpdates()

    async def sleepUntil(self, targetDate):
        print("sleeping until " + targetDate.strftime("%m/%d/%Y @ %H:%M:%S"))
        delta = targetDate - datetime.datetime.now()
        secondsToWait = delta.total_seconds() + 1
        await asyncio.sleep(secondsToWait)

    async def initialLeagueSetup(self):
        print("handling initial league setup")
        await self.makeAnnouncement("Welcome to the league, which has now officially started!")
        leaguedata.changeAllPlayerEnergy(valuestore.getValue("STARTING_ENERGY"))

    async def handleWeekAdvancement(self, weekNumber):
        print("doing week advancement for week " + str(weekNumber))
        if weekNumber == 1:
            await self.initialLeagueSetup()
        else:
            announcementText = "Welcome to week " + str(weekNumber) + "!\n"
            announcementText += "You've been randomly assigned a rival for the week. Play them to get bonus energy.\n"
            announcementText += "All players have also been given additional energy and packs for the week.\n"

            announcementText += "Current Leaderboard Standings:\n"

            leaderboardData = leaguedata.getLeaderboard()
            for datum in leaderboardData:
                announcementText += (str(datum[1]).center(5) + " - " + str(datum[2]).center(5)) + " | " + str(datum[0]) + "\n"

            await self.makeAnnouncement(announcementText)
            leaguedata.changeAllPlayerEnergy(valuestore.getValue("ENERGY_PER_WEEK"))

        rivalsystem.regenerateAllRivals()
        valuestore.setValue("LAST_WEEK_UPDATED", weekNumber)

    async def handleFinalAnnouncement(self):
        print("ending the league")
        await self.makeAnnouncement("The league is ending!")

    async def handleWeeklyUpdates(self):

        currentWeek = max(leagueutils.getWeekNumber(), 0)
        lastUpdatedWeek = valuestore.getValue("LAST_WEEK_UPDATED")

        while currentWeek < (valuestore.getValue("LEAGUE_WEEKS_DURATION") + 1):
            targetSleepDate = None
            if currentWeek < 1:
                targetSleepDate = valuestore.getValue("START_DATE")
            else:
                if currentWeek > lastUpdatedWeek:
                    while valuestore.getValue("LAST_WEEK_UPDATED") < currentWeek:
                        await self.handleWeekAdvancement(valuestore.getValue("LAST_WEEK_UPDATED") + 1)
                targetSleepDate = valuestore.getValue("START_DATE") + timedelta(days=(7 * currentWeek))
            await self.sleepUntil(targetSleepDate)
            currentWeek = max(leagueutils.getWeekNumber(), 0)
            lastUpdatedWeek = valuestore.getValue("LAST_WEEK_UPDATED")
            print("awoke, current week:" + str(currentWeek) + " and last updated week:" + str(lastUpdatedWeek))
        
        leagueFinishedNumber = valuestore.getValue("LEAGUE_WEEKS_DURATION") + 1

        if lastUpdatedWeek < leagueFinishedNumber:
            self.handleFinalAnnouncement()
            valuestore.setValue("LAST_WEEK_UPDATED", leagueFinishedNumber)

    async def makeAnnouncement(self, message):
        if not valuestore.hasValue("CHANNEL_ID"):
            print("Cannot make announcement, no channel attuned.")
            return
        announcementMessage = ""
        if valuestore.hasValue("ROLE_ID"):
            announcementMessage += "<@&" + str(valuestore.getValue("ROLE_ID"))+ "> "
        announcementMessage += message
        await self.getChannel().send(announcementMessage)

    def getChannel(self):
        return self.bot.get_channel(valuestore.getValue("CHANNEL_ID"))

def setup(bot):
    bot.add_cog(WeeklyCog(bot))