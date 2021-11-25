from dis_snek.models import InteractionContext, slash_command

from ElevatorBot.commands.base import BaseScale
from settings import COMMAND_GUILD_SCOPE


class Giveaway(BaseScale):
    # todo perm
    @slash_command(name="giveaway", description="Creates a giveaway", scopes=COMMAND_GUILD_SCOPE)
    async def _giveaway(self, ctx: InteractionContext):
        pass

        # todo neria that's your job
        # todo maybe context menu to draw winners once done


def setup(client):
    Giveaway(client)
