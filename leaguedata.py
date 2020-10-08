import time
from datetime import date
import math

import sqlite3
from sqlite3 import Error

import leagueutils
from packgen import Pack

OWNER_ID = 260682887421100034
DB_PATH = "data/LeagueData.sqlite"
START_DATE = date(2020, 9, 24)
BASE_PACKS = 3
LOSSES_PER_PACK = 3
FRF_RELEASE_WEEK = 4
DTK_RELEASE_WEEK = 7
END_WEEK = 10
MAX_IDENTICAL_GAMES_PER_DAY = 3
MAX_IDENTICAL_GAMES_PER_WEEK = 9
DECK_SIZE_40_WEEK = 4

SQL_CREATE_PLAYER_TABLE = """ CREATE TABLE IF NOT EXISTS players (
id INTEGER PRIMARY KEY,
name TEXT,
isMod INTEGER DEFAULT 0,
timestamp DATETIME DEFAULT (DATETIME('now', 'localtime'))
); """

SQL_CREATE_GAMES_TABLE = """ CREATE TABLE IF NOT EXISTS games (
gameID INTEGER PRIMARY KEY AUTOINCREMENT,
winner INTEGER,
loser INTEGER,
timestamp DATETIME DEFAULT (DATETIME('now', 'localtime'))
); """

SQL_CREATE_PACKS_TABLE = """ CREATE TABLE IF NOT EXISTS packs (
packid INTEGER PRIMARY KEY AUTOINCREMENT,
playerid INTEGER,
setcode TEXT,
isLoss INTEGER DEFAULT 0,
contents TEXT,
timestamp DATETIME DEFAULT (DATETIME('now', 'localtime'))
); """

conn = None

WIPE_TABLES_ON_START = False
ON_START = True

def isUserInLeague(id):
    global c
    for row in c.execute('SELECT COUNT(*) FROM players WHERE id=?', (id,)):
        return row[0] == 1

def getPlayerLosses(id):
    global c
    for row in c.execute("SELECT COUNT(*) FROM games WHERE loser=?", (id,)):
        return row[0]

def getPlayerWins(id):
    global c
    for row in c.execute("SELECT COUNT(*) FROM games WHERE winner=?", (id,)):
        return row[0]

def getPlayerName(id):
    global c
    for row in c.execute("SELECT name FROM players WHERE id=?", (id,)):
        return row[0]

def getPlayerMaxPacks(id):
    playerLosses = getPlayerLosses(id)
    losspacks = math.floor(playerLosses / LOSSES_PER_PACK)
    weekNumber = leagueutils.getWeekNumber()
    KTKpacks = max(BASE_PACKS + min(weekNumber, FRF_RELEASE_WEEK - 1) - 1, BASE_PACKS)
    FRFpacks = max(min((weekNumber - FRF_RELEASE_WEEK) + 1, DTK_RELEASE_WEEK - FRF_RELEASE_WEEK), 0)
    DTKpacks = max(min((weekNumber - DTK_RELEASE_WEEK) + 1, END_WEEK - DTK_RELEASE_WEEK),  0)
    return KTKpacks, FRFpacks, DTKpacks, losspacks

def getPlayerOpenedPacks(id):
    global c
    KTKopened = None
    FRFopened = None
    DTKopened = None
    LOSSopened = None
    for row in c.execute("SELECT COUNT(*) FROM packs WHERE playerid=? AND setcode=? AND isLoss=0", (id, Pack.KAHNS_SETCODE,)):
        KTKopened = row[0]
    for row in c.execute("SELECT COUNT(*) FROM packs WHERE playerid=? AND setcode=? AND isLoss=0", (id, Pack.FATE_SETCODE,)):
        FRFopened = row[0]
    for row in c.execute("SELECT COUNT(*) FROM packs WHERE playerid=? AND setcode=? AND isLoss=0", (id, Pack.DRAGONS_SETCODE,)):
        DTKopened = row[0]
    for row in c.execute("SELECT COUNT(*) FROM packs WHERE playerid=? AND isLoss=1", (id,)):
        LOSSopened = row[0]
    return KTKopened, FRFopened, DTKopened, LOSSopened

def playerOpenedPack(id, p, isLossPack):
    global c
    global conn
    cardContentString = "|".join(p.cardData)
    cardContentString = cardContentString.replace("\'", "\'\'")
    command = "INSERT INTO packs (playerid, setcode, isLoss, contents) VALUES (?, ?, ?, ?)"
    c.execute(command, (id, p.set, int(isLossPack), cardContentString,))
    conn.commit()

def getCardpool(id):
    global c
    global conn
    cardpool = []
    command = "SELECT contents FROM packs WHERE playerid=?"
    for row in c.execute(command, (id,)):
        cardcontent = row[0]
        cardcontent = cardcontent.split("|")
        cardpool.extend(cardcontent)
    return cardpool

def addPlayer(author):
    global c
    global conn
    playerName = author.display_name.replace("\'", "\'\'")
    c.execute("INSERT INTO players (id, name) VALUES (?, ?)", (author.id, playerName,))
    conn.commit()
    return

def setPlayerName(id, name):
    global c
    global conn
    name = name.replace("\'", "\'\'")
    c.execute("UPDATE players SET name=? WHERE id=?", (name, id,))
    conn.commit()
    return

def isMod(id):
    global c
    if id == OWNER_ID:
        return True
    for row in c.execute("SELECT COUNT(*) FROM players WHERE id=? AND isMod=1", (id,)):
        return row[0] == 1

def setMod(id, value):
    global c
    global conn
    c.execute("UPDATE players SET isMod=? WHERE id=?", (value, id,))
    conn.commit()

def addGame(winnerID, loserID):
    global c
    global conn
    c.execute("INSERT INTO games (winner, loser) VALUES (?, ?)", (winnerID, loserID,))
    conn.commit()

def deleteGame(gameID):
    global c
    global conn
    c.execute("DELETE FROM games WHERE gameID=?", (gameID,))
    conn.commit()

def deletePack(packID):
    global c
    global conn
    c.execute("DELETE FROM packs WHERE packid=?", (packID,))

def isOwner(id):
    return id == OWNER_ID

def getGamesToday(player1ID, player2ID):
    command = """
    SELECT
    timestamp
    FROM
    games
    WHERE
    (winner = ?
    OR
    loser = ?)
    AND
    (winner = ?
    OR
    loser = ?)
    AND timestamp >= DATETIME('now', 'localtime', 'start of day')
    """
    times = []
    for row in c.execute(command, (player1ID, player1ID, player2ID, player2ID,)):
        times.append(row[0])
    return times

def getGamesThisWeek(player1ID, player2ID):
    startWeekday = START_DATE.weekday()
    todayWeekday = date.today().weekday()
    daysBack = -1 * ((todayWeekday + (7 - startWeekday)) % 7)
    command = """
    SELECT
    timestamp
    FROM
    games
    WHERE
    (winner = ?
    OR
    loser = ?)
    AND
    (winner = ?
    OR
    loser = ?)
    AND timestamp >= DATETIME('now', 'localtime', 'start of day', ?)"""
    times = []
    for row in c.execute(command, (player1ID, player1ID, player2ID, player2ID, str(daysBack) + " day")):
        times.append(row[0])
    return times

class GameData:
    def __init__(self, id, winnerID, loserID, timestamp):
        self.id = id
        self.winnerID = winnerID
        self.loserID = loserID
        self.timestamp = timestamp

def getLastGames(numGames, player):
    command = """
    SELECT
    *
    FROM
    games
    WHERE
    (winner LIKE ?
    OR
    loser LIKE ?)
    ORDER BY
    timestamp DESC
    LIMIT ?
    """
    gameData = []
    for row in c.execute(command, (player, player, numGames,)):
        gameData.append(GameData(row[0], row[1], row[2], row[3]))
    return gameData

class PackData():
    def __init__(self, id, playerid, set, isLossPack, contents, timestamp):
        self.id = id
        self.playerid = playerid
        self.set = set
        self.isLossPack = isLossPack
        self.contents = contents
        self.timestamp = timestamp

def getLastPacks(numPacks, player):
    command = """
    SELECT
    *
    FROM
    packs
    WHERE
    playerid LIKE ?
    ORDER BY
    packid DESC
    LIMIT ?
    """
    packData = []
    for row in c.execute(command, (player, numPacks,)):
        packData.append(PackData(row[0], row[1], row[2], row[3], row[4], row[5]))
    return packData

class PlayerData():
    def __init__(self, id, name, isMod, timestamp):
        self.id = id
        self.name = name
        self.isMod = isMod
        self.timestamp = timestamp

def getPlayers(numPlayers, pattern):
    command = """
    SELECT
    *
    FROM
    players
    WHERE
    name LIKE ?
    ORDER BY
    timestamp DESC
    LIMIT ?
    """
    playerdata = []
    for row in c.execute(command, (pattern, numPlayers,)):
        playerdata.append(PlayerData(row[0], row[1], row[2], row[3]))
    return playerdata

def getGameById(gameID):
    command = """
    SELECT
    *
    FROM
    games
    WHERE
    gameID=?
    LIMIT 1
    """
    for row in c.execute(command, (gameID,)):
        return GameData(row[0], row[1], row[2], row[3])

def swapWinner(gameID):
    command = """
    UPDATE
    games
    SET
    winner = loser,
    loser = winner
    WHERE
    gameID=?
    """
    for row in c.execute(command, (gameID,)):
        print(row)
    conn.commit()
    return

def updatePackContents(packid, newcontents):
    command = """
    UPDATE
    packs
    SET
    contents = ?
    WHERE
    packid = ?
    """
    for row in c.execute(command, (newcontents, packid)):
        print(row)
    conn.commit()
    return

#tries to get multiverseid by name and set code
def getMultiverseId(name, setcode):
    cardDB = sqlite3.connect(Pack.DB_PATH)
    cardCursor = cardDB.cursor()
    command = """
    SELECT
    multiverseId
    FROM
    cards
    WHERE
    (name = ?
    AND
    setcode = ?)
    ORDER BY
    random()
    LIMIT 1"""
    cardId = 0
    for response in cardCursor.execute(command, (name.replace("'", "''"),setcode,)):
        cardId = response[0]
    cardCursor.close()
    cardDB.close()
    return cardId

# if thisWeekOnly is true, get records only from this week
# otherwise get all records
def getLeaderboard():
    global c
#    command = """
#    SELECT
#    name, wins
#    FROM
#    (
#        SELECT winner,
#        COUNT(*)
#        AS 'wins'
#        FROM games
#        GROUP BY winner
#    )
#    winners
#    INNER JOIN
#    players
#    ON
#    winners.winner=players.id
#    ORDER BY
#    wins DESC
#    """

    command = """
    SELECT
    name, wins, losses
    FROM
    (
        SELECT winner,
        COUNT(*)
        AS 'wins'
        FROM games
        GROUP BY winner
    )
    winners
    INNER JOIN
    players
    ON
    winners.winner=players.id


    INNER JOIN
    (
        SELECT loser,
        COUNT(*)
        AS 'losses'
        FROM games
        GROUP BY loser
    )
    losers
    ON
    losers.loser=players.id

    ORDER BY
    wins DESC,
    losses ASC
    """
    leaderboard = []
    for row in c.execute(command):
        print(row)
        leaderboard.append((row[0], row[1], row[2]))
    return leaderboard

def connect(wipeTables=False, onStart=False):
    global conn
    global c
    try:
        conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        print("Database Connected!")
        c = conn.cursor()
        if wipeTables and onStart:
            print("Kill old tables")
            for row in c.execute("DROP TABLE IF EXISTS players"):
                print(row)
            for row in c.execute("DROP TABLE IF EXISTS games"):
                print(row)
            for row in c.execute("DROP TABLE IF EXISTS packs"):
                print(row)
            print("Refresh tables")
            for row in c.execute(SQL_CREATE_PLAYER_TABLE):
                print(row)
            for row in c.execute(SQL_CREATE_GAMES_TABLE):
                print(row)
            for row in c.execute(SQL_CREATE_PACKS_TABLE):
                print(row)
        print("Done with initial database operations.")
    except Error as e:
        print("Could not connect to Database!")
        print(e)

def kill():
    conn.commit()
    conn.close()
