from typing import Optional

from naff import Member, Permissions

from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from ElevatorBot.misc.formatting import embed_message


async def has_admin_permission(
    member: Member, ctx: Optional[ElevatorInteractionContext] = None, hidden: bool = True
) -> bool:
    """Returns if the member has admin permission"""

    result = member.has_permission(Permissions.ADMINISTRATOR)
    if ctx:
        if not ctx.responded:
            embed = embed_message(
                "Error",
                "You need admin permissions to do this",
            )

            await ctx.send(embeds=embed, ephemeral=hidden)

    return result


async def assign_roles_to_member(member: Member, *role_ids: int, reason: Optional[str] = None):
    """Assigns the role_ids to the member if they exist, else fails silently"""

    guild = member.guild

    # check if member is not pending
    if not member.pending:
        # loop through role_ids and get the role objs
        for role_id in role_ids:
            role = await guild.fetch_role(role_id)

            if not role:
                continue

            # assign them
            await member.add_role(role=role, reason=reason)


async def remove_roles_from_member(member: Member, *role_ids: int, reason: Optional[str] = None):
    """Removes the role_ids from the member if they exist, else fails silently"""

    guild = member.guild

    # check if member is not pending
    if not member.pending:
        # loop through role_ids and get the role objs
        for role_id in role_ids:
            role = await guild.fetch_role(role_id)

            if not role:
                continue

            # remove them
            await member.remove_role(role=role, reason=reason)
