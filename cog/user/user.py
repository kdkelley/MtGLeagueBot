from discord.ext import commands
import datetime
from datetime import timedelta
import io

import leaguedata
import leagueutils
from packgen import Pack

import valuestore

class UserCog(commands.Cog):

    async def cog_check(self, ctx):
        # return leaguedata.isUserInLeague(ctx.author.id) and (not leagueutils.isPM(ctx.message)) and (not leagueutils.getWeekNumber() < 1)
        return leaguedata.isUserInLeague(ctx.author.id) and (not leagueutils.isPM(ctx.message))

    @commands.command(brief="Sets yourself as inactive for the purposes of the rival system.", help="No arguments needed. Please do not abuse or overuse this command as it does affect rival assignment.")
    async def setinactive(self, ctx, user=None):
        if leaguedata.getIsPlayerActive(ctx.author.id):
            leaguedata.setPlayerInactive(ctx.author.id)
            await ctx.send("You have been marked inactive.")
        else:
            await ctx.send("You are already inactive.")

    @commands.command(brief="Sets yourself as active for the purposes of the rival system.", help="No arguments needed..")
    async def setactive(self, ctx, user=None):
        if not leaguedata.getIsPlayerActive(ctx.author.id):
            leaguedata.setPlayerActive(ctx.author.id)
            await ctx.send("You have been marked active.")
        else:
            await ctx.send("You are already active.")

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
        filename = leaguedata.getPlayerName(target) + "_" + datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S") + "_Cardpool.txt"
        await leagueutils.sendMessageByContext(ctx, response, file=cardpool_stream, filename=filename)

    @commands.command(brief="Shows you the current leaderboard.", help="Shows you the current leaderboard.")
    async def leaderboard(self, ctx):
        leaderboardData = leaguedata.getLeaderboard()
        print(leaderboardData)
        response = "Leaderboard: \n"
        for datum in leaderboardData:
            response += (str(datum[1]).center(5) + " - " + str(datum[2]).center(5)) + " | " + str(datum[0]) + "\n"
        await ctx.send(response)

    @commands.command(aliases=['buy'], brief="Buys a pack of the given setcode.", help="Buys a pack of the given setcode, but does not open it.")
    async def buypack(self, ctx, setcode):
        playerEnergy = leaguedata.getPlayerEnergy(ctx.author.id)
        if playerEnergy >= valuestore.getValue("PACK_BASE_PRICE"):
            leaguedata.changePlayerEnergy(ctx.author.id, -1 * valuestore.getValue("PACK_BASE_PRICE"))
            leaguedata.givePlayerUnopenedPack(ctx.author.id, setcode)
            await ctx.send("Gave you a pack of " + setcode)
            return
        await ctx.send("You don't have enough energy.")
        return

    @commands.command(aliases=['op', "pack", "open"], brief="Opens a pack, should you have one to open.", help="Opens a pack. Begins with the first set out and then opens subsequent packs. Packs earned from losses will be opened last and will always be of the current set.")
    async def openpack(self, ctx, setcode=None):
        if leagueutils.isPM(ctx.message):
            response = "Please open packs in public, where we can all share the excitement!\n"
            await ctx.send(response)
            return

        unopenedPackData = leaguedata.getPlayersUnopenedPacks(ctx.author.id)

        if len(unopenedPackData) == 0:
            response = "You don't have any packs to open."
            await ctx.send(response)
            return
        
        if (setcode is None):
            setcode = unopenedPackData[0][0]

        hasFoundPackOfSet = False
        toOpen = 0

        for setPackInfo in unopenedPackData:
            toOpen += setPackInfo[1]
            if setPackInfo[0] == setcode:
                hasFoundPackOfSet = True

        if not hasFoundPackOfSet:
            response = "Can't find a pack of that set you need to open."
            await ctx.send(response)
            return

        p = Pack()
        p.generate(setcode)

        response = ctx.author.name + " opened a pack of " + setcode + "!" + "\n\n"

        response += "Its contents:\n\n"

        commonsData = p.cardData[0:p.commons]
        uncommonsData = p.cardData[p.commons:p.commons + p.uncommons]
        rareData = p.cardData[p.commons + p.uncommons: p.commons + p.uncommons + p.rares]
        mythicData = p.cardData[p.commons + p.uncommons + p.rares:]

        leaguedata.playerOpenExistingPack(ctx.author.id, p)

        commonsBody = "Commons:\n" + "\n".join(commonsData) + "\n\n"
        response += commonsBody

        uncommonsBody = "*Uncommons:*\n" + "\n".join(uncommonsData) + "\n\n"
        response += uncommonsBody

        def getMIDLink(cardName, surrounder):
            mId = leaguedata.getMultiverseId(cardName, setcode)
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
        if not leaguedata.getIsPlayerActive(ctx.author.id):
            response = "You are not active. Please set yourself as active and try again.\nThe game was not recorded.\n"
            await ctx.send(response)
            return
        if not leaguedata.isUserInLeague(leagueutils.getIDFromMention(opponent)):
            response = "Your opponent is not in the league.\nThe game was not recorded.\n"
            await ctx.send(response)
            return
        if not leaguedata.getIsPlayerActive(leagueutils.getIDFromMention(opponent)):
            response = "Your opponent is not active in the league. Please have your opponent set themselves as active and try again.\nThe game was not recorded.\n"
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
        numGamesToday = len(gamesToday)

        gamesThisWeek = leaguedata.getGamesThisWeek(winnerID, loserID)
        numGamesThisWeek = len(gamesThisWeek)

        gamesEver = leaguedata.getGamesEver(winnerID, loserID)
        numGamesEver = len(gamesEver)

        if numGamesToday >= valuestore.getValue("MAX_IDENTICAL_GAMES_PER_DAY"):
            response = "Players have already played " + str(numGamesToday) + " time(s) today. (Limit: " + str(leaguedata.MAX_IDENTICAL_GAMES_PER_DAY) + ")\nThe game was not recorded.\n"
            await ctx.send(response)
            return

        if numGamesThisWeek >= valuestore.getValue("MAX_IDENTICAL_GAMES_PER_WEEK"):
            response = "Players have already played " + str(numGamesThisWeek) + " time(s) this week. (Limit: " + str(leaguedata.MAX_IDENTICAL_GAMES_PER_WEEK) + ")\nThe game was not recorded.\n"
            await ctx.send(response)
            return

        leaguedata.addGame(winnerID, loserID)
        response = "Game successfully recorded.\n"

        winnerRival = leaguedata.getPlayerRival(winnerID)
        loserRival = leaguedata.getPlayerRival(loserID)

        isWinnerRivalGame = (winnerRival == loserID) and not leaguedata.hasPlayerPlayedRival(winnerID)
        isLoserRivalGame = (loserRival == winnerID) and not leaguedata.hasPlayerPlayedRival(loserID)

        newWins = leaguedata.getPlayerWins(winnerID)
        newLosses = leaguedata.getPlayerLosses(loserID)

        basePlayEnergy = valuestore.getValue("ENERGY_PER_PLAY")
        duplicateGamePlayPenalty = valuestore.getValue("IDENTICAL_GAME_PLAY_ENERGY_DECAY") * numGamesThisWeek
        minimumPlayEnergy = valuestore.getValue("ENERGY_PER_PLAY_MINIMUM")

        baseWinEnergy = valuestore.getValue("ENERGY_WIN_BONUS")
        duplicateGameWinPenalty = valuestore.getValue("IDENTICAL_GAME_WIN_ENERGY_DECAY") * numGamesThisWeek
        minimumWinEnergy = valuestore.getValue("ENERGY_WIN_BONUS_MINIMUM")

        rivalGameBonus = valuestore.getValue("PLAY_RIVAL_ENERGY")
        rivalWinBonus = valuestore.getValue("BEAT_RIVAL_ENERGY")

        firstEverBonus = valuestore.getValue("FIRST_GAME_WITH_PLAYER_BONUS")

        effectiveBasePlayEnergy = max(basePlayEnergy - duplicateGamePlayPenalty, minimumPlayEnergy)
        effectiveWinBonusEnergy = max(baseWinEnergy - duplicateGameWinPenalty, minimumWinEnergy)
        winEnergy = effectiveBasePlayEnergy + effectiveWinBonusEnergy

        winnerEnergy = winEnergy
        loserEnergy = effectiveBasePlayEnergy

        if isWinnerRivalGame:
            winnerEnergy += rivalGameBonus
            winnerEnergy += rivalWinBonus
            leaguedata.setHasPlayedRival(winnerID, 1)
        
        if isLoserRivalGame:
            loserEnergy += rivalGameBonus
            leaguedata.setHasPlayedRival(loserID, 1)

        if numGamesEver == 0:
            winnerEnergy += valuestore.getValue("FIRST_GAME_WITH_PLAYER_BONUS")
            loserEnergy += valuestore.getValue("FIRST_GAME_WITH_PLAYER_BONUS")

        leaguedata.changePlayerEnergy(winnerID, winnerEnergy)
        leaguedata.changePlayerEnergy(loserID, loserEnergy)

        response += leaguedata.getPlayerName(winnerID) + " now has " + str(newWins) + " wins and gains " + str(winnerEnergy) + " energy.\n"
        response += leaguedata.getPlayerName(loserID) + " now has " + str(newLosses) + " losses and gains " + str(loserEnergy) + " energy.\n"

        response += "\nEnergy breakdown:\n"
        response += "\tBase Energy: " + str(effectiveBasePlayEnergy) + "\n"
        response += "\t\t\tBase Play Energy: " + str(basePlayEnergy) + "\n"
        response += "\t\t\tDuplicate Game Penalty: " + str(effectiveBasePlayEnergy - basePlayEnergy) + "\n"
        response += "\tWin Bonus Energy: " + str(effectiveWinBonusEnergy) + "\n"
        response += "\t\t\tBase Win Energy: " + str(baseWinEnergy) + "\n"
        response += "\t\t\tDuplicate Game Penalty: " + str(effectiveWinBonusEnergy - baseWinEnergy) + "\n"

        if isWinnerRivalGame or isLoserRivalGame:
            response += "\tRival Game Energy: " + str(rivalGameBonus) + "\n"

        if numGamesEver == 0:
            response += "\tFirst Ever Time Playing Together: " + str(firstEverBonus)

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

        rivalID = leaguedata.getPlayerRival(ctx.author.id)

        if not rivalID == -1:
            rivalName = leaguedata.getPlayerName(rivalID)
            response += "Your rival is " + rivalName + ". "
        else:
            response += "You currently have no valid rival. "

        if leaguedata.hasPlayerPlayedRival(ctx.author.id):
            response += "You have already played them this week."

        response += "\n\n"

        weekNum = leagueutils.getWeekNumber()

        nextWeekStart = valuestore.getValue("START_DATE") + timedelta(days=(7 * weekNum))
        now = datetime.datetime.now()

        timeTillNextWeekStart = nextWeekStart - now

        timeString = leagueutils.getTimeDifferenceFormattedString(timeTillNextWeekStart)

        response += "It is currently week " + str(weekNum) + " (" + timeString + " left)\n"
        response += "The current set is " + leagueutils.getCurrentSet() + "\n"

        if leagueutils.getWeekNumber() >= leaguedata.DECK_SIZE_40_WEEK:
            response += "Decks should be 40 cards.\n\n"
        else:
            response += "Decks should be 30 cards, but will need to be 40 cards starting on week 4.\n\n"

        energy = leaguedata.getPlayerEnergy(ctx.author.id)

        response += "You have " + str(energy) + " energy.\n"

        unopenedPackData = leaguedata.getPlayersUnopenedPacks(ctx.author.id)

        if len(unopenedPackData) == 0:
            response += "You have no packs to open at this time."
        else:
            for packrow in unopenedPackData:
                response += "You have " + str(packrow[1]) + " " + str(packrow[0]) + " packs to open!\n"

        response += "```"

        await ctx.send(response)

def setup(bot):
    bot.add_cog(UserCog(bot))
