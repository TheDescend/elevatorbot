import asyncio
import dataclasses
import datetime
from typing import Union

import discord
import pytz
from apscheduler.jobstores.base import JobLookupError
from discord_slash import SlashContext, ComponentContext, ButtonStyle
from discord_slash.utils import manage_components

from ElevatorBot.database.database import get_next_free_lfg_message_id, get_persistent_message, get_lfg_blacklisted_members, \
    insert_lfg_message, select_lfg_message, delete_lfg_message, select_guild_lfg_events
from ElevatorBot.functions.formating import embed_message
from ElevatorBot.functions.miscFunctions import has_elevated_permissions, get_scheduler
from ElevatorBot.functions.persistentMessages import get_persistent_message_or_channel
from ElevatorBot.static.globals import join_emoji_id, leave_emoji_id, backup_emoji_id


@dataclasses.dataclass()
class LfgMessage:
    """ Class to hold an LFG message """

    client: discord.Client
    id: int

    guild: discord.Guild
    channel: discord.TextChannel

    author: discord.Member
    activity: str
    description: str
    start_time: datetime.datetime
    max_joined_members: int
    blacklisted_members: list[int]

    message: discord.Message = None
    voice_channel: discord.VoiceChannel = None
    creation_time: datetime = None
    joined_members: list[discord.Member] = None
    alternate_members: list[discord.Member] = dataclasses.field(default_factory=list)

    utc_start_time: datetime = dataclasses.field(init=False)


    # post init to do list
    def __post_init__(
        self
    ):
        # sets the author as a joined member, if empty otherwise
        if self.joined_members is None:
            self.joined_members = [self.author]

        # gets the starttime as a utc object
        self.utc_start_time = self.start_time.astimezone(pytz.utc)

        # get the scheduler object
        self.scheduler = get_scheduler()

        # get the button emojis
        self._join_emoji = self.client.get_emoji(join_emoji_id)
        self._leave_emoji = self.client.get_emoji(leave_emoji_id)
        self._backup_emoji = self.client.get_emoji(backup_emoji_id)


    # less than operator to sort the classes by their start time
    def __lt__(
        self,
        other
    ):
        return self.start_time < other.start_time


    # edit start time and sort messages again
    async def edit_start_time_and_send(
        self,
        start_time: datetime.datetime
    ):
        self.start_time = start_time
        self.utc_start_time = start_time.astimezone(pytz.utc)

        # send
        await self.send()

        # sort again
        await self.sort_lfg_messages()


    # add a member
    async def add_member(
        self,
        member: discord.Member,
        ctx: ComponentContext = None,
        force_into_joined: bool = False
    ) -> bool:
        if (member not in self.joined_members) and (member.id not in self.blacklisted_members):
            if (len(self.joined_members) < self.max_joined_members) or force_into_joined:
                self.joined_members.append(member)
                if member in self.alternate_members:
                    self.alternate_members.remove(member)
            else:
                if member not in self.alternate_members:
                    self.alternate_members.append(member)
                else:
                    return False

            await self.send(ctx=ctx)
            return True
        return False


    # add a backup or move member to backup
    async def add_backup(
        self,
        member: discord.Member,
        ctx: ComponentContext = None
    ) -> bool:
        if (member not in self.alternate_members) and (member.id not in self.blacklisted_members):
            self.alternate_members.append(member)

            if member in self.joined_members:
                self.joined_members.remove(member)

            await self.send(ctx=ctx)
            return True
        return False


    # remove a member
    async def remove_member(
        self,
        member: discord.Member,
        ctx: ComponentContext = None
    ) -> bool:
        if member in self.joined_members:
            self.joined_members.remove(member)

            await self.send(ctx=ctx)
            return True

        elif member in self.alternate_members:
            self.alternate_members.remove(member)

            await self.send(ctx=ctx)
            return True
        return False


    # notifies joined members that the event is about to start
    async def notify_about_start(
        self,
        time_to_start: datetime.timedelta
    ):
        voice_text = "Please start gathering in a voice channel"

        # get the voice channel category and make a voice channel
        voice_category_channel = await get_persistent_message_or_channel(self.client, "lfgVoiceCategory", self.guild.id)
        if voice_category_channel:
            voice_channel_name = f"[ID: {self.id}] {self.activity}"

            # allow each participant to move members
            permission_overrides = {}
            for member in self.joined_members:
                # allow the author to also mute
                if member == self.author:
                    permission_overrides.update(
                        {
                            member: discord.PermissionOverwrite(
                                move_members=True,
                                mute_members=True,
                            )
                        }
                    )
                else:
                    permission_overrides.update(
                        {
                            member: discord.PermissionOverwrite(
                                move_members=True,
                            )
                        }
                    )

            self.voice_channel = await voice_category_channel.create_voice_channel(
                name=voice_channel_name,
                bitrate=self.guild.bitrate_limit,
                user_limit=self.max_joined_members,
                overwrites=permission_overrides,
                reason="LFG event starting"
            )

            # make fancy text
            voice_text = f"Click here to join the voice channel -> {self.voice_channel.mention}"

        # prepare embed
        embed = embed_message(
            f"LFG Event - {self.activity}",
            f"The LFG event with the ID `{self.id}` is going to start in **{int(time_to_start.seconds / 60)} minutes**\n{voice_text}",
            "Start Time"
        )
        embed.add_field(name="Guardians", value=", ".join(self.get_joined_members_display_names()), inline=False)
        embed.timestamp = self.utc_start_time

        # if the event was not full
        missing = self.max_joined_members - len(self.joined_members)
        if self.alternate_members:
            embed.add_field(name="Backup", value=", ".join(self.get_alternate_members_display_names()), inline=False)

            # dm the backup if they are needed
            if missing > 0:
                for user in self.alternate_members:
                    await user.send(embed=embed)

        # dm the users
        for user in self.joined_members:
            try:
                await user.send(embed=embed)
            except discord.Forbidden:
                pass

        # edit the channel message
        await self.message.edit(embed=embed, components=[])
        await self.dump_to_db()

        # wait timedelta + 10 mins
        await asyncio.sleep(time_to_start.seconds + 60 * 10)

        # remove the post
        await self.delete()


    # sort all the lfg messages in the guild by start_time
    async def sort_lfg_messages(
        self
    ):
        # get all lfg ids
        results = await select_guild_lfg_events(self.guild.id)

        # only continue if there is more than one event
        if len(results) <= 1:
            return

        # create three lists. A list with the current message objs (sorted by asc creation date), a list with the creation_time, and a list with the LfgMessage objs
        sorted_messages_by_creation_time = []
        sorted_creation_times_by_creation_time = []
        lfg_messages = []
        for r in results:
            sorted_messages_by_creation_time.append(await self.channel.fetch_message(r["message_id"]))
            sorted_creation_times_by_creation_time.append(r["creation_time"])
            lfg_messages.append(await get_lfg_message(self.client, lfg_id=r["id"], guild=self.guild))

        # sort the LfgMessages by their start_time
        sorted_lfg_messages = sorted(lfg_messages, reverse=True)

        # update the messages with their new message obj
        for message, creation_time, lfg_message in zip(sorted_messages_by_creation_time, sorted_creation_times_by_creation_time, sorted_lfg_messages):
            lfg_message.message = message
            lfg_message.creation_time = creation_time
            await lfg_message.send()


    # gets the display name of the joined members
    def get_joined_members_display_names(
        self
    ) -> list[str]:
        return [member.mention for member in self.joined_members]


    # gets the display name of the alternate members
    def get_alternate_members_display_names(
        self
    ) -> list[str]:
        return [member.mention for member in self.alternate_members]


    # return the formatted embed
    def return_embed(
        self
    ) -> discord.Embed:
        embed = embed_message(
            footer=f"Creator: {self.author.display_name}   |   Your Time",
        )

        # add the fields with the data
        embed.add_field(
            name="Activity",
            value=self.activity,
            inline=True,
        )
        embed.add_field(
            name="Start Time",
            value=f"<t:{int(self.start_time.timestamp())}:f>",
            inline=True,
        )
        embed.add_field(
            name="ID",
            value=str(self.id),
            inline=True,
        )
        embed.add_field(
            name="Description",
            value=self.description,
            inline=False,
        )
        embed.add_field(
            name=f"Guardians Joined ({len(self.joined_members)}/{self.max_joined_members})",
            value=", ".join(self.get_joined_members_display_names()) if self.joined_members else "_Empty Space :(_",
            inline=True,
        )
        if self.alternate_members:
            embed.add_field(
                name="Backup",
                value=", ".join(self.get_alternate_members_display_names()),
                inline=True,
            )

        # add the start time to the footerpip uninstall
        embed.timestamp = self.utc_start_time

        return embed


    # returns the buttons for the message
    @staticmethod
    def return_buttons() -> list:
        return [
            manage_components.create_actionrow(
                manage_components.create_button(
                    custom_id="lfg_join",
                    style=ButtonStyle.green,
                    label="Join"
                ),
                manage_components.create_button(
                    custom_id="lfg_leave",
                    style=ButtonStyle.red,
                    label="Leave"
                ),
                manage_components.create_button(
                    custom_id="lfg_backup",
                    style=ButtonStyle.blue,
                    label="Backup"
                ),
            ),
        ]


    # updates the database entry
    async def dump_to_db(
        self
    ):
        await insert_lfg_message(
            lfg_message_id=self.id,
            guild_id=self.guild.id,
            channel_id=self.channel.id,
            message_id=self.message.id,
            author_id=self.author.id,
            voice_channel=self.voice_channel,
            activity=self.activity,
            description=self.description,
            start_time=self.start_time,
            creation_time=self.creation_time,
            max_joined_members=self.max_joined_members,
            joined_members=[member.id for member in self.joined_members],
            alternate_members=[member.id for member in self.alternate_members],
        )


    # (re-) scheduled the event with apscheduler using the lfg_id as event_id
    async def schedule_event(
        self
    ):
        # try to delete old job
        try:
            self.scheduler.remove_job(str(self.id))
        except JobLookupError:
            pass

        # using the id the job gets added
        timedelta = datetime.timedelta(minutes=10)
        run_date = self.utc_start_time - timedelta
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        if run_date < now:
            run_date = now
        self.scheduler.add_job(
            notify_about_lfg_event_start, 'date', (self.client, self.guild, self.id, timedelta),
            run_date=run_date, id=str(self.id)
        )


    # send / edit the message in the channel
    async def send(
        self,
        ctx: ComponentContext = None
    ):
        embed = self.return_embed()
        buttons = self.return_buttons()

        if not self.message:
            self.message = await self.channel.send(embed=embed, components=buttons)
            self.creation_time = datetime.datetime.now(tz=datetime.timezone.utc)
            first_send = True
        else:
            # acknodlege the button press
            if ctx:
                await ctx.edit_origin(embed=embed, components=buttons)
            else:
                await self.message.edit(embed=embed, components=buttons)
            first_send = False

        # update the database entry
        await self.dump_to_db()

        # schedule the event
        await self.schedule_event()

        # if message was freshly send, sort messages
        if first_send:
            await self.sort_lfg_messages()


    # removes the message and also the database entries
    async def delete(
        self
    ):
        # delete message
        if self.message:
            await self.message.delete()

        # try to delete voice channel, if that is currently empty
        if self.voice_channel and not self.voice_channel.members:
            try:
                await self.voice_channel.delete()
            except discord.NotFound:
                pass

        # delete DB entry
        await delete_lfg_message(self.id)

        # delete scheduler event
        # try to delete old job
        try:
            self.scheduler.remove_job(str(self.id))
        except JobLookupError:
            pass


async def get_lfg_message(
    client: discord.Client,
    lfg_id: int = None,
    ctx: SlashContext = None,
    lfg_message_id: int = None,
    guild: discord.Guild = None
) -> Union[LfgMessage, None]:
    assert (ctx or guild), "Either ctx or client need to be specified"
    assert (lfg_id or lfg_message_id), "Either lfg id or message id need to be specified"

    # get the stuff from the DB
    res = await select_lfg_message(lfg_id=lfg_id, lfg_message_id=lfg_message_id)
    if not res:
        if ctx:
            await ctx.send(
                hidden=True, embed=embed_message(
                    "Error",
                    f"ID `{lfg_id}` does not exist. Please try again"
                )
            )
        return None

    if ctx:
        guild = ctx.bot.get_guild(res["guild_id"])
    author = guild.get_member(res["author_id"]) if guild else None

    # check that the lfg post is in the correct server
    if ctx:
        if ctx.guild != guild:
            await ctx.send(
                hidden=True, embed=embed_message(
                    "Error",
                    f"ID `{lfg_id}` belongs to a different server. Please try again"
                )
            )
            return None

        # check that the author matches or user has elevated permissions
        if (ctx.author != author) and (not await has_elevated_permissions(ctx.author, ctx.guild)):
            await ctx.send(
                hidden=True, embed=embed_message(
                    "Error",
                    f"You do not have permissions to do stuff to the LFG with ID `{lfg_id}`"
                )
            )
            return None

    lfg_id = res["id"]
    channel = guild.get_channel(res["channel_id"])
    try:
        message = await channel.fetch_message(res["message_id"]) if channel else None
    except discord.NotFound:
        message = None
    voice_channel = guild.get_channel(res["voice_channel_id"]) if res["voice_channel_id"] else None
    activity = res["activity"]
    description = res["description"]
    start_time = res["start_time"]
    creation_time = res["creation_time"]
    max_joined_members = res["max_joined_members"]
    joined_members = [guild.get_member(member) for member in res["joined_members"]]
    alternate_members = [guild.get_member(member) for member in res["alternate_members"]]
    blacklisted_members = await get_lfg_blacklisted_members(author.id)

    # create LfgMessage object
    lfg_message = LfgMessage(
        client=client,
        id=lfg_id,
        guild=guild,
        channel=channel,
        voice_channel=voice_channel,
        author=author,
        activity=activity,
        description=description,
        start_time=start_time,
        creation_time=creation_time,
        max_joined_members=max_joined_members,
        blacklisted_members=blacklisted_members,
        message=message,
        joined_members=joined_members,
        alternate_members=alternate_members
    )

    return lfg_message


async def create_lfg_message(
    client: discord.Client,
    guild: discord.Guild,
    author: discord.Member,
    activity: str,
    description: str,
    start_time: datetime,
    max_joined_members: int
):
    # get next free id
    lfg_id = await get_next_free_lfg_message_id()

    # get blacklisted members
    blacklisted_members = await get_lfg_blacklisted_members(author.id)

    # get channel id
    result = await get_persistent_message("lfg", guild.id)
    if not result:
        return
    channel = guild.get_channel(result[0])

    # create LfgMessage object
    lfg_message = LfgMessage(
        client=client,
        id=lfg_id,
        guild=guild,
        channel=channel,
        author=author,
        activity=activity,
        description=description,
        start_time=start_time,
        max_joined_members=max_joined_members,
        blacklisted_members=blacklisted_members
    )

    # send and save to db
    await lfg_message.send()


async def notify_about_lfg_event_start(
    client: discord.Client,
    guild: discord.Guild,
    lfg_id: int,
    time_to_start: datetime.timedelta
):
    """ DMs the given list of users that the event is about to start """

    lfg_message = await get_lfg_message(client, lfg_id, guild=guild)
    await lfg_message.notify_about_start(time_to_start)
