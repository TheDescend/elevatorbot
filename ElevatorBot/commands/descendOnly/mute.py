import asyncio

import discord
from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option

from ElevatorBot.commandHelpers.optionTemplates import get_user_option
from ElevatorBot.commandHelpers.permissionTemplates import permissions_admin
from ElevatorBot.misc.discordShortcutFunctions import assign_roles_to_member, remove_roles_from_member
from ElevatorBot.misc.formating import embed_message


# todo descend only permissions
from ElevatorBot.static.descendOnlyIds import descend_muted_role_id


class Mute(Cog):
    def __init__(
        self,
        client
    ):
        self.client = client


    @cog_ext.cog_slash(
        name="mute",
        description="Mutes specified user for specified time",
        options=[
            get_user_option(
                description="Which user to mute",
                required=True
            ),
            create_option(
                name="hours",
                description="How many hours to mute the user for",
                option_type=4,
                required=True,
            ),
        ],
        default_permission=False,
        permissions=permissions_admin,
    )
    async def _mute(
        self,
        ctx: SlashContext,
        user: discord.Member,
        hours: int
    ):
        """ Mutes specified user for specified time """

        await assign_roles_to_member(user, descend_muted_role_id, reason=f"/mute by {ctx.author}")

        status = await ctx.send(
            embed=embed_message(
                "Success",
                f"Muted {user.mention} for {hours} hours\nI will edit this message once the time is over",
            )
        )

        await asyncio.sleep(hours * 60 * 60)
        await remove_roles_from_member(user, descend_muted_role_id, reason=f"/mute by {ctx.author}")

        await status.edit(
            embed=embed_message(
                "Success",
                f"{user.mention} is no longer muted"
            )
        )


def setup(
    client
):
    client.add_cog(Mute(client))
