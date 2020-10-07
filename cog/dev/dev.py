import leagueutils
import leaguedata

from discord.ext import commands
from datetime import date

class DevCog(commands.Cog):

    async def cog_check(self, ctx):
        if not (leaguedata.isMod(ctx.author.id)) and (not leagueutils.isPM(ctx.message)):
            await ctx.send("```Permissions check failed.\nYou likely either aren't a moderator or you sent this command in a DM.```")
            return False
        return True

    @commands.command()
    async def changestartdate(self, ctx, yearStr, monthStr, dayStr):
        year = int(yearStr)
        month = int(monthStr)
        day = int(dayStr)
        leaguedata.START_DATE = date(year, month, day)
        await ctx.send("Updated start date to {0}/{1}/{2}".format(month, day, year))

    @commands.command()
    async def wipedb(self, ctx):
        leaguedata.kill()
        leaguedata.connect(True, True)
        await ctx.send('Tables wiped'.format(ctx.author))

def setup(bot):
    bot.add_cog(DevCog(bot))
