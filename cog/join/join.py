import leaguedata
import leagueutils

from discord.ext import commands

class JoinCog(commands.Cog):

    async def cog_check(self, ctx):
        return (not leaguedata.isUserInLeague(ctx.author.id)) and (not leagueutils.isPM(ctx.message))

    @commands.command(brief="Join the league.")
    async def join(self, ctx):
        leaguedata.addPlayer(ctx.author)
        response = "Welcome to the league " + ctx.author.name + "!"
        await ctx.send(response)

def setup(bot):
    bot.add_cog(JoinCog(bot))
