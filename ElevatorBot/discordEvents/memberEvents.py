import asyncio

from naff import ActionRow, Button, ButtonStyles, Member
from naff.api.events import Component, MemberAdd, MemberRemove, MemberUpdate
from naff.client.errors import Forbidden

from ElevatorBot.core.destiny.lfg.lfgSystem import LfgMessage
from ElevatorBot.core.destiny.roles import Roles
from ElevatorBot.core.misc.persistentMessages import PersistentMessages
from ElevatorBot.misc.discordShortcutFunctions import assign_roles_to_member
from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.networking.destiny.clan import DestinyClan
from ElevatorBot.networking.destiny.lfgSystem import DestinyLfgSystem
from ElevatorBot.networking.destiny.profile import DestinyProfile
from ElevatorBot.networking.errors import BackendException
from ElevatorBot.static.descendOnlyIds import descend_channels
from ElevatorBot.static.emojis import custom_emojis
from Shared.functions.readSettingsFile import get_setting


async def on_member_add(event: MemberAdd):
    """Triggers when a user joins a guild"""

    if not event.member.bot:
        # descend only stuff
        if event.member.guild == descend_channels.guild:
            # inform the user that they should register with the bot
            try:
                await event.member.send(
                    embeds=embed_message(
                        f"{custom_emojis.descend_logo} Welcome to Descend {event.member.user.tag}! {custom_emojis.descend_logo}",
                        f"Before you can do anything else, you need to accept our rules. Please read them and accept them [> here <](discord://-/event.member-verification/{descend_channels.guild.id}), if you have not done so already \n⁣\nYou can join the Destiny 2 clan in {descend_channels.registration_channel.mention}\nYou can find our current requirements in the same channel. \n⁣\nWe have a wide variety of roles you can earn, for more information, please use `roles overview` or check out {descend_channels.community_roles_channel.mention}\n⁣\nIf you have any problems / questions, do not hesitate to write {event.bot.user.mention} (me) a personal message with your problem / question. This will get forwarded to staff",
                    )
                )
            except Forbidden:
                pass

        await _assign_roles_on_join(member=event.member)


async def on_member_remove(event: MemberRemove):
    """Triggers when a member leaves / gets kicked from a guild"""

    # descend only stuff
    if event.member.guild == descend_channels.guild:
        # =========================================================================
        # send a message in the join log channel
        embed = embed_message("Server Update", f"{event.member.mention} has left the server")
        embed.add_field(name="Display Name", value=event.member.display_name)
        embed.add_field(name="Name", value=event.member.user.tag)
        embed.add_field(name="Discord ID", value=event.member.id)
        await descend_channels.join_log_channel.send(embeds=embed)

        # =========================================================================
        # remove destiny clan event.members from the clan
        # wait 10 min bc bungie takes forever in updating the clan roster
        await asyncio.sleep(10 * 60)

        clan = DestinyClan(ctx=None, discord_guild=event.member.guild)

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
                    component: Component = await event.bot.wait_for_component(components=components)
                except asyncio.TimeoutError:
                    await message.edit(components=[])
                    return
                else:
                    button_ctx = component.ctx

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

    # =========================================================================
    # remove them from any lfg events
    backend = DestinyLfgSystem(
        ctx=None,
        discord_guild=event.member.guild,
    )
    try:
        result = await backend.user_get_all(discord_member=event.member)
    except BackendException:
        raise LookupError

    # delete them from all of the lfgs
    for lfg_event in result.joined + result.backup:
        guild = await event.bot.fetch_guild(lfg_event.guild_id)
        if not guild:
            raise ValueError
        backend = DestinyLfgSystem(ctx=None, discord_guild=guild)
        lfg_message = await LfgMessage.from_lfg_output_model(
            client=event.bot, model=lfg_event, backend=backend, guild=guild
        )

        await lfg_message.remove_member(member=event.member)


async def on_member_update(event: MemberUpdate):
    """Triggers when a member gets updated"""

    if not event.after.bot:
        # add registration role should the member no longer be pending
        if event.before.pending and not event.after.pending:
            await _assign_roles_on_join(member=event.after)

        # descend only stuff
        if event.after.guild == descend_channels.guild:
            # change nickname back if it is not None
            if (not event.before.nickname) and event.after.nickname:
                if get_setting("DESCEND_ROLE_NO_NICKNAME_ID") in [role.id for role in event.after.roles]:
                    await event.after.edit_nickname("")


async def _assign_roles_on_join(member: Member):
    """Assign all applicable roles when a member joins a guild"""

    # only do stuff here if the event.member is not pending
    if not member.pending:
        # assign member role for descend
        await assign_roles_to_member(
            member, get_setting("DESCEND_ROLE_MEMBER_ID"), reason="Member Screening Completion"
        )

        # assign registration roles in every guild
        destiny_profile = DestinyProfile(ctx=None, discord_member=member, discord_guild=member.guild)
        await destiny_profile.assign_registration_role()

        # add filler roles for descend
        if member.guild == descend_channels.guild:
            await assign_roles_to_member(
                member, *get_setting("DESCEND_ROLE_FILLER_IDS"), reason="Destiny 2 Filler Roles"
            )

        # assign their roles
        await Roles(guild=member.guild, member=member, ctx=None).update()
