from dis_snek.models import Member

from ElevatorBot.backendNetworking.destiny.profile import DestinyProfile
from ElevatorBot.core.destiny.roles import Roles
from ElevatorBot.misc.formating import embed_message
from ElevatorBot.static.descendOnlyIds import (
    community_roles_channel_id,
    descend_guild_id,
    join_log_channel_id,
    registration_channel_id,
)
from ElevatorBot.static.emojis import custom_emojis


async def on_member_add(member: Member, guild_id: int):
    """Triggers when a user joins a guild"""

    if not member.bot:
        client = after._client

        # descend only stuff
        if member.guild.id == descend_guild_id:
            # inform the user that they should registration with the bot
            await member.send(
                embeds=embed_message(
                    f"{custom_emojis.descend_logo} Welcome to Descend {member.name}! {custom_emojis.descend_logo}",
                    f"You can join the Destiny 2 clan in <#{registration_channel_id}> . \nYou can find our current requirements in the same channel. \n⁣\nWe have a wide variety of roles you can earn, for more information, please use `roles overview` or check out <#{community_roles_channel_id}>\n⁣\nIf you have any problems / questions, do not hesitate to write {member._client.user.mention} (me) a personal message with your problem / question. This will get forwarded to staff",
                )
            )

        # only do stuff here if the member is not pending
        if not member.pending:
            # add registration role
            destiny_profile = DestinyProfile(ctx=None, client=client, discord_member=member, discord_guild=member.guild)
            await destiny_profile.assign_registration_role()

            # assign their roles
            await Roles(client=client, guild=member.guild, member=member, ctx=None).update()


async def on_member_remove(member: Member, guild_id: int):
    """Triggers when a member leaves / gets kicked from a guild"""

    # descend only stuff
    if member.guild.id == descend_guild_id:
        # send a message in the join log channel
        embed = embed_message("Member Left the Server", f"{member.mention} has left the server")
        embed.add_field(name="Display Name", value=member.display_name)
        embed.add_field(name="Name", value=member.name)
        embed.add_field(name="Discord ID", value=member.id)
        channel = await member.guild.get_channel(join_log_channel_id)
        await channel.send(embeds=embed)

        # todo removeFromClanAfterLeftDiscord(client, member)


async def on_member_update(before: Member, after: Member, guild_id: int):
    """Triggers when a member gets updated"""

    if not after.bot:
        client = after._client

        # add registration role should the member no longer be pending
        if before.pending and not after.pending:
            destiny_profile = DestinyProfile(ctx=None, client=client, discord_member=after, discord_guild=after.guild)
            await destiny_profile.assign_registration_role()

            # assign their roles
            await Roles(client=client, guild=after.guild, member=after, ctx=None).update()
