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
    #print("target id = ", id)
    #for row in c.execute("SELECT name, id FROM players"):
    #    print(row)
    for row in c.execute('SELECT COUNT(*) FROM players WHERE id=?', (id,)):
        #print(row[0] == 1)
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
#    command = "INSERT INTO packs (playerid, setcode, isLoss, contents) VALUES (" + str(id) + ", \'" + p.set + "\', " + str(int(isLossPack)) + ", \'" + cardContentString + "\')"
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
    playerName = author.name.replace("\'", "\'\'")
#    c.execute("INSERT INTO players (id, name) VALUES (" + str(author.id) + ", \'" + playerName + "\')")
    c.execute("INSERT INTO players (id, name) VALUES (?, ?)", (author.id, playerName,))
    conn.commit()
    return

def isMod(id):
    if id == OWNER_ID:
        return True
    for row in c.execute("SELECT COUNT(*) FROM players WHERE id=? AND isMod=1", (id,)):
        return row[0] == 1

def setMod(id, value):
    global c
    global conn
#    c.execute("UPDATE players SET isMod=" + str(value) + " WHERE id=" + str(id))
    c.execute("UPDATE players SET isMod=? WHERE id=?", (value, id,))
    conn.commit()

def addGame(winnerID, loserID):
    global c
    global conn
#    c.execute("INSERT INTO games (winner, loser) VALUES (" + str(winnerID) + ", " + str(loserID) + ")")
    c.execute("INSERT INTO games (winner, loser) VALUES (?, ?)", (winnerID, loserID,))
    conn.commit()

def isOwner(id):
    return id == OWNER_ID

def getGamesToday(player1ID, player2ID):
#    command = """
#    SELECT
#    timestamp
#    FROM
#    games
#    WHERE
#    (winner = """ + str(player1ID) + """
#    OR
#    loser = """ + str(player1ID) + """)
#    AND
#    (winner = """ + str(player2ID) + """
#    OR
#    loser = """ + str(player2ID) + """)"""
#    command += """ AND timestamp >= DATETIME('now', 'localtime', 'start of day')"""

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

#    command = """
#    SELECT
#    timestamp
#    FROM
#    games
#    WHERE
#    (winner = """ + str(player1ID) + """
#    OR
#    loser = """ + str(player1ID) + """)
#    AND
#    (winner = """ + str(player2ID) + """
#    OR
#    loser = """ + str(player2ID) + """)"""
#    command += """ AND timestamp >= DATETIME('now', 'localtime', 'start of day', '""" + str(daysBack) + """ day')"""

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

#tries to get multiverseid by name and set code
def getMultiverseId(name, setcode):
    cardDB = sqlite3.connect(Pack.DB_PATH)
    cardCursor = cardDB.cursor()
#    command = """
#    SELECT
#    multiverseId
#    FROM
#    cards
#    WHERE
#    (name = '""" + str(name.replace("'", "''")) + """'
#    AND
#    setcode = '""" + str(setcode) + """')
#    ORDER BY random() LIMIT 1"""
    command = """
    SELECT
    multiverseId
    FROM
    cards
    WHERE
    (name = ?
    AND
    setcode = ?)
    ORDER BY random() LIMIT 1"""
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
    command = """
    SELECT
    name, wins
    FROM
    (SELECT winner, COUNT(*) AS 'wins' FROM games GROUP BY winner) winners
    INNER JOIN
    players
    ON
    winners.winner=players.id
    ORDER BY
    wins DESC
    """
    leaderboard = []
    for row in c.execute(command):
        leaderboard.append((row[0], row[1]))
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
