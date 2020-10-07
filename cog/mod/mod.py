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
        await ctx.send("Mod status updated.")

    @commands.group()
    async def list(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid subcommand")

    @list.command()
    async def games(self, ctx, player="%", number=10):
        if not player == "%":
            player = leagueutils.getIDFromMention(player)
        gameData = leaguedata.getLastGames(number, player)
        if len(gameData) == 0:
            await ctx.send("No games played yet.")
            return
        response = "Games:\n ID | Winner | Loser | Timestamp\n"
        for game in gameData:
            response += str(game.id) + " | " + leaguedata.getPlayerName(game.winnerID) + " | " + leaguedata.getPlayerName(game.loserID) + " | " + game.timestamp
            response += "\n"
        await ctx.send(response)

    @list.command()
    async def packs(self, ctx, player="%", number=10, showContents=0):
        if not player == "%":
            player = leagueutils.getIDFromMention(player)
        packData = leaguedata.getLastPacks(number, player)
        response = "Packs:\n id | player | set | timestamp"
        if not showContents == 0:
            response += " | contents"
        response += "\n"
        if len(packData) == 0:
            await ctx.send("No packs opened yet.")
            return
        for pack in packData:
            response += str(pack.id) + " | " + leaguedata.getPlayerName(pack.playerid) + " | " + (pack.set) + " | " + pack.timestamp
            if not showContents == 0:
                response += " | " + pack.contents
            response += "\n"
        await ctx.send(response)

    @list.command()
    async def players(self, ctx, player="%", number=10):
        playerData = leaguedata.getPlayers(number, player)
        response = "Players:\n id | name | isMod | time joined\n"
        for player in playerData:
            response += str(player.id) + " | " + player.name + " | " + str(player.isMod) + " | " + player.timestamp
            response += "\n"
        await ctx.send(response)

    @commands.command()
    async def swapwinner(self, ctx, gameid):
        gameid = int(gameid)
        leaguedata.swapWinner(gameid)
        await ctx.send("Winner and loser swapped.")

    @commands.command()
    async def setpackcontents(self, ctx, packid, newcontents):
        packid = int(packid)
        leaguedata.updatePackContents(packid, newcontents)
        await ctx.send("Pack contents updated.")

def setup(bot):
    bot.add_cog(ModCog(bot))
