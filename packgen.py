import sqlite3
import time
import random
import math


#def main():
#    p = Pack()
#    p.generate(Pack.KAHNS_SETCODE)
#    print(p.mythics, p.rares, p.uncommons, p.commons)
#    print(p.cardData)

class Pack:

    KAHNS_SETCODE = "IMA"
    FATE_SETCODE = "A25"
    DRAGONS_SETCODE = "UMA"

    DB_PATH = "data/AllPrintings.sqlite"

    # we are excluding common foils
    FOIL_CHANCE = 3/35

    # if it isn't a rare or mythic it'll be an uncommon
    FOIL_RAREMYTHIC_CHANCE = 1/3

    FOIL_RAREMYTHIC_RARE_CHANCE = 106/121
    FOIL_RAREMYTHIC_MYTHIC_CAHNCE = 15/121

    #chance of a mythic upgrade
    MYTHIC_CHANCE = 1/8

    #initial composition of a pack before considering foils, .etc
    BASE_MYTHICS = 0
    BASE_RARES = 1
    BASE_UNCOMMONS = 3
    BASE_COMMONS = 11

    COLOR_MAP = {}
    COLOR_MAP[0] = 'W'
    COLOR_MAP[1] = 'U'
    COLOR_MAP[2] = 'B'
    COLOR_MAP[3] = 'R'
    COLOR_MAP[4] = 'G'

    # strings for rarities in the sqlite database
    RARITY_MYTHIC = "\'mythic\'"
    RARITY_RARE = "\'rare\'"
    RARITY_UNCOMMON = "\'uncommon\'"
    RARITY_COMMON = "\'common\'"

    def __init__(self):
        self.cardData = []
        self.hasFoil = False

    def generate(self, set):
        conn = sqlite3.connect(Pack.DB_PATH)
        self.__c = conn.cursor()

        # store set info for later use and so we don't worry about later formatting
        self.set = set
        self.__setcode = "\'" + set + "\'"
        self.__setRarityDistro()
        self.__generateCards()

        conn.commit()
        self.__c.close()
        conn.close()

    # determines the composition of the pack itself
    def __setRarityDistro(self):
        num_mythics = Pack.BASE_MYTHICS
        num_rares = Pack.BASE_RARES
        num_uncommons = Pack.BASE_UNCOMMONS
        num_commons = Pack.BASE_COMMONS

        if Pack.__hasFoil():
            self.hasFoil = True
            num_commons -= 1
            if Pack.__isFoilRareMythic():
                if Pack.__isFoilRare():
                    num_rares += 1
                else:
                    num_mythics += 1
            else:
                num_uncommons += 1

        if Pack.__rareUpgrade():
            num_rares -= 1
            num_mythics += 1

        self.mythics = num_mythics
        self.rares = num_rares
        self.uncommons = num_uncommons
        self.commons = num_commons

    def __hasFoil():
        return random.random() < Pack.FOIL_CHANCE

    def __isFoilRareMythic():
        return random.random() < Pack.FOIL_RAREMYTHIC_CHANCE

    def __isFoilRare():
        return random.random() < Pack.FOIL_RAREMYTHIC_RARE_CHANCE

    def __rareUpgrade():
        return random.random() < Pack.MYTHIC_CHANCE

    def __generateCards(self):
        seededCommons, seededUncommons = self.__getSeededCards()

        commonData = self.__generateRarity(Pack.RARITY_COMMON, self.commons - len(seededCommons), seededCommons)
        self.cardData.extend(commonData)
        self.cardData.extend(seededCommons)

        uncommonData = self.__generateRarity(Pack.RARITY_UNCOMMON, self.uncommons - len(seededUncommons), seededUncommons)
        self.cardData.extend(uncommonData)
        self.cardData.extend(seededUncommons)

        rareData = self.__generateRarity(Pack.RARITY_RARE, self.rares)
        self.cardData.extend(rareData)

        mythicData = self.__generateRarity(Pack.RARITY_MYTHIC, self.mythics)
        self.cardData.extend(mythicData)

    def __getSeededCards(self):
        seededCards = list(range(0, self.commons + self.uncommons))
        random.shuffle(seededCards)
        seededCards = seededCards[0:len(Pack.COLOR_MAP.keys())]

        seededColors = list(Pack.COLOR_MAP.keys())
        random.shuffle(seededColors)

        seedInfo = []
        for i in range(0, len(seededColors)):
            seedInfo.append((seededCards[i], seededColors[i]))

        seededCommons = []
        seededUncommons = []

        for seedCard in seedInfo:
            if seedCard[0] < self.commons:
                command = self.__getCardGenCommand(Pack.RARITY_COMMON, 1, colors=Pack.COLOR_MAP[seedCard[1]], excludedNames=seededCommons)
                for row in self.__c.execute(command):
                    seededCommons.append(row[0])
            else:
                command = self.__getCardGenCommand(Pack.RARITY_UNCOMMON, 1, colors=Pack.COLOR_MAP[seedCard[1]], excludedNames=seededUncommons)
                for row in self.__c.execute(command):
                    seededUncommons.append(row[0])
        return seededCommons, seededUncommons

    def __getCardGenCommand(self, rarity, number, colors="", excludedNames = []):
        select = "SELECT name FROM cards "
        where = "WHERE "
        where += "rarity = " + rarity + " "
#        where += "AND (frameVersion = 2003 OR frameVersion = 2015) "
        where += "AND layout != \'vanguard\' "
#        where += "AND setcode = " + self.__setcode + " "
        if not colors == "":
            where += "AND colors = \'" + colors + "\' "
        for name in excludedNames:
            where += "AND name != \'" + name.replace("'", r"''") + "\' "
        where += "AND name != \'Plains\' AND name != \'Island\' AND name != \'Swamp\' AND name != \'Mountain\' AND name != \'Forest\' AND name != \'Ice\' "
        order = "ORDER BY random() "
        limit = "LIMIT " + str(number)

        command = select + where + order + limit
#        print(command)
        return command

    def __generateRarity(self, rarity, number, excludedNames=[]):
        data = []
        command = self.__getCardGenCommand(rarity, number, excludedNames=excludedNames)
        for row in self.__c.execute(command):
            data.append(row[0])
        return data

#main()
