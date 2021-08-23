import discord


async def assign_roles_to_member(
    member: discord.Member,
    *role_ids,
    reason: str = None
):
    """ Assigns the role_ids to the member if they exist, else fails silently """

    guild = member.guild

    # loop through role_ids and get the role objs
    roles = []
    for role_id in role_ids:
        role = guild.get_role(role_id)

        if not role:
            continue

        roles.append(role)

    # assign them
    await member.add_roles(*roles, reason=reason)


async def remove_roles_from_member(
    member: discord.Member,
    *role_ids,
    reason: str = None
):
    """ Removes the role_ids from the member if they exist, else fails silently """

    guild = member.guild

    # loop through role_ids and get the role objs
    roles = []
    for role_id in role_ids:
        role = guild.get_role(role_id)

        if not role:
            continue

        roles.append(role)

    # remove them
    await member.remove_roles(*roles, reason=reason)
