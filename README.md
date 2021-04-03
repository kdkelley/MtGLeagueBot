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

GitPython:

```
pip install GitPython
```

PyYAML:

```
pip install PyYAML
```

Jinja2:

```
pip install Jinja2
```

If you haven't already at this point you'll need to [create your application on discord](https://discord.com/developers/docs/intro).

You then need to make a file in the root directory named .env, and have its contents look something like this:

```
NORMAL_TOKEN="[BOT TOKEN]"
DEV_TOKEN="[BOT TOKEN]"
OWNER_ID="[YOUR DISCORD ID]"
```

Where [BOT TOKEN] is the token for the bot of your discord application. The DEV_TOKEN is used if the bot is running in dev mode. [YOUR DISCORD ID] should be your personal account ID on discord, or at least the id of the user you want to be considered the owner of the bot for permissions.

You will also need to download the .sqlite database for all of the MtG cards created by the MtGJSON project from [here](https://mtgjson.com/api/v5/AllPrintings.sqlite).

Put that file in a new directory named "data". Do not change its name.

To do initial setup run the bot with the -w or --wipe flags, and it should initialize all of the necessary tables.

If you did all of that properly the bot should now be functional. Keep in mind that Discord.py often will break completely as Discord updates, and will need to be updated regularly.
