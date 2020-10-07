import leagueutils
import leaguedata

import os
import sys

import git

from discord.ext import commands
from datetime import date

class OwnerCog(commands.Cog):

    async def cog_check(self, ctx):
        return leaguedata.isOwner(ctx.author.id)

    @commands.command(brief="Pulls bot off git.", help="This doesn't work that well.")
    async def pullbot(self, ctx):
        repo = git.Repo(".")
        repo.remotes.origin.pull()

    @commands.command(aliases=["rb", "restart", "reboot"], brief="Restarts the bot.", help="Might cause slight memory problems over time.")
    async def restartbot(self, ctx):
        print(sys.argv)
        os.execv(sys.executable, ['python'] + sys.argv)

def setup(bot):
    bot.add_cog(OwnerCog(bot))
