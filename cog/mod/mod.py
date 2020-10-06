import leaguedata
import leagueutils

from discord.ext import commands

class ModCog(commands.Cog):

    async def cog_check(self, ctx):
        return (leaguedata.isMod(ctx.author.id)) and (not leagueutils.isPM(ctx.message))

    @commands.command()
    async def kill(self, ctx):
        leaguedata.kill()
        print(ctx.author.id, "killed the database.")
        await ctx.send('Database has been killed.'.format(ctx.author))

    @commands.command()
    async def setmod(self, ctx):
        print(ctx.author.id, "")
        await ctx.send('Hello {0.display_name}.'.format(ctx.author))

def setup(bot):
    bot.add_cog(ModCog(bot))
