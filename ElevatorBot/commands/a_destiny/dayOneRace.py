from naff import slash_command

from ElevatorBot.commandHelpers.permissionTemplates import restrict_default_permission
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.core.destiny.dayOneRace import DayOneRace
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from Shared.functions.readSettingsFile import get_setting

# =============
# Descend Only!
# =============


class DayOneRaceCommand(BaseModule):
    @slash_command(
        name="day_one_raid_race",
        description="Starts the Day One raid completion announcer",
        scopes=get_setting("COMMAND_GUILD_SCOPE"),
    )
    @restrict_default_permission()
    async def day_one_raid_race(self, ctx: ElevatorInteractionContext):
        racer = DayOneRace(ctx=ctx)
        await racer.start()


def setup(client):
    DayOneRaceCommand(client)
