from discord.ext import commands
import io

import leaguedata
import leagueutils
from packgen import Pack

class UserCog(commands.Cog):

    async def cog_check(self, ctx):
        return leaguedata.isUserInLeague(ctx.author.id) and (not leagueutils.isPM(ctx.message))

    @commands.command()
    async def cardpool(self, ctx, *args):

        print(args)

        target = None
        if len(args) == 0:
            target = ctx.author.id
        elif len(args) == 1:
            target = leagueutils.getIDFromMention(args[0])
        else:
            response = "Cardpool Command:\n"
            response += "Usage: "
            response += "!league cardpool @user\n"
            response += "@user, if included, must be a valid mention on Discord.\n"
            response += "If @user is not included, will get the cardpool of the one who sent the message.\n"
            await ctx.send(response)
            return

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
        filename = leaguedata.getPlayerName(target) + "_Cardpool.txt"
        await leagueutils.sendMessageByContext(ctx, response, file=cardpool_stream, filename=filename)

    @commands.command()
    async def leaderboard(self, ctx):
        print("Test command")
        await ctx.send('Hello {0.display_name}.'.format(ctx.author))

    @commands.command()
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

    @commands.command()
    async def report(self, ctx):
        print("Test command")
        await ctx.send('Hello {0.display_name}.'.format(ctx.author))

    @commands.command()
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

    @commands.command()
    async def user(self, ctx):
        print("Test command")
        await ctx.send('Hello {0.display_name}.'.format(ctx.author))


def setup(bot):
    bot.add_cog(UserCog(bot))
