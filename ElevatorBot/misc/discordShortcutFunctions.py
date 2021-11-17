from dis_snek.models import Member


async def assign_roles_to_member(member: Member, *role_ids: int, reason: str = None):
    """Assigns the role_ids to the member if they exist, else fails silently"""

    guild = member.guild

    # check if member is not pending
    if not member.pending:
        # loop through role_ids and get the role objs
        for role_id in role_ids:
            role = await guild.get_role(role_id)

            if not role:
                continue

            # assign them
            await member.add_role(role=role, reason=reason)


async def remove_roles_from_member(member: Member, *role_ids: int, reason: str = None):
    """Removes the role_ids from the member if they exist, else fails silently"""

    guild = member.guild

    # check if member is not pending
    if not member.pending:
        # loop through role_ids and get the role objs
        for role_id in role_ids:
            role = await guild.get_role(role_id)

            if not role:
                continue

            # remove them
            await member.remove_role(role=role, reason=reason)
