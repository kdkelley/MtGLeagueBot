import leaguedata
import leagueutils

from discord.ext import commands

class ModCog(commands.Cog):

    async def cog_check(self, ctx):
        return (leaguedata.isMod(ctx.author.id)) and (not leagueutils.isPM(ctx.message))

    @commands.command(brief="Used to mod/demod someone.", help="User is expected to be a valid discord mention.\nUse 1 to make someone a mod and 0 to make someone a normal user.")
    async def setmod(self, ctx, user, modValue):
        targetID = leagueutils.getIDFromMention(user)
        modVal = int(modValue)
        leaguedata.setMod(targetID, modVal)
        await ctx.send("Mod status updated.")

    @commands.group(brief="Used to list various information about the league.")
    async def list(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid subcommand")

    @list.command(brief="Lists entries from the games database.", help="You can use a discord mention in order to filter games by player (use '%' to search all players).\nNumber controls the number of games to show (default:10).\nGames are ordered from the most recent.")
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

    @list.command(brief="Lists packs that have been opened by players.", help="Player should either be a discord mention or '%', and filters packs based on who opened them.\nNumber controls the number of results.\nIf you set showContents to any number other than 0 it will show the contents of each pack as well.\nPacks are listed with most recently opened first.")
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

    @list.command(brief="lists players in the league.", help="Player should either be a discord mention or '%'.\nNumber controls the number of results.\nPlayers are ordered with those having joined the league most recently shown first.")
    async def players(self, ctx, player="%", number=10):
        playerData = leaguedata.getPlayers(number, player)
        response = "Players:\n id | name | isMod | time joined\n"
        for player in playerData:
            response += str(player.id) + " | " + player.name + " | " + str(player.isMod) + " | " + player.timestamp
            response += "\n"
        await ctx.send(response)

    @commands.command(brief="Swaps the winner in a game.", help="Use list games in order to find the correct id of the game you need to swap the winner and loser to, and use that for the id.")
    async def swapwinner(self, ctx, gameid):
        gameid = int(gameid)
        leaguedata.swapWinner(gameid)
        await ctx.send("Winner and loser swapped.")

    @commands.command(brief="Check help before using.", help="The format of newcontents can be seen by looking at the contents of packs with list packs.")
    async def setpackcontents(self, ctx, packid, newcontents):
        packid = int(packid)
        leaguedata.updatePackContents(packid, newcontents)
        await ctx.send("Pack contents updated.")

def setup(bot):
    bot.add_cog(ModCog(bot))
