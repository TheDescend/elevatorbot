from dis_snek import ChannelTypes, GuildChannel, InteractionContext, OptionTypes, slash_command, slash_option

from ElevatorBot.commandHelpers.subCommandTemplates import setup_sub_command, setup_sub_command_lfg_group
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.misc.persistentMessages import handle_setup_command
from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.static.emojis import custom_emojis


class LfgChannel(BaseScale):

    # todo perms
    @slash_command(
        **setup_sub_command,
        **setup_sub_command_lfg_group,
        sub_cmd_name="channel",
        sub_cmd_description="Designate a channel where my LFG events get posted",
    )
    @slash_option(
        name="channel",
        description="The text channel where the message should be displayed",
        required=True,
        opt_type=OptionTypes.CHANNEL,
        channel_types=[ChannelTypes.GUILD_TEXT],
    )
    async def channel(self, ctx: InteractionContext, channel: GuildChannel):
        if ctx.author.id != 238388130581839872:
            await ctx.send(
                "This is blocked for now, since it it waiting for a vital unreleased discord feature", ephemeral=True
            )
            return

        embed = embed_message(
            "How to make an LFG post",
            f"""
Hello fellow humans, and welcome to this easy, 465 steps, guide:
⁣
{custom_emojis.circle} **Step 1:**
First, head to your local bot spam channel, or really any other channel (although you ~~might~~ will get yelled at for that).
⁣
{custom_emojis.circle} **Step 2:**
Then, use `/lfg create` and follow the instructions to make an event.
Due to timezones sucking and there being at least 16789 of them, you might not find your own timezone in the list. In that case please use UTC and an online converter.
⁣
{custom_emojis.circle} **Step 3-464:**
`for i in range(3, 464): print(f"praise {{self.mention}}!")`
⁣
{custom_emojis.circle} **Step 465:**
After you made the LFG post, or if you just want to join an existing post, use the fancy buttons to interact with the event.
⁣
⁣
If you want to feel like an [expert](https://www.youtube.com/watch?v=BKorP55Aqvg), there are a bunch of additional commands you can use to interact with LFG events:
{custom_emojis.enter} `/lfg create` - Create a new LFG event
{custom_emojis.enter} `/lfg edit` - Edit parts of an LFG event
{custom_emojis.enter} `/lfg delete` - Remove the LFG event
{custom_emojis.enter} `/lfg add` - Add a user to your own LFG event
{custom_emojis.enter} `/lfg kick` - Kick a user from your own LFG event
{custom_emojis.enter} `/lfg alert` - Message all members in an event
{custom_emojis.enter} `/lfg joined` - Shows you an overview which LFG events you have joined
⁣
⁣
Basically just type `/lfg` and look around. There are many other cool commands too, so maybe just type `/`.""",
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
