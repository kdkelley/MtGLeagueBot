import leaguedata
import leagueutils
import valuestore

from discord.ext import commands

class JoinCog(commands.Cog):

    async def cog_check(self, ctx):
        return (not leaguedata.isUserInLeague(ctx.author.id)) and (not leagueutils.isPM(ctx.message))

    @commands.command(brief="Join the league.")
    async def join(self, ctx):
        leaguedata.addPlayer(ctx.author)
        leaguedata.setPlayerInactive(ctx.author.id)
        leaguedata.setPlayerActive(ctx.author.id)

        if leagueutils.getWeekNumber() > 0:
            startingEnergy = (leagueutils.getWeekNumber() - 1) * valuestore.getValue("ENERGY_PER_WEEK") + valuestore.getValue("STARTING_ENERGY")
            if startingEnergy > 0:
                leaguedata.changePlayerEnergy(ctx.author.id, startingEnergy)

        response = "Welcome to the league " + ctx.author.name + "!"
        await ctx.send(response)

def setup(bot):
    bot.add_cog(JoinCog(bot))
