import asyncio

from naff import Member, Permissions, slash_command

from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commandHelpers.subCommandTemplates import roles_sub_command
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.core.destiny.roles import Roles
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from ElevatorBot.misc.formatting import embed_message

user_lock: dict[int, asyncio.Lock] = {}


class RoleGet(BaseModule):
    @slash_command(
        **roles_sub_command,
        sub_cmd_name="get",
        sub_cmd_description="Assigns you all the Destiny 2 achievement roles you have earned",
        dm_permission=False,
    )
    @default_user_option(description="**Admin only** | The user you want to look up")
    async def get(self, ctx: ElevatorInteractionContext, user: Member = None):
        if user:
            if not ctx.author.has_permission(Permissions.ADMINISTRATOR):
                await ctx.send(
                    ephemeral=True,
                    embeds=embed_message(
                        "Error",
                        "Only admins can use this command to update roles for other people, sorry.",
                    ),
                )
                return

        member = user or ctx.author

        if member.id not in user_lock:
            user_lock[member.id] = asyncio.Lock()

        async with user_lock[member.id]:
            # get new roles and update the member
            roles = Roles(ctx=ctx, guild=ctx.guild, member=member)
            await roles.update()


def setup(client):
    RoleGet(client)
