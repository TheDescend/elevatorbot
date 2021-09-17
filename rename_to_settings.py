# Fill out these settings, then rename the file to "settings.py" before running the app

# This setting enables additional console log and print statements
# Default: False
ENABLE_DEBUG_MODE: bool = False

# Enabling this makes ElevatorBot sync all slash commands on startup
# Enable to _update changes made, but disable if many restarts are made to prevent rate limits
# Default: True
SYNC_COMMANDS: bool = True

# The discord bot token to launch the bot
DISCORD_BOT_TOKEN: str = ""

# Your own bungie token, and you bungie secret data. Needed to access bungies api
BUNGIE_TOKEN: str = ""
B64_SECRET: str = ""
BUNGIE_OAUTH: str = ""

# Your steam token. This is needed to access the steam api and query the current amount of D2 players
STEAM_TOKEN: str = ""
