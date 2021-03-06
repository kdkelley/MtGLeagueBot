from discord.ext import commands
from datetime import datetime
import io

import leaguedata
import leagueutils
from packgen import Pack

class UserCog(commands.Cog):

    async def cog_check(self, ctx):
        return leaguedata.isUserInLeague(ctx.author.id) and (not leagueutils.isPM(ctx.message))

    @commands.command(brief="Shows you your cardpool or the cardpool of another user.", help="user, if included, must be a valid mention on Discord.\n If user is not included, will retrieve the cardpool of the user that sent the message")
    async def cardpool(self, ctx, user=None):

        target = None
        if user is None:
            target = ctx.author.id
        else:
            target = leagueutils.getIDFromMention(user)

        if not leaguedata.isUserInLeague(target):
            response = "The target is not a player in the league.\n"
            await ctx.send(response)
            return

        cardpool = leaguedata.getCardpool(target)

        if len(cardpool) == 0:
            response = "Player has no cards in their cardpool.\n"
            await ctx.send(response)
            return

        response = "Cardpool is attached.\n"

        cardpool_stream = io.BytesIO("\n".join(cardpool).encode())
        filename = leaguedata.getPlayerName(target) + "_" + datetime.now().strftime("%m_%d_%Y_%H_%M_%S") + "_Cardpool.txt"
        await leagueutils.sendMessageByContext(ctx, response, file=cardpool_stream, filename=filename)

    @commands.command(brief="Shows you the current leaderboard.", help="Shows you the current leaderboard.")
    async def leaderboard(self, ctx):
        leaderboardData = leaguedata.getLeaderboard()
        response = "Leaderboard: \n"
        for datum in leaderboardData:
            response += (str(datum[1]).center(5) + " - " + str(datum[2]).center(5)) + " | " + str(datum[0]) + "\n"
        response += "\n Users without any wins are not shown in the leaderboard.\n"
        await ctx.send(response)

    @commands.command(aliases=['op', "pack", "open"], brief="Opens a pack, should you have one to open.", help="Opens a pack. Begins with the first set out and then opens subsequent packs. Packs earned from losses will be opened last and will always be of the current set.")
    async def openpack(self, ctx):
        if leagueutils.isPM(ctx.message):
            response = "Please open packs in public, where we can all share the excitement!\n"
            await ctx.send(response)
            return

        KTKpacks, FRFpacks, DTKpacks, losspacks = leaguedata.getPlayerMaxPacks(ctx.author.id)
        KTKopened, FRFopened, DTKopened, lossopened = leaguedata.getPlayerOpenedPacks(ctx.author.id)

        packSet = None
        isLossPack = False

        if KTKopened < KTKpacks:
            packSet = Pack.KAHNS_SETCODE
        elif FRFopened < FRFpacks:
            packSet = Pack.FATE_SETCODE
        elif DTKopened < DTKpacks:
            packSet = Pack.DRAGONS_SETCODE
        elif lossopened < losspacks:
            packSet = leagueutils.getCurrentSet()
            isLossPack = True
        else:
            response = "You have no packs to open.\n"
            await ctx.send(response)
            return

        p = Pack()
        p.generate(packSet)

        response = ctx.author.name + " opened a pack of " + packSet + "!" + "\n\n"

        KTKpacks, FRFpacks, DTKpacks, losspacks = leaguedata.getPlayerMaxPacks(ctx.author.id)
        KTKopened, FRFopened, DTKopened, lossopened = leaguedata.getPlayerOpenedPacks(ctx.author.id)

        KTKToOpen = KTKpacks - KTKopened
        FRFToOpen = FRFpacks - FRFopened
        DTKToOpen = DTKpacks - DTKopened

        toOpen = KTKToOpen + FRFToOpen + DTKToOpen

        response += "Its contents:\n\n"

        commonsData = p.cardData[0:p.commons]
        uncommonsData = p.cardData[p.commons:p.commons + p.uncommons]
        rareData = p.cardData[p.commons + p.uncommons: p.commons + p.uncommons + p.rares]
        mythicData = p.cardData[p.commons + p.uncommons + p.rares:]

        leaguedata.playerOpenedPack(ctx.author.id, p, isLossPack)

        commonsBody = "Commons:\n" + "\n".join(commonsData) + "\n\n"
        response += commonsBody

        uncommonsBody = "*Uncommons:*\n" + "\n".join(uncommonsData) + "\n\n"
        response += uncommonsBody

    #https://gatherer.wizards.com/Handlers/Image.ashx?multiverseid=368970&type=card

        def getMIDLink(cardName, surrounder):
            mId = leaguedata.getMultiverseId(cardName, packSet)
            return (surrounder + cardName + surrounder + " - " + "https://gatherer.wizards.com/Handlers/Image.ashx?multiverseid=" + str(mId) + "&type=card" + "\n")

        if p.rares > 0:
            rareBody = "__Rares:__\n"
            for rare in rareData:
                rareBody += getMIDLink(rare, "")
            rareBody += "\n\n"
            response += rareBody

        if p.mythics > 0:
            mythicBody = "__**Mythics!**__\n"
            for mythic in mythicData:
                mythicBody += getMIDLink(mythic, "**")
            mythicBody += "\n\n"
            response += mythicBody

        if toOpen == 1:
            response += "You have no more packs left to open. \n\n"
        else:
            response += "You have " + str(toOpen - 1) + " packs left. \n\n"

        await ctx.send(response)

    @commands.command(brief="Used to report games.", help="The 'opponent' argument is expected to be a discord mention.\nWinner should be either 'I' or 'me' if the person writing the message won, or 'they' or 'them' if the other player won.")
    async def report(self, ctx, opponent, winner):
        # gotta check two different restrictions
        # gotta check last game between these players, see if it was less than 18 hours ago
        # gotta check total number of games between these players this week, see if it is less than 3
        # if either criteria not met, gotta reject the game
        # gotta inform winner of their new win total:
        # weekly and global
        # gotta infrom loser of their new lose total (and if they can open a new pack)
        # for now intentionally not checking if the target is in the league or not, for debug

        if not leaguedata.isUserInLeague(ctx.author.id):
            response = "You are not in the league.\nThe game was not recorded.\n"
            await ctx.send(response)
            return
        if not leaguedata.isUserInLeague(leagueutils.getIDFromMention(opponent)):
            response = "Your opponent is not in the league.\nThe game was not recorded.\n"
            await ctx.send(response)
            return

        winner = winner.lower()
        winnerID = None
        loserID = None
        if winner == "i" or winner == "me":
            winnerID = ctx.author.id
            loserID = leagueutils.getIDFromMention(opponent)
        elif winner == "they" or winner == "them":
            winnerID = leagueutils.getIDFromMention(opponent)
            loserID = ctx.author.id
        else:
            response = "Winner could not be identified.\nPlease use I/Me/Them/They to denote the winner.\nThe game was not recorded.\n"
            await ctx.send(response)
            return

        gamesToday = leaguedata.getGamesToday(winnerID, loserID)
        gamesThisWeek = leaguedata.getGamesThisWeek(winnerID, loserID)

        if len(gamesToday) >= leaguedata.MAX_IDENTICAL_GAMES_PER_DAY:
            response = "Players have already played " + str(len(gamesToday)) + " time(s) today. (Limit: " + str(leaguedata.MAX_IDENTICAL_GAMES_PER_DAY) + ")\nThe game was not recorded.\n"
            await ctx.send(response)
            return

        if len(gamesThisWeek) >= leaguedata.MAX_IDENTICAL_GAMES_PER_WEEK:
            response = "Players have already played " + str(len(gamesThisWeek)) + " time(s) this week. (Limit: " + str(leaguedata.MAX_IDENTICAL_GAMES_PER_WEEK) + ")\nThe game was not recorded.\n"
            await ctx.send(response)
            return

        leaguedata.addGame(winnerID, loserID)
        response = "Game successfully recorded.\n"

        newWins = leaguedata.getPlayerWins(winnerID)
        newLosses = leaguedata.getPlayerLosses(loserID)

        response += leaguedata.getPlayerName(winnerID) + " now has " + str(newWins) + " wins.\n"
        response += leaguedata.getPlayerName(loserID) + " now has " + str(newLosses) + " losses.\n"

        if newLosses % leaguedata.LOSSES_PER_PACK == 0:
            response += "They may open another pack using \"!league openpack\".\n"

        await ctx.send(response)

    @commands.command(brief="Used to change your name on the leaderboard.", help="Used to change your internal name which is used on the leaderboard.")
    async def setname(self, ctx, name):
        leaguedata.setPlayerName(ctx.author.id, name)
        await ctx.send("Name updated.")

    @commands.command(brief="Get your personal wins/losses/packs.", help="Gets a variety of information about the league and your current wins/losses/packs, .etc.")
    async def status(self, ctx):
        response = "Status:\n```"

        if not leaguedata.isUserInLeague(ctx.author.id):
            response += "You are NOT in the league\n"
            response += "You can join the league with the command:\n"
            response += "\"!league join\" without the quotes\n"
            return response

        wins = leaguedata.getPlayerWins(ctx.author.id)
        losses = leaguedata.getPlayerLosses(ctx.author.id)

        response += "You have " + str(wins) + " wins and " + str(losses) + " losses.\n\n"

        response += "It is currently week " + str(leagueutils.getWeekNumber()) + " (" + str(leagueutils.getDaysLeftInWeek()) + " day(s) left)\n"
        response += "The current set is " + leagueutils.getCurrentSet() + "\n"

        if leagueutils.getWeekNumber() >= leaguedata.DECK_SIZE_40_WEEK:
            response += "Decks should be 40 cards.\n\n"
        else:
            response += "Decks should be 30 cards, but will need to be 40 cards starting on week 4.\n\n"

        KTKpacks, FRFpacks, DTKpacks, losspacks = leaguedata.getPlayerMaxPacks(ctx.author.id)
        KTKopened, FRFopened, DTKopened, lossopened = leaguedata.getPlayerOpenedPacks(ctx.author.id)

        KTKToOpen = KTKpacks - KTKopened
        FRFToOpen = FRFpacks - FRFopened
        DTKToOpen = DTKpacks - DTKopened

        currentSet = leagueutils.getCurrentSet()

        lossToOpen = losspacks - lossopened

        if currentSet == Pack.KAHNS_SETCODE:
            KTKToOpen += lossToOpen
        elif currentSet == Pack.FATE_SETCODE:
            FRFToOpen += lossToOpen
        elif currentSet == Pack.DRAGONS_SETCODE:
            DTKToOpen += lossToOpen

        if KTKToOpen > 0:
            response += "You have " + str(KTKToOpen) + " Iconic Masters packs to open!\n"

        if FRFToOpen > 0:
            response += "You have " + str(FRFToOpen) + " Masters 25 packs to open!\n"

        if DTKToOpen > 0:
            response += "You have " + str(DTKToOpen) + " Ultimate Masters packs to open!\n"

        if KTKToOpen + FRFToOpen + DTKToOpen == 0:
            response += "There are no packs you need to open at this time.\n"
        else:
            response += "You can open them using \"!league openpack\".\n The set opened will be chosen in order.\n Packs from losses will automatically move to the latest set when it releases.\n"

        response += "```"

        await ctx.send(response)

def setup(bot):
    bot.add_cog(UserCog(bot))
