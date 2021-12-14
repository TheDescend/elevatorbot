import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dis_snek.models import listen
from dis_snek.models.enums import Intents

from ElevatorBot.discordEvents.base import register_discord_events
from ElevatorBot.discordEvents.errorEvents import CustomErrorSnake
from ElevatorBot.misc.status import update_discord_bot_status
from ElevatorBot.misc.veryMisc import yield_files_in_folder
from ElevatorBot.startup.initAutocompleteOptions import load_autocomplete_options
from ElevatorBot.startup.initBackgroundEvents import register_background_events
from ElevatorBot.startup.initComponentCallbacks import add_component_callbacks
from ElevatorBot.startup.initDocs import create_command_docs
from ElevatorBot.startup.initLogging import init_logging
from ElevatorBot.static.descendOnlyIds import descend_channels
from ElevatorBot.static.emojis import custom_emojis
from ElevatorBot.webserver.server import run_webserver
from settings import DISCORD_BOT_TOKEN, ENABLE_DEBUG_MODE, SYNC_COMMANDS


class ElevatorSnake(CustomErrorSnake):
    # register the scheduler for easier access
    scheduler = AsyncIOScheduler()

    # load startup event
    @listen()
    async def on_startup(self):
        """Gets triggered on startup"""

        print("Creating docs for commands...")
        create_command_docs(client)

        print("Loading Background Events...")
        await register_background_events(client)

        print("Launching the Status Changer...")
        asyncio.create_task(update_discord_bot_status(client))

        print("Start Webserver...")
        asyncio.create_task(run_webserver(client=client))

        print("Loading Custom Emoji...")
        await custom_emojis.init_emojis(client)

        print("Setting Up Descend Data...")
        await descend_channels.init_channels(client)

        # chunk descend and load its data, but not all guilds
        await descend_channels.guild.chunk_guild()

        print("Startup Finished!\n")
        print("--------------------------\n")


if __name__ == "__main__":
    # config logging
    init_logging()

    # print ascii art
    print("----------------------------------------------------------------------------------------")
    print(
        """
  ______   _                          _                    ____            _
 |  ____| | |                        | |                  |  _ \          | |
 | |__    | |   ___  __   __   __ _  | |_    ___    _ __  | |_) |   ___   | |_
 |  __|   | |  / _ \ \ \ / /  / _` | | __|  / _ \  | '__| |  _ <   / _ \  | __|
 | |____  | | |  __/  \ V /  | (_| | | |_  | (_) | | |    | |_) | | (_) | | |_
 |______| |_|  \___|   \_/    \__,_|  \__|  \___/  |_|    |____/   \___/   \__|
    """
    )
    print("----------------------------------------------------------------------------------------\n")
    print("Starting Up...")

    # enable intents to allow certain events--
    # see https://discord.com/developers/docs/topics/gateway#gateway-intents
    intents = Intents.new(
        guilds=True,
        guild_members=True,
        guild_messages=True,
        guild_voice_states=True,
        direct_messages=True,
    )

    # actually get the bot obj
    client = ElevatorSnake(
        intents=intents, sync_interactions=SYNC_COMMANDS, delete_unused_application_cmds=not ENABLE_DEBUG_MODE
    )

    print("Loading Discord Events...")
    register_discord_events(client)

    print("Loading Component Callbacks...")
    add_component_callbacks(client=client)

    print("Loading Autocomplete Options...")
    asyncio.run(load_autocomplete_options(client))

    # load commands
    print("Loading Commands...")
    for path in yield_files_in_folder("commands", "py"):
        # todo remove those once discord increases their stupid character limit (Currently 6145 chars)
        if "weapons.meta" not in path and "weapons.top" not in path:
            client.load_extension(path)

    global_commands = len(client.interactions[0])
    print(f"< {global_commands} > Global Commands Loaded")

    local_commands = 0
    for key, value in client.interactions.items():
        if key != 0:
            local_commands += len(value)
    print(f"< {local_commands} > Local Commands Loaded")

    # load context menus
    print("Loading Context Menus...")
    for path in yield_files_in_folder("contextMenus", "py"):
        client.load_extension(path)

    global_context_menus = len(client.interactions[0])
    print(f"< {global_context_menus - global_commands} > Global Context Menus Loaded")

    local_context_menus = 0
    for key, value in client.interactions.items():
        if key != 0:
            local_context_menus += len(value)
    print(f"< {local_context_menus - local_commands} > Local Context Menus Loaded")

    # run the bot
    client.start(DISCORD_BOT_TOKEN)
