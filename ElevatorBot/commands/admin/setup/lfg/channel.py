from dis_snek.models import (
    GuildChannel,
    GuildText,
    InteractionContext,
    OptionTypes,
    slash_option,
    sub_command,
)

from ElevatorBot.commandHelpers.responseTemplates import respond_wrong_channel_type
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.misc.persistentMessages import handle_setup_command
from ElevatorBot.misc.formating import embed_message
from ElevatorBot.static.emojis import custom_emojis


class LfgChannel(BaseScale):

    # todo perms
    @sub_command(
        base_name="setup",
        base_description="Use these commands to setup ElevatorBot on this server",
        group_name="lfg",
        group_description="Everything needed to use my LFG system",
        sub_name="channel",
        sub_description="The channel in which the LFG messages get posted",
    )
    @slash_option(
        name="channel",
        description="The text channel where the message should be displayed",
        required=True,
        opt_type=OptionTypes.CHANNEL,
    )
    async def _channel(self, ctx: InteractionContext, channel: GuildChannel):
        # make sure the channel is a text channel
        if not isinstance(channel, GuildText):
            await respond_wrong_channel_type(ctx=ctx)
            return

        # todo add additional lfg commands to list
        embed = embed_message(
            "How to make an LFG post",
            f"""
Hello fellow humans, and welcome to this easy, 465 steps, guide:
⁣
{custom_emojis.circle} **Step 1:**
First, head to your local bot spam channel, or really any other channel (although you ~~might~~ will get yelled at for that)
⁣
{custom_emojis.circle} **Step 2:**
Then, use `/lfg insert` and follow the instructions to make an event.
Due to timezones sucking and there being at least 16789 of them, you might not find your own timezone in the list. In that case please use
UTC and an online converter
⁣
{custom_emojis.circle} **Step 3-464:**
Praise {ctx.bot.user.mention}!
⁣
{custom_emojis.circle} **Step 465:**
After you made the LFG post, or if you just want to join an existing post, use the fancy buttons to interact with the event
⁣
⁣
If you want to feel like an [expert](https://www.youtube.com/watch?v=BKorP55Aqvg), there are a bunch of additional commands you can use to
interact with LFG events:
{custom_emojis.enter} `/lfg insert` - Create a new LFG event
{custom_emojis.enter} `/lfg edit` - Edit parts of an LFG event
{custom_emojis.enter} `/lfg _delete` - Remove the LFG event
{custom_emojis.enter} `/lfg add` - Add a user to your own LFG event
{custom_emojis.enter} `/lfg kick` - Kick a user from your own LFG event
{custom_emojis.enter} `/lfg blacklist` - Blacklist a user from joining any of your own LFG events
⁣
⁣
Basically just type `/lfg` and look around. There are many other cool commands too, so maybe just type `/`""",
        )
        success_message = f"Future LFG posts will be posted in {channel.mention}"
        await handle_setup_command(
            ctx=ctx,
            message_name="lfg_channel",
            success_message=success_message,
            channel=channel,
            send_message=True,
            send_message_embed=embed,
        )


def setup(client):
    LfgChannel(client)
