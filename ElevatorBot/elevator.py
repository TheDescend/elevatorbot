import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dis_snek import AutoDefer, Intents, InteractionContext, Permissions, Snake, listen, logger_name, slash_command

from ElevatorBot.discordEvents.base import ElevatorSnake
from ElevatorBot.misc.helperFunctions import yield_files_in_folder
from ElevatorBot.misc.status import update_discord_bot_status
from ElevatorBot.startup.initAutocompleteOptions import load_autocomplete_options
from ElevatorBot.startup.initBackgroundEvents import register_background_events
from ElevatorBot.startup.initComponentCallbacks import add_component_callbacks
from ElevatorBot.startup.initDiscordEvents import register_discord_events
from ElevatorBot.startup.initDocs import create_command_docs
from ElevatorBot.startup.initLogging import init_logging
from ElevatorBot.static.descendOnlyIds import descend_channels
from ElevatorBot.static.emojis import custom_emojis
from ElevatorBot.webserver.server import run_webserver
from settings import COMMAND_GUILD_SCOPE, DISCORD_APPLICATION_API_KEY, ENABLE_DEBUG_MODE, SYNC_COMMANDS


class Elevator(ElevatorSnake):
    # register the scheduler for easier access
    scheduler = AsyncIOScheduler(timezone="UTC")

    # load startup event
    @listen()
    async def on_startup(self):
        """Gets triggered on startup"""

        print("Creating docs for commands...")
        create_command_docs(client)

        print("Loading Background Events...")
        await register_background_events(client)

        print("Launching the Status Changer...")
        # its **important** that this has a reference - https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task
        task = asyncio.create_task(update_discord_bot_status(client))

        print("Start Webserver...")
        task2 = asyncio.create_task(run_webserver(client=client))

        print("Loading Custom Emoji...")
        await custom_emojis.init_emojis(client)

        print("Setting Up Descend Data...")
        is_descend = await descend_channels.init_channels(client)
        if is_descend:
            # chunk descend and load its data, but not all guilds
            await descend_channels.guild.chunk_guild()

        print("Startup Finished!\n")
        print("--------------------------\n")


def load_commands(client: Snake) -> int:
    """Load all commands scales. Returns number of local commands"""

    # load commands
    print("Loading Commands...")
    for path in yield_files_in_folder("ElevatorBot/commands", "py"):
        # todo remove those once discord increases their stupid character limit (Currently 6145 chars)
        if "weapons.meta" not in path and "weapons.top" not in path and "rank.clan" not in path:
            client.reload_extension(path)

    global_commands = len(client.interactions[0])
    print(f"< {global_commands} > Global Commands Loaded")

    local = 0
    for k, v in client.interactions.items():
        if k != 0:
            local += len(v)
    print(f"< {local} > Local Commands Loaded")

    # load context menus
    print("Loading Context Menus...")
    for path in yield_files_in_folder("ElevatorBot/contextMenus", "py"):
        client.reload_extension(path)

    global_context_menus = len(client.interactions[0])
    print(f"< {global_context_menus - global_commands} > Global Context Menus Loaded")

    return local


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

    try:
        # install uvloop for faster asyncio (docker only)
        import uvloop

        print("Installing uvloop...")
        uvloop.install()
    except ModuleNotFoundError:
        print("Uvloop not installed, skipping")

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
    client = Elevator(
        intents=intents,
        sync_interactions=SYNC_COMMANDS,
        delete_unused_application_cmds=not ENABLE_DEBUG_MODE,
        asyncio_debug=ENABLE_DEBUG_MODE,
        fetch_members=True,
        auto_defer=AutoDefer(enabled=True),
    )

    if ENABLE_DEBUG_MODE:
        print("Setting Up Snek Logging...")
        cls_log = logging.getLogger(logger_name)
        cls_log.setLevel(logging.DEBUG)

    print("Loading Discord Events...")
    register_discord_events(client)

    print("Loading Component Callbacks...")
    add_component_callbacks(client=client)

    print("Loading Autocomplete Options...")
    asyncio.run(load_autocomplete_options(client))

    local_commands = load_commands(client=client)

    local_context_menus = 0
    for key, value in client.interactions.items():
        if key != 0:
            local_context_menus += len(value)
    print(f"< {local_context_menus - local_commands} > Local Context Menus Loaded")

    # load the reload command if debug mode is on
    if ENABLE_DEBUG_MODE:

        @slash_command(name="reload", description="Reload all scales", scopes=COMMAND_GUILD_SCOPE)
        async def my_command_function(ctx: InteractionContext):
            if not ctx.author.has_permission(Permissions.ADMINISTRATOR):
                await ctx.send("Admin Only")
                return
            load_commands(client=ctx.bot)
            await ctx.send("Reload successful!")

    # run the bot
    client.start(DISCORD_APPLICATION_API_KEY)
