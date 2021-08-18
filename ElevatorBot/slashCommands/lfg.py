import asyncio
import datetime

import dateutil
import pytz
from discord.ext import commands
from discord_slash import cog_ext, SlashContext, ButtonStyle, ComponentContext
from discord_slash.utils import manage_components
from discord_slash.utils.manage_commands import create_option, create_choice

from ElevatorBot.database.database import (
    add_lfg_blacklisted_member,
    remove_lfg_blacklisted_member,
)
from ElevatorBot.functions.formating import embed_message
from ElevatorBot.functions.lfg import create_lfg_message, get_lfg_message
from ElevatorBot.static.slashCommandOptions import options_user


timezones_dict = {
    "GMT / UTC": "UTC",
    "Central Europe": "Europe/Berlin",
    "Eastern Europe": "Europe/Tallinn",
    "Moscow / Turkey": "Europe/Moscow",
    "Central US": "US/Central",
    "Eastern US": "US/Eastern",
    "Pacific US": "US/Pacific",
}


class LfgCommands(commands.Cog):
    timeout_embed = embed_message(
        "Error - Time Is Money",
        "You took too long. If you weren't finished, please try again. \nI can give you my grandmas phone number, her doing the typing might make it a bit faster 🙃",
    )

    def __init__(self, client):
        self.client = client

    @cog_ext.cog_subcommand(
        base="lfg",
        base_description="Everything concerning my awesome Destiny 2 LFG system",
        name="insert",
        description="Creates an LFG post",
        options=[
            create_option(
                name="start_time",
                description="Format: 'HH:MM DD/MM' - When the event is supposed to start",
                option_type=3,
                required=True,
            ),
            create_option(
                name="timezone",
                description="What timezone you are in",
                option_type=3,
                required=True,
                choices=[
                    create_choice(
                        name=timezone_name,
                        value=timezone_value,
                    )
                    for timezone_name, timezone_value in timezones_dict.items()
                ],
            ),
            create_option(
                name="overwrite_max_members",
                description="You can overwrite the maximum number of people that can join your event",
                option_type=3,
                required=False,
            ),
        ],
    )
    async def _create(
        self, ctx: SlashContext, start_time, timezone, overwrite_max_members=None
    ):
        # get start time
        try:
            start_time = dateutil.parser.parse(start_time, dayfirst=True)
        except dateutil.parser.ParserError:
            await ctx.send(
                hidden=True,
                embed=embed_message(
                    "Error",
                    "There was an error with the formatting of the time parameters. Please try again",
                ),
            )
            return
        tz = pytz.timezone(timezone)
        start_time = tz.localize(start_time)

        # make sure thats in the future
        if start_time < datetime.datetime.now(datetime.timezone.utc):
            await ctx.send(
                hidden=True,
                embed=embed_message(
                    "Error", "The event cannot start in the past. Please try again"
                ),
            )
            return

        activity = "Easter Egg Search"
        max_joined_members = 69

        # might take a sec
        await ctx.defer()

        # ask for the activity
        components = [
            manage_components.create_actionrow(
                manage_components.create_button(style=ButtonStyle.blue, label="Raids"),
                manage_components.create_button(
                    style=ButtonStyle.blue, label="Dungeons"
                ),
                manage_components.create_button(style=ButtonStyle.blue, label="Trials"),
                manage_components.create_button(
                    style=ButtonStyle.blue, label="Iron Banner"
                ),
                manage_components.create_button(style=ButtonStyle.blue, label="Other"),
            ),
        ]
        embed = embed_message(
            "Please Select the Activity",
        )

        message = await ctx.send(components=components, embed=embed)

        # wait 60s for button press
        try:
            button_ctx: ComponentContext = await manage_components.wait_for_component(
                ctx.bot, components=components, timeout=60
            )
        except asyncio.TimeoutError:
            await message.edit(components=None, embed=self.timeout_embed)
            return
        else:
            # Raids
            if button_ctx.component["label"] == "Raids":
                components = manage_components.spread_to_rows(
                    manage_components.create_button(
                        style=ButtonStyle.blue, label="Last Wish"
                    ),
                    manage_components.create_button(
                        style=ButtonStyle.blue, label="Garden of Salvation"
                    ),
                    manage_components.create_button(
                        style=ButtonStyle.blue, label="Deep Stone Crypt"
                    ),
                    manage_components.create_button(
                        style=ButtonStyle.blue, label="Vault of Glass"
                    ),
                )
                embed = embed_message(
                    "Please Select the Raid",
                )

                await button_ctx.edit_origin(components=components, embed=embed)

                # wait 60s for button press
                try:
                    button_ctx: ComponentContext = (
                        await manage_components.wait_for_component(
                            ctx.bot, components=components, timeout=60
                        )
                    )
                except asyncio.TimeoutError:
                    await message.edit(components=None, embed=self.timeout_embed)
                    return
                else:
                    await button_ctx.edit_origin(embed=embed)
                    activity = button_ctx.component["label"]
                    max_joined_members = 6

            # Dungeons
            elif button_ctx.component["label"] == "Dungeons":
                components = [
                    manage_components.create_actionrow(
                        manage_components.create_button(
                            style=ButtonStyle.blue, label="Shattered Throne"
                        ),
                        manage_components.create_button(
                            style=ButtonStyle.blue, label="Pit of Hersey"
                        ),
                        manage_components.create_button(
                            style=ButtonStyle.blue, label="Prophecy"
                        ),
                    ),
                ]
                embed = embed_message(
                    "Please Select the Dungeon",
                )

                await button_ctx.edit_origin(components=components, embed=embed)

                # wait 60s for button press
                try:
                    button_ctx: ComponentContext = (
                        await manage_components.wait_for_component(
                            ctx.bot, components=components, timeout=60
                        )
                    )
                except asyncio.TimeoutError:
                    await message.edit(embed=self.timeout_embed)
                    return
                else:
                    await button_ctx.edit_origin(embed=embed)
                    activity = button_ctx.component["label"]
                    max_joined_members = 3

            # Trials
            elif button_ctx.component["label"] == "Trials":
                await button_ctx.edit_origin(embed=embed)
                activity = button_ctx.component["label"]
                max_joined_members = 3

            # Iron Banner
            elif button_ctx.component["label"] == "Iron Banner":
                await button_ctx.edit_origin(embed=embed)
                activity = button_ctx.component["label"]
                max_joined_members = 6

            # Other
            elif button_ctx.component["label"] == "Other":
                await button_ctx.edit_origin(
                    components=None,
                    embed=embed_message("Activity Name", "Please enter a name"),
                )

                # wait 60s for message
                def check(answer_msg):
                    return (
                        answer_msg.author == ctx.author
                        and answer_msg.channel == message.channel
                    )

                try:
                    answer_msg = await self.client.wait_for(
                        "message", timeout=60.0, check=check
                    )
                except asyncio.TimeoutError:
                    await message.edit(embed=self.timeout_embed)
                    return
                else:
                    activity = answer_msg.content
                    max_joined_members = 12

                    await answer_msg.delete()

        # do the max_joined_members overwrite if asked for
        if overwrite_max_members:
            max_joined_members = int(overwrite_max_members)

        # get the description
        await message.edit(
            components=None,
            embed=embed_message("Description", "Please enter a description"),
        )

        # wait 60s for message
        def check(answer_msg):
            return (
                answer_msg.author == ctx.author
                and answer_msg.channel == message.channel
            )

        try:
            answer_msg = await self.client.wait_for(
                "message", timeout=60.0, check=check
            )
        except asyncio.TimeoutError:
            await message.edit(embed=self.timeout_embed)
            return
        else:
            description = answer_msg.content
            await answer_msg.delete()

        # insert and post the lfg message
        await create_lfg_message(
            ctx.bot,
            ctx.guild,
            ctx.author,
            activity,
            description,
            start_time,
            max_joined_members,
        )

        await message.edit(embed=embed_message(f"Success", f"I've created the post"))

    @cog_ext.cog_subcommand(
        base="lfg",
        base_description="Everything concerning my awesome Destiny 2 LFG system",
        name="edit",
        description="When you fucked up and need to edit an event",
        options=[
            create_option(
                name="lfg_id",
                description="The lfg message id",
                option_type=4,
                required=True,
            ),
            create_option(
                name="section",
                description="What section to edit",
                option_type=3,
                required=True,
                choices=[
                    create_choice(name="Activity", value="Activity"),
                    create_choice(name="Description", value="Description"),
                    create_choice(name="Start Time", value="Start Time"),
                    create_choice(name="Maximum Members", value="Maximum Members"),
                ],
            ),
        ],
    )
    async def _edit(self, ctx: SlashContext, lfg_id, section):
        # get the message obj
        lfg_message = await get_lfg_message(ctx.bot, lfg_id, ctx)
        if not lfg_message:
            return

        # might take a sec
        await ctx.defer()

        def check(answer_msg):
            return answer_msg.author == ctx.author and answer_msg.channel == ctx.channel

        if section == "Activity":
            message = await ctx.send(
                embed=embed_message("Activity Name", "Please enter a new name")
            )

            # wait 60s for message
            try:
                answer_msg = await self.client.wait_for(
                    "message", timeout=60.0, check=check
                )
            except asyncio.TimeoutError:
                await message.edit(embed=self.timeout_embed)
                return
            else:
                # edit the message
                lfg_message.activity = answer_msg.content

                # delete old msgs
                await answer_msg.delete()

        elif section == "Description":
            message = await ctx.send(
                embed=embed_message("Description", "Please enter a new description")
            )

            # wait 60s for message
            try:
                answer_msg = await self.client.wait_for(
                    "message", timeout=60.0, check=check
                )
            except asyncio.TimeoutError:
                await message.edit(embed=self.timeout_embed)
                return
            else:
                # edit the message and resend
                lfg_message.description = answer_msg.content

                # delete old msgs
                await answer_msg.delete()

        elif section == "Start Time":
            message = await ctx.send(
                embed=embed_message(
                    "Start Time",
                    "Please enter a new start time like this \n`HH:MM DD/MM`",
                )
            )

            # wait 60s for message
            try:
                answer_msg = await self.client.wait_for(
                    "message", timeout=60.0, check=check
                )
            except asyncio.TimeoutError:
                await message.edit(embed=self.timeout_embed)
                return
            else:
                # get the datetime
                try:
                    start_time = dateutil.parser.parse(
                        answer_msg.content, dayfirst=True
                    )
                except dateutil.parser.ParserError:
                    await message.edit(
                        embed=embed_message(
                            "Error",
                            "There was an error with the formatting of the time parameters, please try again",
                        )
                    )
                    await answer_msg.delete()
                    return
                await answer_msg.delete()

                # ask for the timezone
                components = [
                    manage_components.create_actionrow(
                        manage_components.create_select(
                            options=[
                                manage_components.create_select_option(
                                    emoji="🕑",
                                    label=timezone_name,
                                    value=timezone_value,
                                )
                                # Options for timezones
                                for timezone_name, timezone_value in timezones_dict.items()
                            ],
                            placeholder="Select timezone here",
                            min_values=1,
                            max_values=1,
                        )
                    ),
                ]
                embed = embed_message(
                    "Please Select the Timezone",
                )

                await message.edit(components=components, embed=embed)

                # wait 60s for selection
                def check(select_ctx: ComponentContext):
                    return select_ctx.author == ctx.author

                try:
                    select_ctx: ComponentContext = (
                        await manage_components.wait_for_component(
                            ctx.bot, components=components, timeout=60, check=check
                        )
                    )
                except asyncio.TimeoutError:
                    await message.edit(embed=self.timeout_embed)
                    return
                else:
                    selected = select_ctx.selected_options[0]

                    # localize to that timezone
                    tz = pytz.timezone(selected)
                    start_time = tz.localize(start_time)

                    # make sure thats in the future
                    if start_time < datetime.datetime.now(datetime.timezone.utc):
                        await select_ctx.edit_origin(
                            components=None,
                            embed=embed_message(
                                "Error",
                                "The event cannot start in the past. Please try again",
                            ),
                        )
                        return

                    # edit the message
                    await lfg_message.edit_start_time_and_send(start_time)
                    await select_ctx.edit_origin(
                        components=None,
                        embed=embed_message(f"Success", f"I've edited the post"),
                    )
                    return

        else:  # section == "Maximum Members":
            message = await ctx.send(
                embed=embed_message(
                    "Maximum Members", "Please enter the new maximum members"
                )
            )

            # wait 60s for message
            try:
                answer_msg = await self.client.wait_for(
                    "message", timeout=60.0, check=check
                )
            except asyncio.TimeoutError:
                await message.edit(embed=self.timeout_embed)
                return
            else:
                # edit the message
                try:
                    lfg_message.max_joined_members = int(answer_msg.content)
                except ValueError:
                    await message.edit(
                        embed=embed_message(
                            "Error",
                            f"`{answer_msg.content}` is not a number. Please try again",
                        )
                    )
                    await answer_msg.delete()
                    return

                # delete old msgs
                await answer_msg.delete()

        # resend msg
        await lfg_message.send()

        await message.edit(embed=embed_message(f"Success", f"I've edited the post"))

    @cog_ext.cog_subcommand(
        base="lfg",
        base_description="Everything concerning my awesome Destiny 2 LFG system",
        name="delete",
        description="When you fucked up and need to delete an event",
        options=[
            create_option(
                name="lfg_id",
                description="The lfg message id",
                option_type=4,
                required=True,
            ),
        ],
    )
    async def _remove(self, ctx: SlashContext, lfg_id):
        # get the message obj
        lfg_message = await get_lfg_message(ctx.bot, lfg_id, ctx)
        if not lfg_message:
            return

        await lfg_message.delete()
        await ctx.send(
            hidden=True,
            embed=embed_message(
                "Success", f"The LFG post with the id `{lfg_id}` has been deleted"
            ),
        )

    @cog_ext.cog_subcommand(
        base="lfg",
        base_description="Everything concerning my awesome Destiny 2 LFG system",
        name="add",
        description="Add a user to an lfg event",
        options=[
            create_option(
                name="lfg_id",
                description="The lfg message id",
                option_type=4,
                required=True,
            ),
            options_user(flavor_text="The user you want to add", required=True),
        ],
    )
    async def _add(self, ctx: SlashContext, lfg_id, user):
        # get the message obj
        lfg_message = await get_lfg_message(ctx.bot, lfg_id, ctx)
        if not lfg_message:
            return

        if await lfg_message.add_member(user, force_into_joined=True):
            await ctx.send(
                hidden=True,
                embed=embed_message(
                    "Success",
                    f"{user.display_name} has been added to the LFG post with the id `{lfg_id}`",
                ),
            )
        else:
            await ctx.send(
                hidden=True,
                embed=embed_message(
                    "Error",
                    f"{user.display_name} could not be added to the LFG post with the id `{lfg_id}`, because they are already in it or they are blacklisted by the creator",
                ),
            )

    @cog_ext.cog_subcommand(
        base="lfg",
        base_description="Everything concerning my awesome Destiny 2 LFG system",
        name="kick",
        description="Kick a user from an lfg event",
        options=[
            create_option(
                name="lfg_id",
                description="The lfg message id",
                option_type=4,
                required=True,
            ),
            options_user(flavor_text="The user you want to add", required=True),
        ],
    )
    async def _kick(self, ctx: SlashContext, lfg_id, user):
        # get the message obj
        lfg_message = await get_lfg_message(ctx.bot, lfg_id, ctx)
        if not lfg_message:
            return

        if await lfg_message.remove_member(user):
            await ctx.send(
                hidden=True,
                embed=embed_message(
                    "Success",
                    f"{user.display_name} has been removed from the LFG post with the id `{lfg_id}`",
                ),
            )
        else:
            await ctx.send(
                hidden=True,
                embed=embed_message(
                    "Error",
                    f"{user.display_name} could not be delete from the LFG post with the id `{lfg_id}`, because they are not in it",
                ),
            )

    @cog_ext.cog_subcommand(
        base="lfg",
        base_description="Everything concerning my awesome Destiny 2 LFG system",
        name="blacklist",
        description="(Un-) Blacklist a user from your own lfg event",
        options=[
            create_option(
                name="action",
                description="If you want to add to or delete from the Blacklist",
                option_type=3,
                required=True,
                choices=[
                    create_choice(name="Blacklist", value="Blacklist"),
                    create_choice(name="Un-Blacklist", value="Un-Blacklist"),
                ],
            ),
            options_user(
                flavor_text="The user you want to add / delete", required=True
            ),
        ],
    )
    async def _blacklist(self, ctx: SlashContext, action, user):
        if action == "Blacklist":
            if ctx.author == user:
                await ctx.send(
                    hidden=True,
                    embed=embed_message(
                        "Error",
                        f"Mate, you cannot blacklist yourself. That is just stupid",
                    ),
                )
                return

            await add_lfg_blacklisted_member(ctx.author.id, user.id)
            await ctx.send(
                hidden=True,
                embed=embed_message(
                    "Success",
                    f"{user.display_name} has been added to your personal blacklist and will not be able to join your events",
                ),
            )

        elif action == "Un-Blacklist":
            await remove_lfg_blacklisted_member(ctx.author.id, user.id)
            await ctx.send(
                hidden=True,
                embed=embed_message(
                    "Success",
                    f"{user.display_name} has been removed from your personal blacklist and will be able to join your events again",
                ),
            )


def setup(client):
    client.add_cog(LfgCommands(client))
