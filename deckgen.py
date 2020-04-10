import sqlite3
import time
import random
import math

WRITE_MODE = True
PRINT_MODE = True

NUM_SEEDED_BY_CMC = [0, 1, 2, 2, 1, 1, 0]
NUM_SEEDED_COLOR = sum(NUM_SEEDED_BY_CMC)
NUM_SEEDED_CARDS = NUM_SEEDED_COLOR * 5
PERCENT_SEEDED_CREATURES = 0.75
NUM_SEEDED_CREATURES = math.floor(NUM_SEEDED_CARDS * 0.6)

NUM_UNSEEDED = 25

COLOR_MAP = {}
COLOR_MAP[0] = 'W'
COLOR_MAP[1] = 'U'
COLOR_MAP[2] = 'B'
COLOR_MAP[3] = 'R'
COLOR_MAP[4] = 'G'

UNIVERSAL_EXCLUDER = "types != \'Plane\' AND types != \'Vanguard\' AND types != \'Conspiracy\' AND types != \'Scheme\' AND types != \'Phenomenon\'"

def main():
    global conn
    conn = sqlite3.connect('data/AllPrintings.sqlite')
    global c
    c = conn.cursor()

#    debugCommand = "PRAGMA table_info(cards);"
#    debugCommand = "SELECT * FROM cards LIMIT 5;"
#    debugCommand = "SELECT DISTINCT rarity FROM cards LIMIT 200;"
#    debugCommand = "SELECT COUNT(*) FROM cards;"
#    debugCommand = "SELECT name, supertypes FROM cards WHERE setcode = \'KTK\' AND rarity=\'common\' AND LIMIT 100;"

    try:
        debugCommand
    except NameError:
        debugCommand = None

    if not debugCommand is None:
        for row in c.execute(debugCommand):
            print(row)

#    makeRandomDeck()
    conn.commit()
    c.close()
    conn.close()

def makeRandomDeck():
    deckData = getManaBase()
    deckData.extend(getSeededCards())
    deckData.extend(getUnseededCards())
    outputDeck(deckData)

def getSeededCards():
    cards = []
    seededCardIds = list(range(0, NUM_SEEDED_CARDS))
    random.shuffle(seededCardIds)
    seededCardIds = seededCardIds[0:NUM_SEEDED_CREATURES]
    for i in range(0, NUM_SEEDED_CARDS):
        isCreature = i in seededCardIds
        neededColor = COLOR_MAP[math.floor(i / NUM_SEEDED_COLOR)]
        CMC = getSeededCMC(i)
        cards.append(getSeededCard(neededColor, isCreature, CMC))
    return cards

def getSeededCMC(i):
    location = i % NUM_SEEDED_COLOR
    for i in range (0, len(NUM_SEEDED_BY_CMC)):
        location -= NUM_SEEDED_BY_CMC[i]
        if location < 0:
            return i
    return -1

def getSeededCard(neededColor, isCreature, CMC):
    command = "SELECT name FROM cards WHERE colors = \'" + neededColor + "\' AND convertedManaCost = " + str(CMC)
    if isCreature:
        command += " AND types = \'Creature\'"
    command += " AND " + UNIVERSAL_EXCLUDER + " ORDER BY random() LIMIT 1;"
    cardData = ()
    for row in c.execute(command):
        cardData = (1, row[0])
    return cardData

def getUnseededCards():
    command = "SELECT name FROM cards "
    command += "WHERE " + UNIVERSAL_EXCLUDER
    command += " ORDER BY random() LIMIT " + str(NUM_UNSEEDED) + ";"
    cardData = []
    for row in c.execute(command):
        cardData.append((1, row[0]))
    return cardData

def getManaBase():
    return [
    (3, "Vivid Meadow"),
    (5, "Plains"),
    (3, "Vivid Creek"),
    (5, "Island"),
    (3, "Vivid Marsh"),
    (5, "Swamp"),
    (3, "Vivid Crag"),
    (5, "Mountain"),
    (3, "Vivid Grove"),
    (5, "Forest")
    ]

def outputDeck(deckData):
    if not (WRITE_MODE or PRINT_MODE):
        return
    outPath = "decks/" + str(int(time.time())) + ".txt"
    with open(outPath, 'w') as f:
        for cardData in deckData:
            postDataToFile(cardData, f)

def postDataToFile(card, f):
    outString = str(card[0]).ljust(5) + card[1]
    if WRITE_MODE:
        f.write(outString + "\n")
    if PRINT_MODE:
        print(outString)

main()
