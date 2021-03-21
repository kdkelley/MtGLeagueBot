import leagueutils
import leaguedata
import valuestore

import os
import sys

import git

from discord.ext import commands
from datetime import date

class OwnerCog(commands.Cog):

    async def cog_check(self, ctx):
        return leaguedata.isOwner(ctx.author.id)

    @commands.command(brief="Pulls bot off git.", help="This doesn't also work super well.")
    async def pullbot(self, ctx):
        repo = git.Repo(".")
        repo.remotes.origin.pull()

    @commands.command(aliases=["rb", "restart", "reboot"], brief="Restarts the bot.", help="Might cause slight memory problems over time.")
    async def restartbot(self, ctx, *newargs):

        args = ['python'] + sys.argv
        if not len(newargs)==0:
            args = ['python', sys.argv[0]]
            args.extend(newargs)

        print(args)
        os.execv(sys.executable, args)

    @commands.command(brief="Used to mod/demod someone.", help="User is expected to be a valid discord mention.\nUse 1 to make someone a mod and 0 to make someone a normal user.")
    async def setmod(self, ctx, user, modValue):
        targetID = leagueutils.getIDFromMention(user)
        modVal = int(modValue)
        leaguedata.setMod(targetID, modVal)
        await ctx.send("Mod status updated.")

    @commands.command(brief="Used to directly change values.", help="key and value can be anything.")
    async def setstorestring(self, ctx, key, value):
        valuestore.setValue(key, str(value))
        await ctx.send("value updated.")

    @commands.command(brief="Used to directly change values.", help="key and value can be anything.")
    async def setstoreint(self, ctx, key, value):
        valuestore.setValue(key, int(value))
        await ctx.send("value updated.")

def setup(bot):
    bot.add_cog(OwnerCog(bot))
