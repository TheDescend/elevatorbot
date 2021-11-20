import dataclasses
from typing import Optional

from dis_snek.client import Snake
from dis_snek.models import (
    ActionRow,
    ComponentContext,
    Embed,
    Guild,
    GuildText,
    InteractionContext,
    Member,
    Message,
    Select,
    SelectOption,
)

from ElevatorBot.backendNetworking.misc.polls import BackendPolls
from ElevatorBot.misc.discordShortcutFunctions import has_admin_permission
from ElevatorBot.misc.formating import embed_message
from NetworkingSchemas.misc.polls import PollSchema


@dataclasses.dataclass()
class Poll:
    backend: BackendPolls

    name: str
    description: str
    guild: Guild
    channel: GuildText
    author: Member
    message: Optional[Message] = None

    id: Optional[int | str] = None
    data: dict = dataclasses.field(default_factory=dict)

    select: list[ActionRow] = dataclasses.field(init=False)

    def __post_init__(self):
        self.select = (
            [
                ActionRow(
                    Select(
                        options=[
                            SelectOption(
                                label=option_name,
                                value=option_name,
                            )
                            for option_name in self.data
                        ],
                        placeholder="Please select your choice",
                        min_values=1,
                        max_values=1,
                        custom_id="poll",
                    )
                ),
            ]
            if self.data
            else []
        )

        self.backend.hidden = True

    @classmethod
    async def from_pydantic_model(cls, client: Snake, data: PollSchema):
        """Create the obj from the PollSchema data"""

        name = data.name
        description = data.description
        guild = await client.get_guild(data.guild_id)
        channel = await guild.get_channel(data.channel_id)
        author = await client.get_member(data.author_id, guild.id)
        poll_id = data.id
        poll_data = data.data
        message = await channel.get_message(data.message_id)

        backend = BackendPolls(ctx=None, discord_member=author, guild=guild)

        return cls(
            backend=backend,
            name=name,
            description=description,
            guild=guild,
            channel=channel,
            author=author,
            id=poll_id,
            data=poll_data,
            message=message,
        )

    @classmethod
    async def from_poll_id(cls, poll_id: int, ctx: InteractionContext):
        """Create the obj from the poll id"""

        backend = BackendPolls(ctx=ctx, discord_member=ctx.author, guild=ctx.guild)
        backend.hidden = True
        result = await backend.get(poll_id=poll_id)

        if not result:
            return

        return await Poll.from_pydantic_model(client=ctx.bot, data=result)

    async def add_new_option(self, ctx: InteractionContext, option: str):
        """Add an option"""

        if not await self._check_permission(ctx=ctx):
            return

        self.data.update({option: []})

        # run the post init again to update select
        self.__post_init__()

        await self.send(ctx=ctx)

    async def remove_option(self, ctx: InteractionContext, option: str):
        """Delete an option"""

        if not await self._check_permission(ctx=ctx):
            return

        result = await self.backend.remove_option(poll_id=self.id, choice_name=option)

        if not result:
            return

        new_poll = await Poll.from_pydantic_model(client=ctx.bot, data=result)
        await new_poll.send(ctx=ctx)

    async def delete(self, ctx: InteractionContext):
        """Delete the poll"""

        if not await self._check_permission(ctx=ctx):
            return

        result = await self.backend.delete(poll_id=self.id)
        if not result:
            return

        await self.message.delete()

    async def _check_permission(self, ctx: InteractionContext) -> bool:
        """Checks permissions from the author"""

        # test that the guild is correct
        if ctx.guild.id != self.guild.id:
            await ctx.send(ephemeral=True, embeds=embed_message("Error", "This poll does not belong to this guild"))
            return False

        # test if the user is admin or author
        if ctx.author.id != self.author.id:
            if not await has_admin_permission(ctx=ctx, member=ctx.author):
                return False

        return True

    async def send(self, ctx: Optional[InteractionContext | ComponentContext] = None):
        """Send the poll message"""

        if not self.id:
            # we have not send anything to the db yet, so gotta do that and get our id
            self.message = await self.channel.send(
                embeds=embed_message(f"Poll: {self.name}", "Constructing Poll, gimme a sec...")
            )
            await self._dump_to_db()

        embed = self._get_embed()

        if ctx:
            if isinstance(ctx, ComponentContext):
                await ctx.edit_origin(
                    embeds=embed,
                    components=self.select,
                )

                await ctx.send(
                    ephemeral=True,
                    embeds=embed_message("Success", "Your poll was edited"),
                )
        else:
            await self.message.edit(
                embeds=embed,
                components=self.select,
            )

        if ctx:
            if not isinstance(ctx, ComponentContext):
                await ctx.send(
                    ephemeral=True,
                    embeds=embed_message("Success", "Your poll was edited"),
                )

    async def disable(self, ctx: InteractionContext):
        """Disable the poll and delete it from the DB"""

        if not await self._check_permission(ctx=ctx):
            return

        # delete from db
        result = await self.backend.delete(poll_id=self.id)
        if not result:
            return

        # edit the message to remove the select and the id
        self.id = "DISABLED"
        embed = self._get_embed()
        await self.message.edit(embeds=embed, components=[])
        await ctx.send(
            ephemeral=True,
            embeds=embed_message("Success", "Your poll was disabled"),
        )

    def _get_embed(self) -> Embed:
        """Get embed"""

        total_users_count = sum([len(option_users) for option_users in self.data.values()])

        embed = embed_message(
            f"Poll: {self.name}",
            f"{self.description}\n**{total_users_count} votes**",
            f"Asked by {self.author.display_name}  |  ID: {self.id}",
        )

        # sort the data by most answers
        self.data = {k: v for k, v in sorted(self.data.items(), key=lambda item: len(item[1]), reverse=True)}

        # add options
        for option_name, option_users in self.data.items():
            option_users_count = len(option_users)

            # number of text elements
            n = 10

            # get value text
            text = ""
            try:
                progress = option_users_count / total_users_count
            except ZeroDivisionError:
                progress = 0
            for i in range(int(progress * n)):
                text += "▓"
            for i in range(n - int(progress * n)):
                text += "░"

            embed.add_field(
                name=option_name,
                value=f"{text} {int(progress * 100)}%",
                inline=False,
            )

        return embed

    async def _dump_to_db(self):
        """Insert the poll to the db"""

        result = await self.backend.insert(
            name=self.name,
            description=self.description,
            channel_id=self.channel.id,
            message_id=self.message.id,
        )

        # save the id we got
        self.id = result.id
