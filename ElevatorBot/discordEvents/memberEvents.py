import asyncio

from dis_snek import Snake
from dis_snek.models import ActionRow, Button, ButtonStyles, Member
from dis_snek.models.events import Component, MemberAdd, MemberRemove, MemberUpdate

from ElevatorBot.backendNetworking.destiny.clan import DestinyClan
from ElevatorBot.backendNetworking.destiny.profile import DestinyProfile
from ElevatorBot.core.destiny.roles import Roles
from ElevatorBot.misc.discordShortcutFunctions import assign_roles_to_member
from ElevatorBot.misc.formating import embed_message
from ElevatorBot.static.descendOnlyIds import (
    descend_channels,
    descend_filler_role_ids,
    descend_no_nickname_role_id,
)
from ElevatorBot.static.emojis import custom_emojis


async def on_member_add(event: MemberAdd):
    """Triggers when a user joins a guild"""

    client = event.bot

    if not event.member.bot:
        # descend only stuff
        if event.member.guild == descend_channels.guild:
            # inform the user that they should registration with the bot
            await event.member.send(
                embeds=embed_message(
                    f"{custom_emojis.descend_logo} Welcome to Descend {event.member.name}! {custom_emojis.descend_logo}",
                    f"Before you can do anything else, you need to accept our rules. Please read them and accept them [> here <](discord://-/event.member-verification/{descend_channels.guild.id}), if you have not done so already \n⁣\nYou can join the Destiny 2 clan in {descend_channels.registration_channel.mention}\nYou can find our current requirements in the same channel. \n⁣\nWe have a wide variety of roles you can earn, for more information, please use `roles overview` or check out {descend_channels.community_roles_channel.mention}\n⁣\nIf you have any problems / questions, do not hesitate to write {client.user.mention} (me) a personal message with your problem / question. This will get forwarded to staff",
                )
            )

        # only do stuff here if the event.member is not pending
        if not event.member.pending:
            await _assign_roles_on_join(client=client, member=event.member)


async def on_member_remove(event: MemberRemove):
    """Triggers when a member leaves / gets kicked from a guild"""

    client = event.bot

    # descend only stuff
    if event.member.guild == descend_channels.guild:
        # send a message in the join log channel
        embed = embed_message("Member Left the Server", f"{event.member.mention} has left the server")
        embed.add_field(name="Display Name", value=event.member.display_name)
        embed.add_field(name="Name", value=event.member.name)
        embed.add_field(name="Discord ID", value=event.member.id)
        await descend_channels.join_log_channel.send(embeds=embed)

        # todo removeFromClanAfterLeftDiscord(client, event.member)
        # =========================================================================
        # remove destiny clan event.members from the clan
        # wait 10 min bc bungie takes forever in updating the clan roster
        await asyncio.sleep(10 * 60)

        clan = DestinyClan(ctx=None, client=client, discord_guild=event.member.guild)

        # check if the user was in the clan
        result = await clan.get_clan_members(use_cache=False)
        if not result:
            raise ValueError

        # look if the event.member is in the clan
        for player in result.members:
            if player.discord_id == event.member.id:
                # prompt in bot-dev
                components = [
                    ActionRow(
                        Button(
                            custom_id="clan_kick_yes",
                            style=ButtonStyles.GREEN,
                            label="Kick Them",
                        ),
                        Button(
                            custom_id="clan_kick_no",
                            style=ButtonStyles.RED,
                            label="Ignore This",
                        ),
                    )
                ]
                embed = embed_message(
                    "Clan Update",
                    f"{event.member.mention} has left the Destiny 2 clan but is still in this discord server",
                )
                embed.add_field(name="Bungie Name", value=player.name, inline=True)
                embed.add_field(name="Destiny ID", value=player.destiny_id, inline=True)
                embed.add_field(name="System", value=player.system, inline=True)

                message = await descend_channels.bot_dev_channel.send(embeds=embed, components=components)

                try:
                    component: Component = await client.wait_for_component(components=components)
                except asyncio.TimeoutError:
                    await message.edit(components=[])
                    return
                else:
                    button_ctx = component.context

                    if button_ctx.custom_id == "clan_kick_yes":
                        # kick the user from the clan
                        result = await clan.kick_from_clan(to_kick=event.member)

                        if result:
                            text = "Successfully removed!"
                        else:
                            text = "Something went wrong. Please remove them manually"
                    else:
                        text = "Aborted"

                    await button_ctx.send(text)


async def on_member_update(event: MemberUpdate):
    """Triggers when a member gets updated"""

    client = event.bot

    if not event.after.bot:
        # add registration role should the member no longer be pending
        if event.before.pending and not event.after.pending:
            await _assign_roles_on_join(client=client, member=event.after)

        # descend only stuff
        if event.after.guild == descend_channels.guild:
            # change nickname back if it is not None
            if (not event.before.nickname) and event.after.nickname:
                if descend_no_nickname_role_id in [role.id for role in event.after.roles]:
                    await event.after.edit_nickname("")


async def _assign_roles_on_join(client: Snake, member: Member):
    """Assign all applicable roles when a member joins a guild"""

    destiny_profile = DestinyProfile(ctx=None, client=client, discord_member=member, discord_guild=member.guild)
    await destiny_profile.assign_registration_role()

    # add filler roles for descend
    if member.guild == descend_channels.guild:
        await assign_roles_to_member(member=member, *descend_filler_role_ids, reason="Destiny 2 Filler Roles")

    # assign their roles
    await Roles(client=client, guild=member.guild, member=member, ctx=None).update()
