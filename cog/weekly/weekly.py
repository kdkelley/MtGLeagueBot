import leagueutils
import leaguedata
import valuestore

import asyncio
import os
import sys
import random

import git

from discord.ext import tasks, commands
from datetime import date

class WeeklyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.announcementCheck()

    async def announcementCheck(self):
        print("announcement check starting")
        await asyncio.sleep(1)
        print("announcement check unsleeping")
        await self.weeklyUpdateProcess()

    async def weeklyUpdateProcess(self):
        print("starting weekly update, please do not stop bot execution.")
        print("giving all players their weekly energy")
        leaguedata.changeAllPlayerEnergy(valuestore.getValue("ENERGY_PER_WEEK"))
        self.updateRivalSystem()
        await self.makeAnnouncement()
        print("ending weekly update, bot execution may now be stopped safely.")

    def updateRivalSystem(self):
        leaguedata.setAllPlayersNotPlayedWithRival()
        allPlayers = leaguedata.getAllActivePlayers()
        if len(allPlayers) <= 1:
            for player in allPlayers:
                leaguedata.setPlayerRival(player, -1)
            return

        random.shuffle(allPlayers)
        for i in range(1, len(allPlayers)):
            leaguedata.setPlayerRival(allPlayers[i-1], allPlayers[i])
        print(allPlayers)
        leaguedata.setPlayerRival(allPlayers[len(allPlayers) - 1], allPlayers[0])

    async def makeAnnouncement(self):
        if not valuestore.hasValue("CHANNEL_ID"):
            print("Cannot make announcement, no channel attuned.")
            return
        announcementMessage = ""
        if valuestore.hasValue("ROLE_ID"):
            announcementMessage += "<@&" + str(valuestore.getValue("ROLE_ID"))+ "> "
        announcementMessage += "This is a test message. "
        await self.getChannel().send(announcementMessage)

    def getChannel(self):
        return self.bot.get_channel(valuestore.getValue("CHANNEL_ID"))

def setup(bot):
    bot.add_cog(WeeklyCog(bot))