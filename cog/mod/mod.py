import leaguedata
import leagueutils

from discord.ext import commands

class ModCog(commands.Cog):

    async def cog_check(self, ctx):
        return (leaguedata.isMod(ctx.author.id)) and (not leagueutils.isPM(ctx.message))

    @commands.command()
    async def setmod(self, ctx, user, modValue):
        targetID = leagueutils.getIDFromMention(user)
        modVal = int(modValue)
        leaguedata.setMod(targetID, modVal)
        await ctx.send("Mod status updated.");

def setup(bot):
    bot.add_cog(ModCog(bot))
