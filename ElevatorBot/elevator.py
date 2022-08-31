import asyncio
import inspect
import logging

from naff import AutoDefer, Intents, InteractionCommand, Listener, Permissions, Task, listen, logger_name, slash_command
from naff.ext.debug_extension import DebugExtension
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.text import Text

from ElevatorBot.discordEvents.base import ElevatorClient
from ElevatorBot.discordEvents.customInteractions import (
    ElevatorAutocompleteContext,
    ElevatorComponentContext,
    ElevatorInteractionContext,
    ElevatorModalContext,
    ElevatorPrefixedContext,
)
from ElevatorBot.misc.cache import descend_cache
from ElevatorBot.misc.helperFunctions import check_is_guild, yield_files_in_folder
from ElevatorBot.misc.status import update_discord_bot_status
from ElevatorBot.networking.errorCodesAndResponses import get_error_codes_and_responses
from ElevatorBot.startup.initAutocompleteOptions import load_autocomplete_options
from ElevatorBot.startup.initBackgroundEvents import register_background_events
from ElevatorBot.startup.initComponentCallbacks import add_component_callbacks
from ElevatorBot.startup.initDiscordEvents import register_discord_events
from ElevatorBot.startup.initDocs import create_command_docs
from ElevatorBot.startup.initLogging import init_logging
from ElevatorBot.static.descendOnlyIds import descend_channels
from ElevatorBot.static.emojis import custom_emojis
from ElevatorBot.webserver.server import run_webserver
from Shared.functions.logging import DESCEND_COLOUR, ColourHighlighter, ElevatorLogger
from Shared.functions.readSettingsFile import get_setting


class Elevator(ElevatorClient):
    # load startup event
    @listen()
    async def on_startup(self):
        """Gets triggered on startup"""

        startup_progress.update(startup_task, advance=1)

        self.logger_exceptions.debug("Loading error code responses...")
        get_error_codes_and_responses(client=client)
        startup_progress.update(startup_task, advance=1)

        self.logger_exceptions.debug("Creating docs for commands...")
        create_command_docs(client)
        startup_progress.update(startup_task, advance=1)

        self.logger_exceptions.debug("Loading Background Events...")
        await register_background_events(client)
        startup_progress.update(startup_task, advance=1)

        self.logger_exceptions.debug("Launching the Status Changer...")
        # its **important** that this has a reference - https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task
        task = asyncio.create_task(update_discord_bot_status(client))
        startup_progress.update(startup_task, advance=1)

        self.logger_exceptions.debug("Start Webserver...")
        task2 = asyncio.create_task(run_webserver(client=client))
        startup_progress.update(startup_task, advance=1)

        self.logger_exceptions.debug("Loading Custom Emoji...")
        await custom_emojis.init_emojis(client)
        startup_progress.update(startup_task, advance=1)

        self.logger_exceptions.debug("Setting Up Descend Data...")
        is_descend = await descend_channels.init_channels(client)
        if is_descend:
            await descend_cache.init_status_message()
        startup_progress.update(startup_task, advance=1)

        startup_progress.stop()

    def get_command_by_name(self, name: str) -> InteractionCommand:
        for scope, commands in self.interactions.items():
            for resolved_name, command in commands.items():
                if resolved_name == name:
                    return command


def load_commands(client: ElevatorClient, reload: bool = True) -> int:
    """Load all command modules. Returns number of local commands"""

    # load commands
    client.logger_exceptions.debug("Loading Commands...")
    for path in yield_files_in_folder("ElevatorBot/commands", "py"):
        if reload:
            client.reload_extension(path)
        else:
            client.load_extension(path)

    global_commands = len(client.interactions[0])
    client.logger_exceptions.debug(f"< {global_commands} > Global Commands Loaded")
    startup_progress.update(startup_task, advance=1)

    local = 0
    for k, v in client.interactions.items():
        if k != 0:
            local += len(v)
    client.logger_exceptions.debug(f"< {local} > Local Commands Loaded")
    startup_progress.update(startup_task, advance=1)

    # load context menus
    client.logger_exceptions.debug("Loading Context Menus...")
    for path in yield_files_in_folder("ElevatorBot/contextMenus", "py"):
        client.reload_extension(path)

    global_context_menus = len(client.interactions[0])
    client.logger_exceptions.debug(f"< {global_context_menus - global_commands} > Global Context Menus Loaded")
    startup_progress.update(startup_task, advance=1)

    return local


if __name__ == "__main__":
    # print ascii art
    console = Console()
    text = Text.assemble(
        (
            """
 ███████ ██      ███████ ██    ██  █████  ████████  ██████  ██████  ██████   ██████  ████████
 ██      ██      ██      ██    ██ ██   ██    ██    ██    ██ ██   ██ ██   ██ ██    ██    ██
 █████   ██      █████   ██    ██ ███████    ██    ██    ██ ██████  ██████  ██    ██    ██
 ██      ██      ██       ██  ██  ██   ██    ██    ██    ██ ██   ██ ██   ██ ██    ██    ██
 ███████ ███████ ███████   ████   ██   ██    ██     ██████  ██   ██ ██████   ██████     ██
══════════════════════════════════════════════════════════════════════════════════════════════
    """,
            DESCEND_COLOUR,
        )
    )
    console.print(Panel.fit(text, padding=(0, 6), border_style="black"))

    # loading bar
    startup_progress = Progress()
    startup_progress.start()
    startup_task = startup_progress.add_task("Starting Up...", total=16)

    # config logging
    init_logging()
    logger = logging.getLogger("generalExceptions")

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
        sync_interactions=get_setting("SYNC_COMMANDS"),
        delete_unused_application_cmds=not get_setting("ENABLE_DEBUG_MODE"),
        asyncio_debug=get_setting("ENABLE_DEBUG_MODE"),
        fetch_members=True,
        auto_defer=AutoDefer(enabled=True),
        interaction_context=ElevatorInteractionContext,
        prefixed_context=ElevatorPrefixedContext,
        component_context=ElevatorComponentContext,
        autocomplete_context=ElevatorAutocompleteContext,
        modal_context=ElevatorModalContext,
        logger=ElevatorLogger.make_console_logger(
            logger=logging.getLogger("naff"),
            level=logging.DEBUG if get_setting("ENABLE_DEBUG_MODE") else logging.WARNING,
            highlighter=ColourHighlighter(name="NAFF", colour="red"),
        ),
    )

    # install uvloop for faster asyncio (docker only)
    try:
        import uvloop  # noqa
    except ModuleNotFoundError:
        logger.debug("Uvloop not installed, skipping")
    else:
        logger.debug("Installing uvloop...")
        uvloop.install()
    startup_progress.update(startup_task, advance=1)

    # load the debug module for the debug guilds only
    class CustomDebugModule(DebugExtension):
        def __init__(self, bot: ElevatorClient):
            super().__init__(bot)
            self.add_ext_check(check_is_guild())

        def __new__(cls, bot: ElevatorClient, *args, **kwargs):
            for name, val in inspect.getmembers(cls):
                if isinstance(val, InteractionCommand):
                    val.scopes = get_setting("COMMAND_GUILD_SCOPE")
                    val.default_member_permissions = Permissions.ADMINISTRATOR
                    val.dm_permission = False
                elif isinstance(val, Listener | Task):
                    setattr(cls, name, None)
            return super().__new__(cls=cls, bot=bot, *args, **kwargs)

        @slash_command(name="debug", sub_cmd_name="reload", sub_cmd_description="Reload all modules")
        async def my_command_function(self, ctx: ElevatorInteractionContext):
            load_commands(client=ctx.bot)
            await ctx.send("Reload successful!")

    CustomDebugModule(bot=client)

    logger.debug("Loading Discord Events...")
    register_discord_events(client)
    startup_progress.update(startup_task, advance=1)

    logger.debug("Loading Component Callbacks...")
    add_component_callbacks(client=client)
    startup_progress.update(startup_task, advance=1)

    logger.debug("Loading Autocomplete Options...")
    asyncio.run(load_autocomplete_options())
    startup_progress.update(startup_task, advance=1)

    local_commands = load_commands(client=client, reload=False)

    local_context_menus = 0
    for key, value in client.interactions.items():
        if key != 0:
            local_context_menus += len(value)
    logger.debug(f"< {local_context_menus - local_commands} > Local Context Menus Loaded")
    startup_progress.update(startup_task, advance=1)

    # run the bot
    logger.debug(f"Logging Into Discord...")
    client.start(get_setting("DISCORD_APPLICATION_API_KEY"))
