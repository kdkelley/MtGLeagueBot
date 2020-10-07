import leaguedata
import leagueutils

from discord.ext import commands

class JoinCog(commands.Cog):

    async def cog_check(self, ctx):
        if (not leaguedata.isUserInLeague(ctx.author.id)) and (not leagueutils.isPM(ctx.message)):
            return True
        if leaguedata.isUserInLeague(ctx.author.id):
            response = "```You are already in the league.```"
            await ctx.send(response)
            return False
        else:
            await ctx.send("```Permissions check failed.\nYou probably sent this command in a DM.```")
            return False

    @commands.command(brief="Join the league.")
    async def join(self, ctx):
        leaguedata.addPlayer(ctx.author)
        response = "Welcome to the league " + ctx.author.name + "!"
        await ctx.send(response)

def setup(bot):
    bot.add_cog(JoinCog(bot))
