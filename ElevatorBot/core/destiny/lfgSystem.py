from __future__ import annotations

import asyncio
import dataclasses
import datetime
import io
from typing import Optional

from apscheduler.jobstores.base import JobLookupError
from dis_snek.client import Snake
from dis_snek.errors import Forbidden, NotFound
from dis_snek.models import (
    ActionRow,
    Button,
    ButtonStyles,
    ComponentContext,
    Embed,
    File,
    Guild,
    GuildCategory,
    GuildText,
    GuildVoice,
    InteractionContext,
    Member,
    Message,
    OverwriteTypes,
    PermissionOverwrite,
    Permissions,
    Timestamp,
    TimestampStyles,
)
from ics import Calendar, Event

from ElevatorBot.backendNetworking.destiny.lfgSystem import DestinyLfgSystem
from ElevatorBot.backgroundEvents import scheduler
from ElevatorBot.misc.formating import embed_message
from ElevatorBot.misc.helperFunctions import get_now_with_tz
from ElevatorBot.static.emojis import custom_emojis
from ElevatorBot.static.schemas import LfgInputData, LfgUpdateData

asap_start_time = datetime.datetime(year=1997, month=6, day=11, tzinfo=datetime.timezone.utc)


@dataclasses.dataclass()
class LfgMessage:
    """Class to hold an LFG message"""

    backend: DestinyLfgSystem

    client: Snake
    id: int

    guild: Guild
    channel: Optional[GuildText]

    author: Member
    activity: str
    description: str
    start_time: datetime.datetime
    max_joined_members: int

    message: Optional[Message] = None
    creation_time: Optional[datetime.datetime] = None
    joined: Optional[list[Member]] = None
    backup: list[Member] = dataclasses.field(default_factory=list)

    voice_category_channel: Optional[GuildCategory] = None
    voice_channel: Optional[GuildVoice] = None

    # post init to do list
    def __post_init__(self):
        # get the scheduler object
        self.scheduler = scheduler

        # get the button emojis
        self.__join_emoji = custom_emojis.join
        self.__leave_emoji = custom_emojis.leave
        self.__backup_emoji = custom_emojis.backup

        # buttons
        self.__buttons = [
            ActionRow(
                Button(custom_id="lfg_join", style=ButtonStyles.GREEN, label="Join", emoji=self.__join_emoji),
                Button(custom_id="lfg_leave", style=ButtonStyles.RED, label="Leave", emoji=self.__leave_emoji),
                Button(custom_id="lfg_backup", style=ButtonStyles.BLUE, label="Backup", emoji=self.__backup_emoji),
            ),
        ]

        # if the message / channel does not exist, delete info
        if not (self.message or self.channel):
            asyncio.run(self.delete())

    # less than operator to sort the classes by their start time
    def __lt__(self, other):
        return self.start_time < other.start_time

    def __bool__(self):
        return True

    @classmethod
    async def from_component_button(cls, ctx: ComponentContext) -> LfgMessage:
        """Get the LFG data from an embed send by me"""

        # read the lfg id from the embed
        fields = ctx.message.embeds[0].fields
        lfg_id = None
        for field in fields:
            if field.name == "ID":
                lfg_id = int(field.value)
        assert isinstance(lfg_id, int)

        return await LfgMessage.from_lfg_id(ctx=ctx, lfg_id=lfg_id, client=ctx.bot, guild=ctx.guild)

    @classmethod
    async def from_lfg_id(
        cls, lfg_id: int, client: Snake, guild: Guild, ctx: Optional[InteractionContext] = None
    ) -> Optional[LfgMessage]:
        """
        Classmethod to get with a known lfg_id
        Returns LfgMessage() if successful, BackendResult() if not
        """

        backend = DestinyLfgSystem(ctx=ctx, client=client, discord_guild=guild)

        # get the message by the id
        result = await backend.get(lfg_id=lfg_id)
        if not result:
            return

        # fill class info
        channel: GuildText = await guild.get_channel(result.channel_id)
        start_time: datetime.datetime = result.start_time

        lfg_message = cls(
            backend=backend,
            client=client,
            id=result.id,
            guild=guild,
            channel=channel,
            author=guild.get_member(result.author_id),
            activity=result.activity,
            description=result.description,
            start_time=start_time if start_time != asap_start_time else "asap",
            max_joined_members=result.max_joined_members,
            message=await channel.fetch_message(result.message_id),
            creation_time=result.creation_time,
            joined=[guild.get_member(member_id) for member_id in result.joined_members if guild.get_member(member_id)],
            backup=[
                guild.get_member(member_id) for member_id in result.alternate_members if guild.get_member(member_id)
            ],
            voice_channel=await guild.get_channel(result.voice_channel_id),
            voice_category_channel=await guild.get_channel(result.voice_category_channel_id),
        )

        return lfg_message

    @classmethod
    async def create(
        cls,
        ctx: InteractionContext,
        activity: str,
        description: str,
        start_time: datetime.datetime | str,
        max_joined_members: int,
    ) -> Optional[LfgMessage]:
        """Classmethod to create a new lfg message"""

        backend = DestinyLfgSystem(ctx=ctx, client=ctx.bot, discord_guild=ctx.guild)

        # create the message and fill it later
        result = await backend.create(
            discord_member=ctx.author,
            lfg_data=LfgInputData(
                activity=activity,
                description=description,
                start_time=start_time if isinstance(start_time, datetime.datetime) else asap_start_time,
                max_joined_members=max_joined_members,
                joined_members=[ctx.author.id],
                alternate_members=[],
            ),
        )

        # error out if need be
        if not result:
            return

        # create class obj
        lfg_message = cls(
            backend=backend,
            client=ctx.bot,
            id=result.id,
            guild=ctx.guild,
            channel=ctx.guild.get_channel(result.channel_id),
            author=ctx.author,
            activity=activity,
            description=description,
            start_time=start_time,
            max_joined_members=max_joined_members,
            voice_category_channel=ctx.guild.get_channel(result.voice_category_channel_id),
        )

        # send message in the channel to populate missing entries
        await lfg_message.send()

        # respond to the context
        await ctx.send(
            embeds=embed_message(
                "Success",
                f"I've created the event (ID: `{lfg_message.id}`) \nClick [here]({lfg_message.message.jump_url}) to view the event",
            )
        )

        return lfg_message

    async def add_joined(
        self,
        member: Member,
        ctx: Optional[ComponentContext] = None,
        force_into_joined: bool = False,
    ) -> bool:
        """add a member"""

        if member not in self.joined:
            if (len(self.joined) < self.max_joined_members) or force_into_joined:
                self.joined.append(member)
                if member in self.backup:
                    self.backup.remove(member)

                # check if the post is full and the event is supposed to start asap
                if self.start_time == "asap" and len(self.joined) >= self.max_joined_members:
                    self.start_time = datetime.datetime.now(tz=datetime.timezone.utc)
                    await self.__notify_about_start(datetime.timedelta(minutes=10))

            else:
                if member not in self.backup:
                    self.backup.append(member)
                else:
                    return False

            await self.send(ctx=ctx)
            return True
        return False

    async def add_backup(self, member: Member, ctx: Optional[ComponentContext] = None) -> bool:
        """Add a backup or move member to backup"""

        if member not in self.backup:
            self.backup.append(member)

            if member in self.joined:
                self.joined.remove(member)

            await self.send(ctx=ctx)
            return True
        return False

    async def remove_member(self, member: Member, ctx: Optional[ComponentContext] = None) -> bool:
        """Delete a member"""

        if member in self.joined:
            self.joined.remove(member)

            await self.send(ctx=ctx)
            return True

        elif member in self.backup:
            self.backup.remove(member)

            await self.send(ctx=ctx)
            return True
        return False

    async def send(self, ctx: Optional[ComponentContext] = None):
        """send / edit the message in the channel"""

        embed = await self.__return_embed()

        if not self.message:
            self.message = await self.channel.send(embed=embed, components=self.__buttons)
            self.creation_time = get_now_with_tz()
            first_send = True
        else:
            # acknowledge the button press
            if ctx:
                await ctx.edit_origin(embeds=embed, components=self.__buttons)
            else:
                await self.message.edit(embeds=embed, components=self.__buttons)
            first_send = False

        # update the database entry
        await self.__dump_to_db()

        # schedule the event
        await self.schedule_event()

        # if message was freshly send, sort messages
        if first_send:
            await self.__sort_lfg_messages()

    async def delete(self, delete_command_user: Optional[Member] = None):
        """removes the message and also the database entries"""

        if not delete_command_user:
            delete_command_user = self.author

        # delete message
        if self.message:
            await self.message.delete()

        # try to delete voice channel, if that is currently empty
        if self.voice_channel and not self.voice_channel.members:
            try:
                await self.voice_channel.delete()
            except NotFound:
                pass

        # delete DB entry
        result = await self.backend.delete(discord_member=delete_command_user, lfg_id=self.id)

        if result:
            # delete scheduler event
            # try to delete old job
            try:
                self.scheduler.remove_job(str(self.id))
            except JobLookupError:
                pass

    async def alert_start_time_changed(self, previous_start_time: datetime.datetime):
        """Alert all joined / backups that the event start time was changed"""

        embed = embed_message(
            "Attention Please",
            f"The start time for the lfg event [{self.id}]({self.message.jump_url}) has changed \nIt changed from {Timestamp.fromdatetime(previous_start_time).format(style=TimestampStyles.ShortDateTime)} to {Timestamp.fromdatetime(self.start_time).format(style=TimestampStyles.ShortDateTime)}",
        )

        for user in self.joined + self.backup:
            try:
                await user.send(embed=embed)
            except Forbidden:
                pass

    async def schedule_event(self):
        """(re-) scheduled the event with apscheduler using the lfg_id as event_id"""

        if self.message or self.channel:
            # only do this if is it has a start date
            if self.start_time != "asap":

                # try to delete old job
                try:
                    self.scheduler.remove_job(str(self.id))
                except JobLookupError:
                    pass

                # using the id the job gets added
                timedelta = datetime.timedelta(minutes=10)
                run_date = self.start_time - timedelta
                now = get_now_with_tz()
                if run_date < now:
                    run_date = now
                self.scheduler.add_job(
                    self.__notify_about_start,
                    "date",
                    (self.client, self.guild, self.id, timedelta),
                    run_date=run_date,
                    id=str(self.id),
                )

    async def __notify_about_start(self, time_to_start: datetime.timedelta):
        """notifies joined members that the event is about to start"""

        voice_text = "Please start gathering in a voice channel"

        # get the voice channel category and make a voice channel
        if self.voice_category_channel:
            voice_channel_name = f"[ID: {self.id}] {self.activity}"

            # allow each participant to move members
            permission_overrides = []
            for member in self.joined:
                # allow the author to also mute
                if member == self.author:
                    permission_overrides.append(
                        PermissionOverwrite(
                            id=member.id,
                            type=OverwriteTypes.MEMBER,
                            allow=Permissions.MOVE_MEMBERS | Permissions.MUTE_MEMBERS,
                        )
                    )

                else:
                    permission_overrides.append(
                        PermissionOverwrite(
                            id=member.id,
                            type=OverwriteTypes.MEMBER,
                            allow=Permissions.MOVE_MEMBERS,
                        )
                    )

            self.voice_channel = await self.guild.create_voice_channel(
                name=voice_channel_name,
                bitrate=self.guild.bitrate_limit,
                user_limit=self.max_joined_members,
                category=self.voice_category_channel,
                permission_overwrites=permission_overrides,
                reason="LFG event starting",
            )

            # make fancy text
            voice_text = f"Click here to join the voice channel -> {self.voice_channel.mention}"

        # prepare embed
        embed = embed_message(
            f"LFG Event - {self.activity}",
            f"The LFG event [{self.id}]({self.message.jump_url}) is going to start in **{int(time_to_start.seconds / 60)} minutes**\n{voice_text}",
            "Start Time",
        )
        embed.add_field(
            name="Guardians",
            value=", ".join(self.__get_joined_members_display_names()),
            inline=False,
        )
        embed.timestamp = self.start_time

        # if the event was not full
        missing = self.max_joined_members - len(self.joined)
        if self.backup:
            embed.add_field(
                name="Backup",
                value=", ".join(self.__get_alternate_members_display_names()),
                inline=False,
            )

            # dm the backup if they are needed
            if missing > 0:
                for user in self.backup:
                    try:
                        await user.send(embed=embed)
                    except Forbidden:
                        pass

        # dm the users
        for user in self.joined:
            try:
                await user.send(embed=embed)
            except Forbidden:
                pass

        # edit the channel message
        await self.message.edit(embeds=embed, components=[])
        await self.__dump_to_db()

        # wait timedelta + 10 min
        await asyncio.sleep(time_to_start.seconds + 60 * 10)

        # delete the post
        await self.delete()

    async def __sort_lfg_messages(self):
        """sort all the lfg messages in the guild by start_time"""

        async with asyncio.Lock():
            # get all lfg ids
            result = await self.backend.get_all()
            if result:
                events = result.events

                # only continue if there is more than one event
                if len(events) <= 1:
                    return

                # get three lists:
                # a list with the current message objs (sorted by asc creation date)
                # a list with the creation_time
                # and a list with the LfgMessage objs
                sorted_messages_by_creation_time = []
                sorted_creation_times_by_creation_time = []
                lfg_messages = []
                for event in events:
                    sorted_messages_by_creation_time.append(await self.channel.fetch_message(event.message_id))
                    sorted_creation_times_by_creation_time.append(event.creation_time)
                    lfg_messages.append(
                        LfgMessage(
                            backend=self.backend,
                            client=self.client,
                            id=event.id,
                            guild=self.guild,
                            channel=self.channel,
                            author=self.guild.get_member(event.author_id),
                            activity=event.activity,
                            description=event.description,
                            start_time=event.start_time,
                            max_joined_members=event.max_joined_members,
                            message=await self.channel.fetch_message(event.message_id),
                            creation_time=event.creation_time,
                            joined=[
                                self.guild.get_member(member_id)
                                for member_id in event.joined_members
                                if self.guild.get_member(member_id)
                            ],
                            backup=[
                                self.guild.get_member(member_id)
                                for member_id in event.alternate_members
                                if self.guild.get_member(member_id)
                            ],
                            voice_channel=await self.guild.get_channel(event.voice_channel_id),
                            voice_category_channel=await self.guild.get_channel(event.voice_category_channel_id),
                        )
                    )

                # sort the LfgMessages by their start_time
                sorted_lfg_messages = sorted(lfg_messages, reverse=True)

                # update the messages with their new message obj
                for message, creation_time, lfg_message in zip(
                    sorted_messages_by_creation_time,
                    sorted_creation_times_by_creation_time,
                    sorted_lfg_messages,
                ):
                    lfg_message.message = message
                    lfg_message.creation_time = creation_time
                    await lfg_message.send()

    def __get_joined_members_display_names(self) -> list[str]:
        """gets the display name of the joined members"""

        return [member.mention for member in self.joined]

    def __get_alternate_members_display_names(self) -> list[str]:
        """gets the display name of the alternate members"""

        return [member.mention for member in self.backup]

    async def __get_ics_url(self) -> str:
        """Create an ics file, upload it, and return the url"""

        calendar = Calendar()
        event = Event()
        event.name = f"LFG event `{self.id}`"
        event.description = f"{self.activity}: {self.description}"
        event.location = f"Server: {self.guild.name}"
        event.categories = ["Destiny 2", "LFG"]
        event.begin = self.start_time
        event.duration = datetime.timedelta(hours=1, minutes=30)
        calendar.events.add(event)

        data = io.StringIO(str(calendar))

        # send this in the spam channel in one of the test servers
        spam_server: GuildText = await self.client.get_channel(761278600103723018)
        file_message = await spam_server.send(file=File(file=data, file_name=f"lfg_event_{self.id}.ics"))

        return file_message.attachments[0].url

    async def __return_embed(self) -> Embed:
        """return the formatted embed"""

        embed = embed_message(
            footer=f"Creator: {self.author.display_name}   |   Your Time",
        )

        # add the fields with the data
        embed.add_field(
            name="Activity",
            value=self.activity,
            inline=True,
        )
        if isinstance(self.start_time, datetime.datetime):
            embed.add_field(
                name="Start Time",
                value=f"{Timestamp.fromdatetime(self.start_time).format(style=TimestampStyles.ShortDateTime)}\n[Add To Calendar]({await self.__get_ics_url()})",
                inline=True,
            )
        else:
            embed.add_field(
                name="Start Time",
                value=f"__As Soon As Full__",
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
            name=f"Guardians Joined ({len(self.joined)}/{self.max_joined_members})",
            value=", ".join(self.__get_joined_members_display_names()) if self.joined else "_Empty Space :(_",
            inline=True,
        )
        if self.backup:
            embed.add_field(
                name="Backup",
                value=", ".join(self.__get_alternate_members_display_names()),
                inline=True,
            )

        if isinstance(self.start_time, datetime.datetime):
            # add the start time to the footer
            embed.timestamp = self.start_time

        return embed

    async def __dump_to_db(self):
        """updates the database entry"""

        await self.backend.update(
            lfg_id=self.id,
            discord_member=self.author,
            lfg_data=LfgUpdateData(
                channel_id=self.channel.id,
                message_id=self.message.id,
                voice_channel_id=self.voice_channel.id if self.voice_channel else None,
                activity=self.activity,
                description=self.description,
                start_time=self.start_time if isinstance(self.start_time, datetime.datetime) else asap_start_time,
                max_joined_members=self.max_joined_members,
                joined_members=[member.id for member in self.joined],
                alternate_members=[member.id for member in self.backup],
            ),
        )

    async def __edit_start_time_and_send(self, start_time: datetime.datetime):
        """edit start time and sort messages again"""
        self.start_time = start_time

        # send
        await self.send()

        # sort again
        await self.__sort_lfg_messages()
