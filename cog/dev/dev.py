import leagueutils
import leaguedata

from discord.ext import commands

class DevCog(commands.Cog):

    async def cog_check(self, ctx):
        return (not leagueutils.isPM(ctx.message))

    @commands.command()
    async def changestartdate(self, ctx):
        print("Test command")
        await ctx.send('Hello {0.display_name}.'.format(ctx.author))

    @commands.command()
    async def toggledb(self, ctx):
        print("Test command")
        await ctx.send('Hello {0.display_name}.'.format(ctx.author))

    @commands.command()
    async def test(self, ctx):
        print("Test command")
        await ctx.send('Hello {0.display_name}.'.format(ctx.author))

    @commands.command()
    async def wipedb(self, ctx):
        leaguedata.kill()
        leaguedata.connect(True, True)
        await ctx.send('Tables wiped'.format(ctx.author))

def setup(bot):
    bot.add_cog(DevCog(bot))
