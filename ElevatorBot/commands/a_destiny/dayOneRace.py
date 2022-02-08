import asyncio
import copy
import datetime
import pickle
from io import BytesIO
from typing import Optional

import aiohttp
from anyio import create_task_group
from dis_snek import File, GuildText, InteractionContext, Member, Message, Timestamp, TimestampStyles, slash_command

from ElevatorBot.backendNetworking.destiny.account import DestinyAccount
from ElevatorBot.backendNetworking.destiny.activities import DestinyActivities
from ElevatorBot.backendNetworking.destiny.clan import DestinyClan
from ElevatorBot.backendNetworking.errors import BackendException
from ElevatorBot.commandHelpers.responseTemplates import something_went_wrong
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.destiny.dayOneRace import DayOneRace
from ElevatorBot.misc.formatting import embed_message, format_timedelta
from ElevatorBot.static.descendOnlyIds import descend_channels
from ElevatorBot.static.emojis import custom_emojis
from Shared.functions.helperFunctions import get_now_with_tz
from Shared.functions.readSettingsFile import get_setting
from Shared.networkingSchemas.destiny import DestinyActivityInputModel, DestinyActivityOutputModel
from Shared.networkingSchemas.destiny.clan import DestinyClanMemberModel, DestinyClanMembersModel

# =============
# Descend Only!
# =============


class DayOneRaceCommand(BaseScale):

    # todo perms
    @slash_command(
        name="day_one_raid_race",
        description="Starts the Day One raid completion announcer",
        scopes=get_setting("COMMAND_GUILD_SCOPE"),
    )
    async def day_one_raid_race(self, ctx: InteractionContext):
        if ctx.author.id != 238388130581839872:
            await ctx.send(
                "This is blocked for now, since it it waiting for a vital unreleased discord feature", ephemeral=True
            )
            return

        racer = DayOneRace(ctx=ctx)
        await racer.start()


def setup(client):
    DayOneRaceCommand(client)
