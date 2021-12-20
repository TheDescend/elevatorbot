# Fill out these settings, then rename the file to "settings.py" before running the app

# This should be a list of guild_ids
# Some commands are only visible in the guilds you define here
COMMAND_GUILD_SCOPE: list[int] = []

# This setting changes the docker build process to no longer listen to file changes
# Annoying for testing, great for production
# Default: False
PRODUCTION: bool = False

# This setting enables additional console log and print statements
# Default: False
ENABLE_DEBUG_MODE: bool = False

# Enabling this makes ElevatorBot sync all slash commands on startup
# Enable to _update changes made, but disable if many restarts are made to prevent rate limits
# Default: True
SYNC_COMMANDS: bool = True

# This is the admin password for the website that is generated on startup
# Please change it to something only you know
# Username is "admin"
ADMIN_PASSWORD: str = ""

# The discord bot token to launch the bot
DISCORD_APPLICATION_API_KEY: str = ""

# Your own bungie token, and you bungie secret data. Needed to access bungies api
BUNGIE_APPLICATION_API_KEY: str = ""
BUNGIE_APPLICATION_CLIENT_SECRET: str = ""
BUNGIE_APPLICATION_CLIENT_ID: str = ""

# Your steam token. This is needed to access the steam api and query the current amount of D2 players
STEAM_APPLICATION_API_KEY: str = ""
