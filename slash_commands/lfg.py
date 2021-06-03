import asyncio
import datetime
import dateutil
import pytz
from discord.ext import commands
from discord_components import Button, ButtonStyle
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice

from database.database import add_lfg_blacklisted_member, remove_lfg_blacklisted_member
from functions.formating import embed_message
from functions.lfg import create_lfg_message, get_lfg_message
from static.config import GUILD_IDS
from static.globals import join_emoji_id, leave_emoji_id, backup_emoji_id
from static.slashCommandOptions import options_user


class LfgCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.timeout_embed = embed_message(
            "Error",
            "I AM IMPATIENT. PLEASE BE QUICKER NEXT TIME. THANKS"
        )


    @cog_ext.cog_subcommand(
        base="lfg",
        base_description="Everything concerning my awesome Destiny 2 LFG system",
        name="create",
        description="Creates an LFG post",
        options=[
            create_option(
                name="time",
                description="Format: 'HH:MM' - When the event is supposed to start",
                option_type=3,
                required=True,
            ),
            create_option(
                name="date",
                description="Format: 'DD/MM' - When the event is supposed to start",
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
                        name="GMT / UTC",
                        value="UTC"
                    ),
                    create_choice(
                        name="Central Europe",
                        value='Europe/Berlin'
                    ),
                    create_choice(
                        name="Eastern Europe",
                        value='Europe/Tallinn'
                    ),
                    create_choice(
                        name="Moscow / Turkey",
                        value='Europe/Moscow'
                    ),
                    create_choice(
                        name="Central US",
                        value='US/Central'
                    ),
                    create_choice(
                        name="Eastern US",
                        value='US/Eastern'
                    ),
                    create_choice(
                        name="Pacific US",
                        value='US/Pacific'
                    ),
                ]
            ),
            create_option(
                name="overwrite_max_members",
                description="You can overwrite the maximum number of people that can join your event",
                option_type=3,
                required=False,
            ),
        ],
    )
    async def _create(self, ctx: SlashContext, time, date, timezone, overwrite_max_members=None):
        # get start time
        try:
            start_time = dateutil.parser.parse(f"{time} {date}/{datetime.datetime.now().year}", dayfirst=True)
        except dateutil.parser.ParserError:
            await ctx.send(hidden=True, embed=embed_message(
                "Error",
                "There was an error with the formatting of the time parameters. Please try again"
            ))
            return
        tz = pytz.timezone(timezone)
        start_time = pytz.utc.localize(start_time).astimezone(tz)

        # make sure thats in the future
        if start_time < datetime.datetime.now(datetime.timezone.utc):
            await ctx.send(hidden=True, embed=embed_message(
                "Error",
                "The event cannot start in the past. Please try again"
            ))
            return

        activity = "Easter Egg Search"
        max_joined_members = 69

        # might take a sec
        await ctx.defer()

        # ask for the activity
        message = await ctx.send(embed=embed_message(
            "Please Select the Activity",
            "\n".join(["1️⃣ Raids", "2️⃣ Dungeons", "3️⃣ Trials", "4️⃣ Iron Banner", "5️⃣ Other"])
        ))
        reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
        for reaction in reactions:
            await message.add_reaction(reaction)

        # wait 60s for reaction
        def check(reaction_reaction, reaction_user):
            return (str(reaction_reaction.emoji) in reactions) \
                   and (reaction_reaction.message.id == message.id) \
                   and (ctx.author == reaction_user)
        try:
            reaction, _ = await self.client.wait_for('reaction_add', check=check, timeout=60)
        except asyncio.TimeoutError:
            await message.edit(embed=self.timeout_embed)
            return
        else:
            # Raids
            if str(reaction) == "1️⃣":
                await message.clear_reactions()
                await message.edit(embed=embed_message(
                    "Please Select the Raid",
                    "\n".join(["1️⃣ Last Wish", "2️⃣ Garden of Salvation", "3️⃣ Deep Stone Crypt", "4️⃣ Vault of Glass"])
                ))
                reactions2 = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
                for reaction in reactions2:
                    await message.add_reaction(reaction)

                # wait 60s for reaction
                def check(reaction_reaction, reaction_user):
                    return (str(reaction_reaction.emoji) in reactions2) \
                           and (reaction_reaction.message.id == message.id) \
                           and (ctx.author == reaction_user)

                try:
                    reaction2, _ = await self.client.wait_for('reaction_add', check=check, timeout=60)
                except asyncio.TimeoutError:
                    await message.edit(embed=self.timeout_embed)
                    return
                else:
                    # lw
                    if str(reaction2) == "1️⃣":
                        activity = "Last Wish"
                        max_joined_members = 6

                    # gos
                    elif str(reaction2) == "2️⃣":
                        activity = "Garden of Salvation"
                        max_joined_members = 6

                    # dsc
                    elif str(reaction2) == "3️⃣":
                        activity = "Deep Stone Crypt"
                        max_joined_members = 6

                    # vog
                    elif str(reaction2) == "4️⃣":
                        activity = "Vault of Glass"
                        max_joined_members = 6

            # Dungeons
            elif str(reaction) == "2️⃣":
                await message.clear_reactions()
                await message.edit(embed=embed_message(
                    "Please Select the Dungeon",
                    "\n".join(
                        ["1️⃣ Shattered Throne", "2️⃣ Pit of Hersey", "3️⃣ Prophecy"])
                ))
                reactions2 = ["1️⃣", "2️⃣", "3️⃣"]
                for reaction in reactions2:
                    await message.add_reaction(reaction)

                # wait 60s for reaction
                def check(reaction_reaction, reaction_user):
                    return (str(reaction_reaction.emoji) in reactions2) \
                           and (reaction_reaction.message.id == message.id) \
                           and (ctx.author == reaction_user)

                try:
                    reaction2, _ = await self.client.wait_for('reaction_add', check=check, timeout=60)
                except asyncio.TimeoutError:
                    await message.edit(embed=self.timeout_embed)
                    return
                else:
                    # st
                    if str(reaction2) == "1️⃣":
                        activity = "Last Wish"
                        max_joined_members = 3

                    # pit
                    elif str(reaction2) == "2️⃣":
                        activity = "Pit of Hersey"
                        max_joined_members = 3

                    # proph
                    elif str(reaction2) == "3️⃣":
                        activity = "Prophecy"
                        max_joined_members = 3

            # Trials
            elif str(reaction) == "3️⃣":
                activity = "Trials"
                max_joined_members = 3

            # Iron Banner
            elif str(reaction) == "4️⃣":
                activity = "Iron Banner"
                max_joined_members = 6

            # Other
            elif str(reaction) == "5️⃣":
                await message.clear_reactions()
                await message.edit(embed=embed_message(
                    "Activity Name",
                    "Please enter a name"
                ))

                # wait 60s for message
                def check(answer_msg):
                    return answer_msg.author == ctx.author and answer_msg.channel == message.channel

                try:
                    answer_msg = await self.client.wait_for('message', timeout=60.0, check=check)
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
        await message.clear_reactions()
        await message.edit(embed=embed_message(
            "Description",
            "Please enter a description"
        ))

        # wait 60s for message
        def check(answer_msg):
            return answer_msg.author == ctx.author and answer_msg.channel == message.channel

        try:
            answer_msg = await self.client.wait_for('message', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await message.edit(embed=self.timeout_embed)
            return
        else:
            description = answer_msg.content
            await answer_msg.delete()

        # delete message
        await message.delete()

        # create and post the lfg message
        await create_lfg_message(ctx.bot, ctx.guild, ctx.author, activity, description, start_time, max_joined_members)


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
                    create_choice(
                        name="Activity",
                        value="Activity"
                    ),
                    create_choice(
                        name="Description",
                        value="Description"
                    ),
                    create_choice(
                        name="Start Time",
                        value="Start Time"
                    ),
                    create_choice(
                        name="Maximum Members",
                        value="Maximum Members"
                    ),
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
            message = await ctx.send(embed=embed_message(
                "Activity Name",
                "Please enter a new name"
            ))

            # wait 60s for message
            try:
                answer_msg = await self.client.wait_for('message', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await message.edit(embed=self.timeout_embed)
                return
            else:
                # edit the message
                lfg_message.activity = answer_msg.content

                # delete old msgs
                await message.delete()
                await answer_msg.delete()

        elif section == "Description":
            message = await ctx.send(embed=embed_message(
                "Description",
                "Please enter a new description"
            ))

            # wait 60s for message
            try:
                answer_msg = await self.client.wait_for('message', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await message.edit(embed=self.timeout_embed)
                return
            else:
                # edit the message and resend
                lfg_message.description = answer_msg.content

                # delete old msgs
                await message.delete()
                await answer_msg.delete()

        elif section == "Start Time":
            message = await ctx.send(embed=embed_message(
                "Start Time",
                "Please enter a new start time like this \n`HH:MM DD/MM`"
            ))

            # wait 60s for message
            try:
                answer_msg = await self.client.wait_for('message', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await message.edit(embed=self.timeout_embed)
                return
            else:
                # get the datetime
                try:
                    start_time = dateutil.parser.parse(f"{answer_msg.content}/{datetime.datetime.now().year}", dayfirst=True)
                except dateutil.parser.ParserError:
                    await message.edit(embed=embed_message(
                        "Error",
                        "There was an error with the formatting of the time parameters, please try again"
                    ))
                    await answer_msg.delete()
                    return
                await answer_msg.delete()

                # ask for the timezone
                await message.edit(embed=embed_message(
                    "Please Select your Timezone",
                    "\n".join(["1️⃣ GMT / UTC", "2️⃣ Central Europe", "3️⃣ Eastern Europe", "4️⃣ Moscow / Turkey", "5️⃣ Central US", "6️⃣ Eastern US", "7️⃣ Pacific US"])
                ))
                reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣"]
                for reaction in reactions:
                    await message.add_reaction(reaction)

                # wait 60s for reaction
                def check(reaction_reaction, reaction_user):
                    return (str(reaction_reaction.emoji) in reactions) \
                           and (reaction_reaction.message.id == message.id) \
                           and (ctx.author == reaction_user)

                try:
                    reaction, _ = await self.client.wait_for('reaction_add', check=check, timeout=60)
                except asyncio.TimeoutError:
                    await message.edit(embed=self.timeout_embed)
                    return
                else:
                    if str(reaction) == "1️⃣":
                        tz = pytz.timezone("UTC")
                        start_time = start_time.astimezone(tz)
                    elif str(reaction) == "2️⃣":
                        tz = pytz.timezone("Europe/Berlin")
                        start_time = start_time.astimezone(tz)
                    elif str(reaction) == "3️⃣":
                        tz = pytz.timezone("Europe/Tallinn")
                        start_time = start_time.astimezone(tz)
                    elif str(reaction) == "4️⃣":
                        tz = pytz.timezone("Europe/Moscow")
                        start_time = start_time.astimezone(tz)
                    elif str(reaction) == "5️⃣":
                        tz = pytz.timezone("US/Central")
                        start_time = start_time.astimezone(tz)
                    elif str(reaction) == "6️⃣":
                        tz = pytz.timezone("US/Eastern")
                        start_time = start_time.astimezone(tz)
                    elif str(reaction) == "7️⃣":
                        tz = pytz.timezone("US/Pacific")
                        start_time = start_time.astimezone(tz)

                    # make sure thats in the future
                    if start_time < datetime.datetime.now(datetime.timezone.utc):
                        await message.clear_reactions()
                        await message.edit(embed=embed_message(
                            "Error",
                            "The event cannot start in the past. Please try again"
                        ))
                        return

                # edit the message
                lfg_message.edit_start_time(start_time)

                # delete old msgs
                await message.delete()

        if section == "Maximum Members":
            message = await ctx.send(embed=embed_message(
                "Maximum Members",
                "Please enter the new maximum members"
            ))

            # wait 60s for message
            try:
                answer_msg = await self.client.wait_for('message', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await message.edit(embed=self.timeout_embed)
                return
            else:
                # edit the message
                try:
                    lfg_message.max_joined_members = int(answer_msg.content)
                except ValueError:
                    await message.edit(embed=embed_message(
                        "Error",
                        f"`{answer_msg.content}` is not a number. Please try again"
                    ))
                    await answer_msg.delete()
                    return

                # delete old msgs
                await message.delete()
                await answer_msg.delete()

        # resend msg
        await lfg_message.send()


    @cog_ext.cog_subcommand(
        base="lfg",
        base_description="Everything concerning my awesome Destiny 2 LFG system",
        name="remove",
        description="When you fucked up and need to remove an event",
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
        await ctx.send(hidden=True, embed=embed_message(
            "Success",
            f"The LFG post with the id `{lfg_id}` has been deleted"
        ))


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
            options_user(flavor_text="The user you want to add", required=True)
        ],
    )
    async def _add(self, ctx: SlashContext, lfg_id, user):
        # get the message obj
        lfg_message = await get_lfg_message(ctx.bot, lfg_id, ctx)
        if not lfg_message:
            return

        if await lfg_message.add_member(user):
            await ctx.send(hidden=True, embed=embed_message(
                "Success",
                f"{user.display_name} has been added to the LFG post with the id `{lfg_id}`"
            ))
        else:
            await ctx.send(hidden=True, embed=embed_message(
                "Error",
                f"{user.display_name} could not be added to the LFG post with the id `{lfg_id}`, because they are already in it or they are blacklisted by the creator"
            ))


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
            options_user(flavor_text="The user you want to add", required=True)
        ],
    )
    async def _kick(self, ctx: SlashContext, lfg_id, user):
        # get the message obj
        lfg_message = await get_lfg_message(ctx.bot, lfg_id, ctx)
        if not lfg_message:
            return

        if await lfg_message.remove_member(user):
            await ctx.send(hidden=True, embed=embed_message(
                "Success",
                f"{user.display_name} has been removed from the LFG post with the id `{lfg_id}`"
            ))
        else:
            await ctx.send(hidden=True, embed=embed_message(
                "Error",
                f"{user.display_name} could not be remove from the LFG post with the id `{lfg_id}`, because they are not in it"
            ))


    @cog_ext.cog_subcommand(
        base="lfg",
        base_description="Everything concerning my awesome Destiny 2 LFG system",
        name="blacklist",
        description="(Un-) Blacklist a user from your own lfg event",
        options=[
            create_option(
                name="action",
                description="If you want to add to or remove from the Blacklist",
                option_type=3,
                required=True,
                choices=[
                    create_choice(
                        name="Blacklist",
                        value="Blacklist"
                    ),
                    create_choice(
                        name="Un-Blacklist",
                        value="Un-Blacklist"
                    ),
                ]
            ),
            options_user(flavor_text="The user you want to add / remove", required=True)
        ],
    )
    async def _blacklist(self, ctx: SlashContext, action, user):
        if action == "Blacklist":
            if ctx.author == user:
                await ctx.send(hidden=True, embed=embed_message(
                    "Error",
                    f"Mate, you cannot blacklist yourself. That is just stupid"
                ))
                return

            await add_lfg_blacklisted_member(ctx.author.id, user.id)
            await ctx.send(hidden=True, embed=embed_message(
                "Success",
                f"{user.display_name} has been added to your personal blacklist and will not be able to join your events"
            ))

        elif action == "Un-Blacklist":
            await remove_lfg_blacklisted_member(ctx.author.id, user.id)
            await ctx.send(hidden=True, embed=embed_message(
                "Success",
                f"{user.display_name} has been removed from your personal blacklist and will be able to join your events again"
            ))


def setup(client):
    client.add_cog(LfgCommands(client))
