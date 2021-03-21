import shelve
import os.path
from os import path
import datetime
from datetime import timedelta

VALUE_STORE_FILE_PATH = "data/valuestore/values"

def initialize(ownerid, devMode):
    print("initializing valuestore")
    global values

    values = shelve.open(VALUE_STORE_FILE_PATH, writeback=True)

    values["DEV_MODE"] = devMode
    values["OWNER_ID"] = ownerid

    defaultValueSet("DB_PATH", "data/LeagueData.sqlite")
    defaultValueSet("START_DATE", datetime.datetime.now() + timedelta(days=7))
    defaultValueSet("LAST_WEEK_UPDATED", 0)
    defaultValueSet("LEAGUE_WEEKS_DURATION", 3)

    defaultValueSet("STARTING_ENERGY", 3000)
    defaultValueSet("ENERGY_PER_PLAY", 250)
    defaultValueSet("ENERGY_WIN_BONUS", 250)
    defaultValueSet("ENERGY_PER_WEEK", 1000)
    defaultValueSet("PLAY_RIVAL_ENERGY", 250)
    defaultValueSet("BEAT_RIVAL_ENERGY", 0)
    defaultValueSet("FIRST_GAME_WITH_PLAYER_BONUS", 250)

    defaultValueSet("IDENTICAL_GAME_PLAY_ENERGY_DECAY", 50)
    defaultValueSet("IDENTICAL_GAME_WIN_ENERGY_DECAY", 100)
    defaultValueSet("ENERGY_PER_PLAY_MINIMUM", 50)
    defaultValueSet("ENERGY_WIN_BONUS_MINIMUM", 50)

    defaultValueSet("MAX_IDENTICAL_GAMES_PER_DAY", 99)
    defaultValueSet("MAX_IDENTICAL_GAMES_PER_WEEK", 99)

    values.sync()

def defaultValueSet(key, value):
    global values
    if not (key in values):
        print(key + " value not found, set to default.")
        values[key] = value

def setValue(key, value):
    values[key] = value

def getValue(key):
    return values[key]

def hasValue(key):
    return key in values

def kill():
    global values
    values.close()