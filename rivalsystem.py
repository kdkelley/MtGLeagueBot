import leaguedata
import random

def regenerateAllRivals():
    leaguedata.setAllPlayersNotPlayedWithRival()
    allPlayers = leaguedata.getAllActivePlayers()
    if len(allPlayers) <= 1:
        for player in allPlayers:
            leaguedata.setPlayerRival(player, -1)
        return

    random.shuffle(allPlayers)
    for i in range(1, len(allPlayers)):
        leaguedata.setPlayerRival(allPlayers[i-1], allPlayers[i])
    print(allPlayers)
    leaguedata.setPlayerRival(allPlayers[len(allPlayers) - 1], allPlayers[0])
