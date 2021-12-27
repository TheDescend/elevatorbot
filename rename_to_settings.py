from typing import Optional

# Fill out these settings, then rename the file to "settings.py" before running the app

# This should be a list of guild_ids
# Some commands are only visible in the guilds you define here
COMMAND_GUILD_SCOPE: list[int] = []

# This setting enables additional console log and print statements
# Default: False
ENABLE_DEBUG_MODE: bool = False

# Enabling this makes ElevatorBot sync all slash commands on startup
# Enable to update changes made, but disable if many restarts are made to prevent rate limits
# Default: True
SYNC_COMMANDS: bool = True

# This is the admin password for the website that is generated on startup
# Please change it to something only you know
# Username is "admin"
ADMIN_PASSWORD: str = "admin"

# The discord bot token to launch the bot
DISCORD_APPLICATION_API_KEY: str = ""

# Your own bungie token, and you bungie secret data. Needed to access bungies api
BUNGIE_APPLICATION_API_KEY: str = ""
BUNGIE_APPLICATION_CLIENT_SECRET: str = ""
BUNGIE_APPLICATION_CLIENT_ID: str = ""

# Your steam token. This is needed to access the steam api and query the current amount of D2 players
STEAM_APPLICATION_API_KEY: str = ""

# Your GitHub api data. This is needed to automatically post bug reports on the repo when users use `/bug`
# Use this to find your own repo ID - https://stackoverflow.com/questions/13902593/how-does-one-find-out-ones-own-repo-id/13902640
GITHUB_APPLICATION_API_KEY: Optional[str] = None
GITHUB_REPOSITORY_ID: Optional[int] = None

# The names of the labels the issues should get
GITHUB_ISSUE_LABEL_NAMES: Optional[list[str]] = None

# ======================================================================
# This bot is designed to run on the Descend discord server, where it has some extra functionality
# Thus, some hard-coding is required. To use those functionalities on your own server, please change the following settings
# Note: Not changing these settings while the bot is not in the Descend server **will** break some things
DESCEND_GUILD_ID: int = 669293365900214293

# Channel Ids
DESCEND_CHANNEL_ADMIN_ID: int = 671264040974024705
DESCEND_CHANNEL_BOT_DEV_ID: int = 671264040974024705
DESCEND_CHANNEL_REGISTRATION_ID: int = 671264040974024705
DESCEND_CHANNEL_COMMUNITY_ROLES_ID: int = 671264040974024705
DESCEND_CHANNEL_JOIN_LOG_ID: int = 671264040974024705

# Role Ids
DESCEND_ROLE_NO_NICKNAME_ID: int = 887021717053124659
DESCEND_ROLE_FILLER_IDS: list[int] = [670395920327639085, 670385837044662285, 670385313994113025, 776854211585376296]
