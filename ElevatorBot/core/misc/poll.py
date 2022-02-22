import dataclasses
from typing import Optional

from dis_snek import (
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

from ElevatorBot.backendNetworking.errors import BackendException
from ElevatorBot.backendNetworking.misc.polls import BackendPolls
from ElevatorBot.misc.discordShortcutFunctions import has_admin_permission
from ElevatorBot.misc.formatting import embed_message, replace_progress_formatting
from Shared.functions.formatting import make_progress_bar_text
from Shared.networkingSchemas.misc.polls import PollChoice, PollSchema


@dataclasses.dataclass()
class Poll:
    backend: BackendPolls

    name: str
    description: str
    guild: Guild
    channel: GuildText
    author: Member

    image_url: Optional[str] = None

    message: Optional[Message] = None
    id: Optional[int | str] = None
    choices: list[PollChoice] = dataclasses.field(default_factory=list)

    select: list[ActionRow] = dataclasses.field(init=False)

    def __post_init__(self):
        self.select = (
            [
                ActionRow(
                    Select(
                        options=[
                            SelectOption(
                                label=choice.name,
                                value=choice.name,
                            )
                            for choice in self.choices
                        ],
                        placeholder="Please select your choice",
                        min_values=1,
                        max_values=1,
                        custom_id="poll",
                    )
                ),
            ]
            if self.choices
            else []
        )

        self.backend.hidden = True

    @classmethod
    async def from_pydantic_model(cls, client, data: PollSchema):
        """Create the obj from the PollSchema data"""

        guild = await client.fetch_guild(data.guild_id)
        channel = await client.fetch_channel(data.channel_id)
        author = await client.fetch_member(data.author_id, guild.id)
        message = await channel.fetch_message(data.message_id)

        # make sure the choices match
        if len(message.embeds[0].fields) != len(data.choices):
            choice_names = [choice.name for choice in data.choices]
            for choice in message.embeds[0].fields:
                if choice.name not in choice_names:
                    data.choices.append(PollChoice(name=choice.name, discord_ids=[]))

        # get the image
        image_url = None
        if image := message.embeds[0].image:
            image_url = image.url

        backend = BackendPolls(ctx=None, discord_member=author, guild=guild)

        return cls(
            backend=backend,
            name=data.name,
            description=data.description,
            image_url=image_url,
            guild=guild,
            channel=channel,
            author=author,
            id=data.id,
            choices=data.choices,
            message=message,
        )

    @classmethod
    async def from_poll_id(cls, poll_id: int, ctx: InteractionContext):
        """Create the obj from the poll id"""

        backend = BackendPolls(ctx=ctx, discord_member=ctx.author, guild=ctx.guild)
        backend.hidden = True
        result = await backend.get(poll_id=poll_id)

        return await Poll.from_pydantic_model(client=ctx.bot, data=result)

    async def add_new_option(self, ctx: InteractionContext, option: str):
        """Add an option"""

        if not await self._check_permission(ctx=ctx):
            return

        model = PollChoice(name=option, discord_ids=[])
        if model in self.choices:
            await ctx.send(embeds=embed_message("Error", f"Option `{option}` already exists"))
            return
        self.choices.append(model)

        # run the post init again to update select
        self.__post_init__()

        await self.send(ctx=ctx)

    async def remove_option(self, ctx: InteractionContext, option: str):
        """Delete an option"""

        if not await self._check_permission(ctx=ctx):
            return

        try:
            result = await self.backend.remove_option(poll_id=self.id, choice_name=option)
            new_poll = await Poll.from_pydantic_model(client=ctx.bot, data=result)
        except BackendException as e:
            # if the delete-call failed, check if the option maybe only exists locally
            choice_names = [choice.name for choice in self.choices]
            if option not in choice_names:
                raise e

            self.choices = [choice for choice in self.choices if choice.name != option]

            # run the post init again to update select
            self.__post_init__()

            new_poll = self

        await new_poll.send(ctx=ctx)

    async def delete(self, ctx: InteractionContext):
        """Delete the poll"""

        if not await self._check_permission(ctx=ctx):
            return

        await self.backend.delete(poll_id=self.id)
        await self.message.delete()

        await ctx.send(
            ephemeral=True,
            embeds=embed_message("Success", "The poll has been deleted"),
        )

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

    async def send(self, ctx: Optional[InteractionContext | ComponentContext] = None, user_input: bool = False):
        """Send the poll message"""

        if not self.id:
            # we have not sent anything to the db yet, so gotta do that and get our id
            self.message = await self.channel.send(
                embeds=embed_message(f"Poll: {self.name}", "Constructing Poll, gimme a sec...")
            )
            await self._dump_to_db()

        # put the actual content in
        embed = self._get_embed()

        # user input can end quicker
        if user_input:
            await ctx.edit_origin(
                embeds=embed,
                components=self.select,
            )
            return

        await self.message.edit(
            embeds=embed,
            components=self.select,
        )

        # respond to the context
        if ctx:
            await ctx.send(
                ephemeral=True,
                embeds=embed_message("Success", f"Check your poll [here]({self.message.jump_url})"),
            )

    async def disable(self, ctx: InteractionContext):
        """Disable the poll and delete it from the DB"""

        if not await self._check_permission(ctx=ctx):
            return

        # delete from db
        await self.backend.delete(poll_id=self.id)

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

        total_users_count = sum([len(choice.discord_ids) for choice in self.choices])

        embed = embed_message(
            f"Poll: {self.name}",
            f"{self.description}\n**{total_users_count} votes**",
            f"Asked by {self.author.display_name}  |  ID: {self.id}",
        )
        if self.image_url:
            embed.set_image(self.image_url)

        # sort the data by most answers
        self.choices = sorted(self.choices, key=lambda item: len(item.discord_ids), reverse=True)

        # add choices
        for choice in self.choices:
            option_users_count = len(choice.discord_ids)
            percentage = option_users_count / total_users_count if total_users_count else 0

            text = make_progress_bar_text(percentage=percentage, bar_length=10)

            embed.add_field(
                name=choice.name,
                value=f"{replace_progress_formatting(text)}   {int(percentage * 100)}%",
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
