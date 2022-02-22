from __future__ import annotations

import asyncio
import dataclasses
import datetime
import io
import logging
from typing import Optional

from apscheduler.jobstores.base import JobLookupError
from dis_snek import (
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
    Snake,
    Timestamp,
    TimestampStyles,
)
from dis_snek.client.errors import Forbidden, NotFound
from ics import Calendar, Event

from ElevatorBot.backendNetworking.destiny.lfgSystem import DestinyLfgSystem
from ElevatorBot.backendNetworking.errors import BackendException
from ElevatorBot.commandHelpers.autocomplete import activities
from ElevatorBot.core.destiny.lfg.scheduledEvents import delete_lfg_scheduled_events
from ElevatorBot.discordEvents.base import ElevatorSnake
from ElevatorBot.misc.formatting import embed_message, replace_progress_formatting
from ElevatorBot.static.emojis import custom_emojis
from Shared.functions.formatting import make_progress_bar_text
from Shared.functions.helperFunctions import get_now_with_tz
from Shared.functions.readSettingsFile import get_setting
from Shared.networkingSchemas.destiny.lfgSystem import LfgCreateInputModel, LfgOutputModel, LfgUpdateInputModel

asap_start_time = datetime.datetime(year=1997, month=6, day=11, tzinfo=datetime.timezone.utc)


@dataclasses.dataclass()
class LfgMessage:
    """Class to hold an LFG message"""

    client: ElevatorSnake | Snake
    backend: DestinyLfgSystem

    id: int
    guild: Guild

    author_id: int
    activity: str
    description: str
    start_time: datetime.datetime
    max_joined_members: int

    channel: Optional[GuildText] = None
    message: Optional[Message] = None
    creation_time: Optional[datetime.datetime] = None
    joined_ids: list[int] = dataclasses.field(default_factory=list)
    backup_ids: list[int] = dataclasses.field(default_factory=list)

    voice_category_channel: Optional[GuildCategory] = None
    voice_channel: Optional[GuildVoice] = None

    started: bool = False

    def __post_init__(self):
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

    def __lt__(self, other):
        # special behaviour if one is "asap"
        if self.start_time == "asap":
            return True
        if other.start_time == "asap":
            return False

        # sort the classes by their start time
        return self.start_time < other.start_time

    def __bool__(self):
        return True

    @classmethod
    async def from_lfg_output_model(
        cls, client, model: LfgOutputModel, backend: DestinyLfgSystem, guild: Optional[Guild] = None
    ) -> Optional[LfgMessage]:
        """Parse the info from the pydantic model"""

        if not guild:
            guild = await client.fetch_guild(model.guild_id)
            if not guild:
                raise ValueError

        # fill class info
        channel: GuildText = await client.fetch_channel(model.channel_id)
        start_time: datetime.datetime = model.start_time

        # delete if in the past
        if model.start_time < get_now_with_tz():
            await backend.delete(discord_member_id=model.author_id, lfg_id=model.id)
            return

        # make sure the message exists
        message = await channel.fetch_message(model.message_id) if model.message_id else None
        if not message:
            await backend.delete(discord_member_id=model.author_id, lfg_id=model.id)
            return

        lfg_message = cls(
            backend=backend,
            client=client,
            id=model.id,
            guild=guild,
            channel=channel,
            author_id=model.author_id,
            activity=model.activity,
            description=model.description,
            start_time=start_time if start_time != asap_start_time else "asap",
            max_joined_members=model.max_joined_members,
            message=message,
            creation_time=model.creation_time,
            joined_ids=model.joined_members,
            backup_ids=model.backup_members,
            voice_channel=await client.fetch_channel(model.voice_channel_id) if model.voice_channel_id else None,
            voice_category_channel=await client.fetch_channel(model.voice_category_channel_id)
            if model.voice_category_channel_id
            else None,
            started=model.started,
        )

        return lfg_message

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

        try:
            lfg_message = await LfgMessage.from_lfg_id(ctx=ctx, lfg_id=lfg_id, client=ctx.bot, guild=ctx.guild)
        except BackendException as error:
            if error.error == "NoLfgEventWithIdForGuild":
                lfg_message = None
            else:
                raise error

        # error if that fails
        if not lfg_message:
            await ctx.message.delete()
            await ctx.send(
                embed=embed_message(
                    "Error",
                    "This LFG event has been lost to the depths of time in the vault of glass\nIt does not exist, and the message has now been deleted accordingly\nSorry for that",
                ),
                ephemeral=True,
            )

        return lfg_message

    @classmethod
    async def from_lfg_id(
        cls, lfg_id: int, client: ElevatorSnake | Snake, guild: Guild, ctx: Optional[InteractionContext] = None
    ) -> Optional[LfgMessage]:
        """
        Classmethod to get with a known lfg_id
        Returns LfgMessage() if successful, BackendResult() if not
        """

        backend = DestinyLfgSystem(ctx=ctx, discord_guild=guild)
        backend.hidden = True

        # get the message by the id
        result = await backend.get(lfg_id=lfg_id)

        return await LfgMessage.from_lfg_output_model(client=client, model=result, backend=backend, guild=guild)

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

        backend = DestinyLfgSystem(ctx=ctx, discord_guild=ctx.guild)

        # create the message and fill it later
        result = await backend.create(
            discord_member=ctx.author,
            lfg_data=LfgCreateInputModel(
                activity=activity,
                description=description,
                start_time=start_time if isinstance(start_time, datetime.datetime) else asap_start_time,
                max_joined_members=max_joined_members,
                joined_members=[ctx.author.id],
                backup_members=[],
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
            channel=await ctx.bot.fetch_channel(result.channel_id),
            author_id=ctx.author.id,
            activity=activity,
            description=description,
            start_time=start_time,
            max_joined_members=max_joined_members,
            voice_category_channel=await ctx.bot.fetch_channel(result.voice_category_channel_id)
            if result.voice_category_channel_id
            else None,
            joined_ids=[ctx.author.id],
            started=result.started,
        )

        # send message in the channel to populate missing entries
        await lfg_message.send(ctx=ctx)

        return lfg_message

    async def add_joined(
        self,
        member: Member,
        ctx: Optional[ComponentContext] = None,
        force_into_joined: bool = False,
    ) -> bool:
        """Add a member"""

        if member.id not in self.joined_ids:
            if (len(self.joined_ids) < self.max_joined_members) or force_into_joined:
                self.joined_ids.append(member.id)
                if member.id in self.backup_ids:
                    self.backup_ids.remove(member.id)

                # check if the post is full and the event is supposed to start asap
                if self.start_time == "asap" and len(self.joined_ids) >= self.max_joined_members:
                    self.start_time = datetime.datetime.now(tz=datetime.timezone.utc)
                    await self.__notify_about_start(datetime.timedelta(minutes=10))

            else:
                if member.id not in self.backup_ids:
                    self.backup_ids.append(member.id)
                else:
                    return False

            await self.send(ctx=ctx)
            return True
        return False

    async def add_backup(self, member: Member, ctx: Optional[ComponentContext] = None) -> bool:
        """Add a backup or move a member to backup"""

        if member.id not in self.backup_ids:
            self.backup_ids.append(member.id)

            if member.id in self.joined_ids:
                self.joined_ids.remove(member.id)

            await self.send(ctx=ctx)
            return True
        return False

    async def remove_member(self, member: Member, ctx: Optional[ComponentContext] = None) -> bool:
        """Delete a member"""

        if member.id in self.joined_ids:
            self.joined_ids.remove(member.id)

            await self.send(ctx=ctx)
            return True

        elif member.id in self.backup_ids:
            self.backup_ids.remove(member.id)

            await self.send(ctx=ctx)
            return True
        return False

    async def send(self, ctx: Optional[ComponentContext | InteractionContext] = None, force_sort: bool = False):
        """Send / edit the message in the channel"""

        embed = await self.__return_embed()

        if not self.message:
            self.message = await self.channel.send(embed=embed, components=self.__buttons)
            self.creation_time = get_now_with_tz()
            force_sort = True

            # respond to the context
            if ctx:
                await ctx.send(
                    embeds=embed_message(
                        "Success",
                        f"I've created the event (ID: `{self.message.id}`) \nClick [here]({self.message.jump_url}) to view the event",
                    )
                )

        else:
            # acknowledge the button press
            if ctx:
                await ctx.edit_origin(embeds=embed, components=self.__buttons)
            else:
                await self.message.edit(embeds=embed, components=self.__buttons)

        # update the database entry
        await self.__dump_to_db()

        # schedule the event
        if isinstance(self.start_time, datetime.datetime):
            # skip that if the event starts within 15 minutes
            if self.start_time < (get_now_with_tz() + datetime.timedelta(minutes=15)):
                await self.__notify_about_start()
            else:
                await self.schedule_event()

                # if message was freshly send, sort messages
                if force_sort:
                    await self.__sort_lfg_messages()

    async def delete(self, delete_command_user_id: Optional[int] = None):
        """Removes the message and also the database entries"""

        if not delete_command_user_id:
            delete_command_user_id = self.author_id

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
        await self.backend.delete(discord_member_id=self.author_id, lfg_id=self.id)

        # delete scheduler event
        # try to delete old job
        try:
            self.client.scheduler.remove_job(str(self.id))
        except JobLookupError:
            pass

    async def alert_start_time_changed(self, new_start_time: datetime.datetime):
        """Alert all joined / backups that the event start time was changed"""

        embed = embed_message(
            "Attention Please",
            f"The start time for the lfg event [{self.id}]({self.message.jump_url}) has changed \nIt changed from {Timestamp.fromdatetime(self.start_time).format(style=TimestampStyles.ShortDateTime)} to {Timestamp.fromdatetime(new_start_time).format(style=TimestampStyles.ShortDateTime)}",
        )
        self.start_time = new_start_time

        for user_id in self.joined_ids + self.backup_ids:
            try:
                user = await self.guild.fetch_member(user_id)
                if user:
                    await user.send(embed=embed)
            except Forbidden:
                pass

    async def schedule_event(self):
        """(Re-) schedule the event with apscheduler using the lfg_id as event_id"""

        if self.message or self.channel:
            # only do this if is it has a start date
            if self.start_time != "asap":
                # try to delete old job
                delete_lfg_scheduled_events(event_scheduler=self.client.scheduler, event_ids=[self.id])

                # using the id the job gets added
                timedelta = datetime.timedelta(minutes=10)
                run_date = self.start_time - timedelta
                self.client.scheduler.add_job(
                    func=self.__notify_about_start,
                    trigger="date",
                    run_date=run_date,
                    id=str(self.id),
                )

    async def __notify_about_start(self):
        """Notify joined members that the event is about to start"""

        voice_text = "Please start gathering in a voice channel"

        # get the voice channel category and make a voice channel
        if self.voice_category_channel:
            voice_channel_name = f"[ID: {self.id}] {self.activity}"

            # allow each participant to move members
            permission_overrides = []
            for member_id in self.joined_ids:
                # allow the author to also mute
                if member_id == self.author_id:
                    permission_overrides.append(
                        PermissionOverwrite(
                            id=member_id,
                            type=OverwriteTypes.MEMBER,
                            allow=Permissions.MOVE_MEMBERS | Permissions.MUTE_MEMBERS,
                        )
                    )

                else:
                    permission_overrides.append(
                        PermissionOverwrite(
                            id=member_id,
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
            f"The LFG event [{self.id}]({self.message.jump_url}) is going to start {Timestamp.fromdatetime(self.start_time).format(style=TimestampStyles.RelativeTime)}\n{voice_text}",
            "Start Time",
        )
        embed.add_field(
            name="Guardians Joined",
            value=", ".join(await self.__get_joined_members_display_names()),
            inline=False,
        )

        # if the event was not full
        missing = self.max_joined_members - len(self.joined_ids)
        if self.backup_ids:
            embed.add_field(
                name="Backup",
                value=", ".join(await self.__get_alternate_members_display_names()),
                inline=False,
            )

            # dm the backup if they are needed
            if missing > 0:
                for user_id in self.backup_ids:
                    try:
                        user = await self.guild.fetch_member(user_id)
                        if user:
                            await user.send(embed=embed)
                    except Forbidden:
                        pass

        # dm the users
        for user_id in self.joined_ids:
            try:
                user = await self.guild.fetch_member(user_id)
                if user:
                    await user.send(embed=embed)
            except Forbidden:
                pass

        # edit the channel message
        self.started = True
        await self.message.edit(embeds=embed, components=[])
        await self.__dump_to_db()

        # wait time to start + 10 min
        await asyncio.sleep((self.start_time - get_now_with_tz()).seconds + 60 * 10)

        # delete the post
        await self.delete()

        # delete the voice channel if empty
        if self.voice_channel and not self.voice_channel.voice_members:
            await self.voice_channel.delete()

    async def __sort_lfg_messages(self):
        """Sort all the lfg messages in the guild by start_time"""

        async with asyncio.Lock():
            # get all lfg ids
            result = await self.backend.get_all()
            events = result.events

            # only continue if there is more than one event
            if len(events) <= 1:
                return

            # get two lists:
            # a list with the current message objs (sorted by asc creation date)
            # a list with the LfgMessage objs
            sorted_messages_by_creation_time = []
            lfg_messages = []
            for event in events:
                # ignore started messages
                if event.started:
                    continue

                message = await self.channel.fetch_message(event.message_id)
                sorted_messages_by_creation_time.append(message)
                lfg_messages.append(
                    LfgMessage(
                        backend=self.backend,
                        client=self.client,
                        id=event.id,
                        guild=self.guild,
                        channel=self.channel,
                        author_id=event.author_id,
                        activity=event.activity,
                        description=event.description,
                        start_time=event.start_time if event.start_time != asap_start_time else "asap",
                        max_joined_members=event.max_joined_members,
                        message=message,
                        creation_time=event.creation_time,
                        joined_ids=event.joined_members,
                        backup_ids=event.backup_members,
                        voice_channel=await self.client.fetch_channel(event.voice_channel_id)
                        if event.voice_channel_id
                        else None,
                        voice_category_channel=await self.client.fetch_channel(event.voice_category_channel_id)
                        if event.voice_category_channel_id
                        else None,
                        started=event.started,
                    )
                )

            # sort the LfgMessages by their start_time
            # latest at the bottom
            sorted_lfg_messages = sorted(lfg_messages, reverse=True)

            # update the messages with their new message obj
            for message, lfg_message in zip(sorted_messages_by_creation_time, sorted_lfg_messages):
                # only send if the message changed
                if lfg_message != message:
                    lfg_message.message = message
                    await lfg_message.send()

    async def __get_joined_members_display_names(self) -> list[str]:
        """Get the mention strings of the joined members"""

        mentions = []
        for member_id in self.joined_ids:
            member = await self.guild.fetch_member(member_id)
            mentions.append(member.mention if member else f"`{member_id}`")
        return mentions

    async def __get_alternate_members_display_names(self) -> list[str]:
        """Get the mention strings of the alternate members"""

        mentions = []
        for member_id in self.backup_ids:
            member = await self.guild.fetch_member(member_id)
            mentions.append(member.mention if member else f"`{member_id}`")
        return mentions

    def __reuse_ics_url(self) -> Optional[str]:
        """Try to reuse the ics url"""

        if self.message:
            embed = self.message.embeds[0]

            # check if the message name matches
            try:
                if embed.fields[0].value != self.activity:
                    return

                # check if the message start time matches
                start_time = embed.fields[1].value.split("\n")
                if start_time[0] != Timestamp.fromdatetime(self.start_time).format(style=TimestampStyles.ShortDateTime):
                    return

                # check if the message description matches
                if embed.fields[3].value != self.description:
                    return

                # return the ics url
                return start_time[1].removeprefix("[Add To Calendar]")[1:-1]
            except:
                print(embed)
                logging.getLogger("generalExceptions").error(embed)

    async def __get_ics_url(self) -> str:
        """Create an ics file, upload it, and return the url if it does not exist yet"""

        # try to re-use the ics url
        url = self.__reuse_ics_url()
        if url:
            return url

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
        spam_server: GuildText = await self.client.fetch_channel(get_setting("DESCEND_SPAM_CHANNEL_ID"))
        file_message = await spam_server.send(file=File(file=data, file_name=f"lfg_event_{self.id}.ics"))

        return file_message.attachments[0].url

    async def __return_embed(self) -> Embed:
        """Return the formatted embed"""

        author = await self.guild.fetch_member(self.author_id)
        embed = embed_message(
            footer=f"Creator: {author.display_name if author else self.author_id}",
        )
        if author:
            embed.footer.icon_url = author.display_avatar.url

        # add the fields with the data
        embed.add_field(
            name="Activity",
            value=self.activity,
            inline=True,
        )
        image_url = activities[self.activity.lower()].image_url
        if image_url:
            embed.set_thumbnail(image_url)

        if isinstance(self.start_time, datetime.datetime):
            embed.add_field(
                name="Start Time",
                value=f"{Timestamp.fromdatetime(self.start_time).format(style=TimestampStyles.ShortDateTime)}\n[Add To Calendar]({await self.__get_ics_url()})",
                inline=True,
            )
        else:
            embed.add_field(
                name="Start Time",
                value="__As Soon As Full__",
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
            name="⁣",
            value=replace_progress_formatting(
                completion_status=make_progress_bar_text(
                    percentage=len(self.joined_ids) / self.max_joined_members if self.max_joined_members != 0 else 0,
                    bar_length=8,
                )
            ),
            inline=False,
        )
        embed.add_field(
            name=f"Guardians Joined ({len(self.joined_ids)}/{self.max_joined_members})",
            value=", ".join(await self.__get_joined_members_display_names()) if self.joined_ids else "_Empty Space :(_",
            inline=True,
        )
        if self.backup_ids:
            embed.add_field(
                name="Backup",
                value=", ".join(await self.__get_alternate_members_display_names()),
                inline=True,
            )

        return embed

    async def __dump_to_db(self):
        """Update the database entry"""

        await self.backend.update(
            lfg_id=self.id,
            discord_member_id=self.author_id,
            lfg_data=LfgUpdateInputModel(
                channel_id=self.channel.id,
                message_id=self.message.id,
                voice_channel_id=self.voice_channel.id if self.voice_channel else None,
                activity=self.activity,
                description=self.description,
                start_time=self.start_time if isinstance(self.start_time, datetime.datetime) else asap_start_time,
                max_joined_members=self.max_joined_members,
                joined_members=self.joined_ids,
                backup_members=self.backup_ids,
                started=self.started,
            ),
        )

    async def __edit_start_time_and_send(self, start_time: datetime.datetime):
        """Edit start time and sort messages again"""
        self.start_time = start_time

        # send
        await self.send()

        # sort again
        await self.__sort_lfg_messages()
