import asyncio

from dis_snek.models import ActionRow, Button, ButtonStyles, Member

from ElevatorBot.backendNetworking.destiny.clan import DestinyClan
from ElevatorBot.backendNetworking.destiny.profile import DestinyProfile
from ElevatorBot.core.destiny.roles import Roles
from ElevatorBot.misc.formating import embed_message
from ElevatorBot.static.descendOnlyIds import (
    bot_dev_channel_id,
    community_roles_channel_id,
    descend_guild_id,
    descend_no_nickname_role_id,
    join_log_channel_id,
    registration_channel_id,
)
from ElevatorBot.static.emojis import custom_emojis


async def on_member_add(member: Member, guild_id: int):
    """Triggers when a user joins a guild"""

    if not member.bot:
        client = member._client

        # descend only stuff
        if member.guild.id == descend_guild_id:
            # inform the user that they should registration with the bot
            await member.send(
                embeds=embed_message(
                    f"{custom_emojis.descend_logo} Welcome to Descend {member.name}! {custom_emojis.descend_logo}",
                    f"Before you can do anything else, you need to accept our rules. Please read them and accept them [> here <](discord://-/member-verification/{descend_guild_id}), if you have not done so already \n⁣\nYou can join the Destiny 2 clan in <#{registration_channel_id}>\nYou can find our current requirements in the same channel. \n⁣\nWe have a wide variety of roles you can earn, for more information, please use `roles overview` or check out <#{community_roles_channel_id}>\n⁣\nIf you have any problems / questions, do not hesitate to write {member._client.user.mention} (me) a personal message with your problem / question. This will get forwarded to staff",
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

    client = member._client

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
        # =========================================================================
        # remove destiny clan members from the clan
        # wait 10 min bc bungie takes forever in updating the clan roster
        await asyncio.sleep(10 * 60)

        clan = DestinyClan(ctx=None, client=client, discord_member=member, discord_guild=member.guild)

        # check if the user was in the clan
        result = await clan.get_clan_members(use_cache=False)
        if not result:
            raise ValueError

        # look if the member is in the clan
        for player in result.members:
            if player.discord_id == member.id:
                # prompt in bot-dev
                channel = await client.get_channel(bot_dev_channel_id)

                components = [
                    ActionRow(
                        Button(
                            style=ButtonStyles.GREEN,
                            label="Kick Them",
                        ),
                        Button(
                            style=ButtonStyles.RED,
                            label="Ignore This",
                        ),
                    )
                ]
                embed = embed_message(
                    "Clan Update", f"{member.mention} has left the Destiny 2 clan but is still in this discord server"
                )
                embed.add_field(name="Bungie Name", value=player.name, inline=True)
                embed.add_field(name="Destiny ID", value=player.destiny_id, inline=True)
                embed.add_field(name="System", value=player.system, inline=True)

                message = await channel.send(embeds=embed, components=components)

                # todo wait for component
                if reaction.emoji == yes:
                    # kick the user from the clan
                    result = await clan.kick_from_clan()

                    if result:
                        text = "Successfully removed!"
                    else:
                        text = "Something went wrong. Please remove them manually"
                else:
                    text = "Aborted"

                await button_ctx.send(text)


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

        # descend only stuff
        if after.guild.id == descend_guild_id:
            # change nickname back if it is not None
            if (not before.nickname) and after.nickname:
                if descend_no_nickname_role_id in [role.id for role in after.roles]:
                    await after.edit_nickname("")
