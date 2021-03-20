import leaguedata
import leagueutils
import valuestore
import rivalsystem

from discord.ext import commands
from discord.ext.commands import CommandError

class ModCog(commands.Cog):

    async def cog_check(self, ctx):
        return (leaguedata.isMod(ctx.author.id)) and (not leagueutils.isPM(ctx.message))

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
        if not player == "%":
            player = str(leagueutils.getIDFromMention(player))
        print("LOGGING player = " + player)
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

    @commands.command(brief="Gives or removes energy from a player.", help="Takes a player reference and a value which modifies the player's energy.")
    async def changeplayerenergy(self, ctx, playerid, deltaEnergy):
        playerid = leagueutils.getIDFromMention(playerid)
        deltaEnergy = int(deltaEnergy)
        leaguedata.changePlayerEnergy(playerid, deltaEnergy)
        await ctx.send("Player energy changed.")

    @commands.group(brief="Delete a game or pack.")
    async def delete(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid subcommand")

    @delete.command(brief="Delete a game by id.", help="You should find a valid gameID using list games first before using this command.\n **THERE IS NO UNDO.**")
    async def game(self, ctx, gameID):
        leaguedata.deleteGame(gameID)
        await ctx.send("Game deleted.")

    @delete.command(brief="Delete a pack by id.", help="You should find a valid packID using list packs before using this command.\n **THERE IS NO UNDO.**")
    async def pack(self, ctx, packID):
        leaguedata.deletePack(packID)
        await ctx.send("Pack deleted.")

    @commands.command(brief="Directs all non-reply messages of the bot to this channel.", help="Takes no arguments, make sure you are in the intended channel when you use this command.")
    async def attunechannel(self, ctx):
        valuestore.setValue("CHANNEL_ID", ctx.channel.id)
        await ctx.send("Announcement channel changed.")

    @commands.command(brief="This is the role that will be mentioned by the bot in the weekly report.", help="Takes a mention of the role you would like the bot to then go on to mention.")
    async def attuneRole(self, ctx, role):
        valuestore.setValue("ROLE_ID", leagueutils.getIDFromMention(role))
        await ctx.send("Announcement role changed.")

    @commands.command(brief="Sets the first player's rival to be the second player.", help="First argument is a mention of the player whose rival you want to set, the second argument is a mention of the player who will be set as their rival.")
    async def forceSetRival(self, ctx, targetPlayer, targetRival):
        leaguedata.setPlayerRival(targetPlayer, targetRival)
        await ctx.send("Rival updated.")

    @commands.command(brief="Regenerates all rival selections.", help="Takes no arguments. Regenerates all rival selections such that everyone has one rival and one person rivaling them.")
    async def forceRegenerateRivals(self, ctx):
        rivalsystem.regenerateAllRivals()
        await ctx.send("All rivals updated.")

def setup(bot):
    bot.add_cog(ModCog(bot))
