import copy

from naff import (
    AutoArchiveDuration,
    ChannelTypes,
    GuildCategory,
    GuildChannel,
    GuildForum,
    OptionTypes,
    PermissionOverwrite,
    Permissions,
    Role,
    slash_command,
    slash_option,
)
from naff.client.errors import Forbidden

from ElevatorBot.commandHelpers.permissionTemplates import restrict_default_permission
from ElevatorBot.commandHelpers.subCommandTemplates import setup_sub_command, setup_sub_command_lfg_group
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.core.misc.persistentMessages import handle_setup_command
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.static.emojis import custom_emojis


class LfgChannel(BaseModule):
    @slash_command(
        **setup_sub_command,
        **setup_sub_command_lfg_group,
        sub_cmd_name="channel",
        sub_cmd_description="Designate a forum channel where my LFG events get posted",
        dm_permission=False,
    )
    @slash_option(
        name="channel",
        description="The forum channel where the events should be created",
        required=True,
        opt_type=OptionTypes.CHANNEL,
        channel_types=[ChannelTypes.GUILD_FORUM],
    )
    @restrict_default_permission()
    async def channel(self, ctx: ElevatorInteractionContext, channel: GuildForum):
        reason = "LFG channel initialisation"

        # create channel perms
        everyone_role = await ctx.guild.fetch_role(ctx.guild.id)
        overwrite = PermissionOverwrite.for_target(target_type=everyone_role)
        overwrite.add_denies(Permissions.CREATE_POSTS | Permissions.SEND_MESSAGES_IN_THREADS)
        elevator_overwrite = PermissionOverwrite.for_target(target_type=ctx.guild.me)
        elevator_overwrite.add_allows(
            Permissions.CREATE_POSTS
            | Permissions.SEND_MESSAGES_IN_THREADS
            | Permissions.VIEW_CHANNEL
            | Permissions.MANAGE_CHANNELS
            | Permissions.ADD_REACTIONS
            | Permissions.USE_EXTERNAL_EMOJIS
        )

        # edit channel
        try:
            await channel.edit(
                topic=f"""- Visit the pinned post for a thorough guide\n- Use {ctx.client.get_command_by_name("lfg create").mention()} to create events\n- By joining you agree to be there on time""",
                permission_overwrites=[overwrite, elevator_overwrite],
                default_auto_archive_duration=AutoArchiveDuration.ONE_WEEK,
                reason=reason,
            )

            # delete old stuff
            for tag in channel.available_tags:
                await tag.delete()
            for post in await channel.fetch_posts() + await channel.archived_posts().flatten():
                await post.delete(reason=reason)

            # add tags with emojis, if found
            emojis = {emoji.name.lower(): emoji for emoji in await ctx.guild.fetch_all_custom_emojis()}
            await channel.create_tag(name="Searching...", emoji="🔎")

            await channel.create_tag(name="Raid", emoji=emojis.get("raid_icon", "🏆"))
            await channel.create_tag(name="Dungeon", emoji=emojis.get("dungeon_icon", "🏆"))
            await channel.create_tag(name="PvE", emoji=emojis.get("pve_icon", "🏆"))
            await channel.create_tag(name="PvP", emoji=emojis.get("pvp_icon", "🏆"))
            await channel.create_tag(name="Other")

            await channel.create_tag(name="Full!", emoji="🛑")

            await channel.create_tag(name="Archived", emoji="📁")

            # send and pin the tutorial
            post = await channel.create_post(
                name="LFG Tutorial",
                content=f"""
This guide is meant to help you navigate this channel and my LFG functionality.
⁣
{custom_emojis.circle} **Creating an event**
- Head to your local bot commands channel, or really any other channel (although you ~~might~~ will get yelled at for that).
- Use {ctx.client.get_command_by_name("lfg create").mention()} and follow the instructions.
⁣
{custom_emojis.circle} **Interacting with an event**
- Browse {channel.mention} to find events you may find interesting. They are sorted by their start time with the nearest times at the top.
- You can use the `Searching...` filter to only find events that are not full or filter by activity.
- To join / leave, click on the post and use the matching button at the bottom of the message.
""",
                embed=embed_message(
                    description=f"""
If you want to feel like an [expert](https://www.youtube.com/watch?v=BKorP55Aqvg), there are a bunch of additional commands you can use to interact with LFG events:
⁣
{custom_emojis.enter} {ctx.client.get_command_by_name("lfg create").mention()} - Create a new event
{custom_emojis.enter} {ctx.client.get_command_by_name("lfg edit").mention()} - Edit parts of an event
{custom_emojis.enter} {ctx.client.get_command_by_name("lfg delete").mention()} - Remove the event
{custom_emojis.enter} {ctx.client.get_command_by_name("lfg add").mention()} - Add a user to your own event
{custom_emojis.enter} {ctx.client.get_command_by_name("lfg kick").mention()} - Kick a user from your own event
{custom_emojis.enter} {ctx.client.get_command_by_name("lfg share").mention()} - Share the event to a different channel
{custom_emojis.enter} {ctx.client.get_command_by_name("lfg alert").mention()} - Message all members in an event
{custom_emojis.enter} {ctx.client.get_command_by_name("lfg joined").mention()} - Shows you your joined events
"""
                ),
            )

            # pin it
            await post.pin(reason=reason)

        except Forbidden:
            await ctx.send(
                embed=embed_message(
                    "Error",
                    "I do not have the permissions to initialise this channel, please check that I am allowed to do that and try again",
                ),
                ephemeral=True,
            )
            return

        success_message = f"Future LFG events will be posted in {channel.mention}. \nPlease make sure members to do not have the ability to create posts and send messages since that stops me from sorting the events correctly."
        await handle_setup_command(
            ctx=ctx,
            message_name="lfg_channel",
            success_message=success_message,
            channel=channel,
            send_message=False,
        )


def setup(client):
    LfgChannel(client)
