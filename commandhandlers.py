import io

from datetime import date

import leaguedata
import leagueutils
from packgen import Pack

# the help command should say if a user is in the league or not
# it should show how many packs they have opened vs could currently open
# it should also show current win and loss count
# should also include when the next pack is coming out (and what pack that will be)
async def handleHelp(message):
    response = await __getHelpResponse(message)
    await leagueutils.PMuser(message.author, response)

async def __getHelpResponse(message):
    response = "Help Command:\n"

    if not leaguedata.isUserInLeague(message.author.id):
        response += "You are NOT in the league\n"
        response += "You can join the league with the command:\n"
        response += "\"!league join\" without the quotes\n"
        return response

    wins = leaguedata.getPlayerWins(message.author.id)
    losses = leaguedata.getPlayerLosses(message.author.id)

    response += "You have " + str(wins) + " wins and " + str(losses) + " losses.\n\n"

    response += "It is currently week " + str(leagueutils.getWeekNumber()) + "\n"
    response += "The current set is " + leagueutils.getCurrentSet() + "\n"

    if leagueutils.getWeekNumber() >= leaguedata.DECK_SIZE_40_WEEK:
        response += "Decks should be 40 cards.\n\n"
    else:
        response += "Decks should be 30 cards, but will need to be 40 cards starting on week 4.\n\n"

    KTKpacks, FRFpacks, DTKpacks, losspacks = leaguedata.getPlayerMaxPacks(message.author.id)
    KTKopened, FRFopened, DTKopened, lossopened = leaguedata.getPlayerOpenedPacks(message.author.id)

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
        response += "You have " + str(KTKToOpen) + " KTK packs to open!\n"

    if FRFToOpen > 0:
        response += "You have " + str(FRFToOpen) + " FRF packs to open!\n"

    if DTKToOpen > 0:
        response += "You have " + str(DTKToOpen) + " DTK packs to open!\n"

    if KTKToOpen + FRFToOpen + DTKToOpen == 0:
        response += "There are no packs you need to open at this time.\n"
    else:
        response += "You can open them using \"!league openpack\".\n The set opened will be chosen in order.\n Packs from losses will automatically move to the latest set when it releases.\n"

    response += "\nOther commands:\n"
    response += "\"!league help\" -- Get this message.\n"
    response += "\"!league report @otherplayer Me/I/Them/They\" -- Report the result of a game. If you type \"me\" or \"I\" that means you (the person posting the message) won and vise versa.\n"
    response += "\"!league openpack\" -- Opens a pack (if you have any to open). The contents of which are automatically added to your cardpool.\n"
    response += "\"!league cardpool [@player]\" -- Bot will PM you a .txt with @player's cardpool. If no player is specified, it will send you your own card pool.\n"
    response += "\"!league leaderboard\" -- See the current leaderboard."

#    response += "KTKpacks = " + str(KTKopened) + " / " + str(KTKpacks) + "\n"
#    response += "FRFpacks = " + str(FRFopened) + " / " + str(FRFpacks) + "\n"
#    response += "DTKpacks = " + str(DTKopened) + " / " + str(DTKpacks) + "\n"
#    response += "losspacks = " + str(lossopened) + " / " + str(losspacks) + "\n"
    return response

async def handleJoin(message):
    if leaguedata.isUserInLeague(message.author.id):
        response = "You are already in the league.\n"
        await leagueutils.sendMessage(message.channel, response)
        return
    leaguedata.addPlayer(message.author)
    response = "Welcome to the league " + message.author.name + "!"
    await leagueutils.sendMessage(message.channel, response)

async def handleOpenPack(message):
    if not leaguedata.isUserInLeague(message.author.id):
        response = "You are not in the league.\n"
        await leagueutils.sendMessage(message.channel, response)
        return

    if leagueutils.isPM(message):
        response = "Please open packs in public, where we can all share the excitement!\n"
        await leagueutils.sendMessage(message.channel, response)
        return

    KTKpacks, FRFpacks, DTKpacks, losspacks = leaguedata.getPlayerMaxPacks(message.author.id)
    KTKopened, FRFopened, DTKopened, lossopened = leaguedata.getPlayerOpenedPacks(message.author.id)

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
        await leagueutils.sendMessage(message.channel, response)
        return

    p = Pack()
    p.generate(packSet)

    response = message.author.name + " opened a pack of " + packSet + "!\n Its contents:\n\n"

    commonsData = p.cardData[0:p.commons]
    uncommonsData = p.cardData[p.commons:p.commons + p.uncommons]
    rareData = p.cardData[p.commons + p.uncommons: p.commons + p.uncommons + p.rares]
    mythicData = p.cardData[p.commons + p.uncommons + p.rares:]

    leaguedata.playerOpenedPack(message.author.id, p, isLossPack)

    commonsBody = "Commons:\n" + "\n".join(commonsData) + "\n\n"
    response += commonsBody

    uncommonsBody = "*Uncommons:*\n" + "\n".join(uncommonsData) + "\n\n"
    response += uncommonsBody

    if p.rares > 0:
        rareBody = "__Rares:__\n" + "\n".join(rareData) + "\n\n"
        response += rareBody

    if p.mythics > 0:
        mythicBody = "__**Mythics!**__\n**" + "**\n**".join(mythicData) + "**\n\n"
        response += mythicBody

    await leagueutils.sendMessage(message.channel, response)

    return

async def handleSetMod(message):
    if not leaguedata.isUserInLeague(message.author.id):
        response = "You are not in the league.\n"
        await leagueutils.sendMessage(message.channel, response)
        return
    if not leaguedata.isMod(message.author.id):
        response = "You are not a mod.\n"
        await leagueutils.sendMessage(message.channel, response)
        return
    messageSplit = message.content.split()
    targetID = int(messageSplit[2][3:-1])
    modVal = int(messageSplit[3])
    leaguedata.setMod(targetID, modVal)

async def handleDebugChangeStartDate(message):
    if not leaguedata.isUserInLeague(message.author.id):
        response = "You are not in the league.\n"
        await leagueutils.sendMessage(message.channel, response)
        return
    if not leaguedata.isMod(message.author.id):
        response = "You are not a mod.\n"
        await leagueutils.sendMessage(message.channel, response)
        return
    messageSplit = message.content.split()
    year = int(messageSplit[2])
    month = int(messageSplit[3])
    day = int(messageSplit[4])
    leaguedata.START_DATE = date(year, month, day)

async def handleCardpool(message):
    messageSplit = message.content.split()

    if len(messageSplit) < 2:
        response = "Cardpool Command:\n"
        response += "Usage: "
        response += "!league cardpool @user\n"
        response += "@user, if included, must be a valid mention on Discord.\n"
        response += "If @user is not included, will get the cardpool of the one who sent the message.\n"
        leagueutils.PMuser(message.author, response)
        return

    target = None
    if len(messageSplit) == 2:
        target = message.author.id
    else:
        target = int(messageSplit[2][3:-1])

    if not leaguedata.isUserInLeague(target):
        response = "The target is not a player in the league.\n"
        await leagueutils.sendMessage(message.channel, response)
        return

    cardpool = leaguedata.getCardpool(target)

    if len(cardpool) == 0:
        response = "Player has no cards in their cardpool.\n"
        await leagueutils.sendMessage(message.channel, response)
        return

    response = "Cardpool is attached.\n"

    cardpool_stream = io.BytesIO("\n".join(cardpool).encode())
    filename = message.author.name + "_Cardpool.txt"
    await leagueutils.sendMessage(message.author, response, file=cardpool_stream, filename=filename)

async def handleReport(message):
    # gotta check two different restrictions
    # gotta check last game between these players, see if it was less than 18 hours ago
    # gotta check total number of games between these players this week, see if it is less than 3
    # if either criteria not met, gotta reject the game
    # gotta inform winner of their new win total:
    # weekly and global
    # gotta infrom loser of their new lose total (and if they can open a new pack)
    # for now intentionally not checking if the target is in the league or not, for debug
    messageSplit = message.content.split()
    winner = messageSplit[3].lower()
    winnerID = None
    loserID = None
    if winner == "i" or winner == "me":
        winnerID = message.author.id
        loserID = messageSplit[2][3:-1]
    elif winner == "they" or winner == "them":
        winnerID = messageSplit[2][3:-1]
        loserID = message.author.id

    if not leaguedata.isUserInLeague(message.author.id):
        response = "You are not in the league.\n"
        await leagueutils.sendMessage(message.channel, response)
        return
    if not leaguedata.isUserInLeague(int(messageSplit[2][3:-1])):
        response = "Your opponent is not in the league.\n"
        await leagueutils.sendMessage(message.channel, response)
        return

    gamesToday = leaguedata.getGamesToday(winnerID, loserID)
    gamesThisWeek = leaguedata.getGamesThisWeek(winnerID, loserID)

    if len(gamesToday) >= leaguedata.MAX_IDENTICAL_GAMES_PER_DAY:
        response = "Players have already played " + str(len(gamesToday)) + " time(s) today. (Limit: " + str(leaguedata.MAX_IDENTICAL_GAMES_PER_DAY) + ")\n"
        await leagueutils.sendMessage(message.channel, response)
        return

    if len(gamesThisWeek) >= leaguedata.MAX_IDENTICAL_GAMES_PER_WEEK:
        response = "Players have already played " + str(len(gamesThisWeek)) + " time(s) this week. (Limit: " + str(leaguedata.MAX_IDENTICAL_GAMES_PER_WEEK) + ")\n"
        await leagueutils.sendMessage(message.channel, response)
        return

    leaguedata.addGame(winnerID, loserID)
    response = "Game successfully recorded.\n"

    newWins = leaguedata.getPlayerWins(winnerID)
    newLosses = leaguedata.getPlayerLosses(loserID)

    response += leaguedata.getPlayerName(winnerID) + " now has " + str(newWins) + " wins.\n"
    response += leaguedata.getPlayerName(loserID) + " now has " + str(newLosses) + " losses."

    if newLosses % leaguedata.LOSSES_PER_PACK == 0:
        response += " They may open another pack using \"!league openpack\".\n"
    else:
        response += "\n"

    await leagueutils.sendMessage(message.channel, response)

async def handleLeaderboard(message):
    leaderboardData = leaguedata.getLeaderboard()
    response = "Leaderboard: \n"
    for datum in leaderboardData:
        response += str(datum[0]) + " -- " + str(datum[1]) + "\n"
    response += "\n Users without any wins are not shown in the leaderboard.\n"
    await leagueutils.sendMessage(message.channel, response)
