# MtGLeagueBot

This is the bot that I used to host an MtG league for the VTSFFC discord.

It has two dependencies, discord.py and dotenv.

To setup the bot the first thing you need to do is install these dependencies.

Discord.py:

```
# Linux/macOS
python3 -m pip install -U discord.py

# Windows
py -3 -m pip install -U discord.py
```

dotenv:

```
pip install -U python-dotenv
```

If you haven't already at this point you'll need to [create your application on discord](https://discord.com/developers/docs/intro).

You then need to make a file in the root directory named .env, and have its contents look something like this:

```
DISCORD_TOKEN="[BOT TOKEN]"
```

Where [BOT TOKEN] is the token for the bot of your discord application.

You will also need to download the .sqlite database for all of the MtG cards created by the MtGJSON project from [here](https://mtgjson.com/api/v5/AllPrintings.sqlite).

Put that file in a new directory named "data". Do not change its name.

At this point you need to go to the leaguedata.py file and make sure that the variable WIPE_TABLES_ON_START is set to True. Run the bot once, then kill the bot and set it to False before running the bot again.

If you did all of that properly the bot should now be functional. Keep in mind that Discord.py often will break completely as Discord updates, and will need to be updated regularly.
