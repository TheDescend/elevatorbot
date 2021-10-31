from dis_snek.models import Member

from ElevatorBot.backendNetworking.destiny.profile import DestinyProfile


async def on_member_add(member: Member):
    """ """
    # todo

    # only do stuff here if the member is not pending
    if not member.pending:
        # add registration role
        destiny_profile = DestinyProfile(client=member._client, discord_member=member, discord_guild=member.guild)
        await destiny_profile.assign_registration_role()


async def on_member_remove(member: Member):
    """ """
    # todo
    pass


async def on_member_update(before: Member, after: Member):
    """ """
    # todo

    # add registration role should the member no longer be pending
    if before.pending and not after.pending:
        destiny_profile = DestinyProfile(client=after._client, discord_member=after, discord_guild=after.guild)
        await destiny_profile.assign_registration_role()
