import leagueutils
import leaguedata

from discord.ext import commands
from datetime import date

class DevCog(commands.Cog):

    async def cog_check(self, ctx):
        return (leaguedata.isMod(ctx.author.id)) and (not leagueutils.isPM(ctx.message))

    @commands.command()
    async def wipedb(self, ctx):
        leaguedata.kill()
        leaguedata.connect(True, True)
        await ctx.send('Tables wiped'.format(ctx.author))

def setup(bot):
    bot.add_cog(DevCog(bot))
