import leaguedata
import leagueutils

from discord.ext import commands

class JoinCog(commands.Cog):

    async def cog_check(self, ctx):
        return (not leaguedata.isUserInLeague(ctx.author.id)) and (not leagueutils.isPM(ctx.message))

    @commands.command()
    async def join(self, ctx):
        if leaguedata.isUserInLeague(ctx.author.id):
            response = "You are already in the league.\n"
            await ctx.send(response)
            return
        leaguedata.addPlayer(ctx.author)
        response = "Welcome to the league " + ctx.author.name + "!"
        await ctx.send(response)

def setup(bot):
    bot.add_cog(JoinCog(bot))
