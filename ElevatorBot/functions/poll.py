import dataclasses
from typing import Optional

import discord
from discord_slash import ComponentContext, SlashContext
from discord_slash.utils import manage_components

from ElevatorBot.database.database import insert_poll, get_poll
from ElevatorBot.functions.formating import embed_message


@dataclasses.dataclass()
class Poll:
    name: str
    description: str
    guild: discord.Guild
    channel: discord.TextChannel
    author: discord.Member

    id: int = None
    data: dict = None
    message: discord.Message = None

    select: list[list] = dataclasses.field(init=False)


    def __post_init__(
        self
    ):
        if not self.data:
            self.data = {}

        self.select = [
            manage_components.create_actionrow(
                manage_components.create_select(
                    options=[
                        manage_components.create_select_option(
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
        ] if self.data else []


    # get embed
    def _get_embed(
        self
    ) -> discord.Embed:
        total_users_count = sum([len(option_users) for option_users in self.data.values()])

        embed = embed_message(
            f"Poll: {self.name}",
            f"{self.description}\n**{total_users_count} votes**",
            f"Asked by {self.author.display_name}  |  ID: {self.id}"
        )

        # sort the data by most answers
        self.data = {k: v for k, v in sorted(
            self.data.items(), key=lambda
                item: len(item[1]), reverse=True
        )}

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


    # save the stuff in DB
    async def _dump_to_db(
        self
    ) -> int:
        return await insert_poll(
            poll_id=self.id,
            poll_name=self.name,
            poll_description=self.description,
            poll_data=self.data,
            author_id=self.author.id,
            guild_id=self.guild.id,
            channel_id=self.channel.id,
            message_id=self.message.id if self.message else None,
        )


    # add an option
    async def add_new_option(
        self,
        ctx: SlashContext,
        option: str
    ):
        self.data.update(
            {
                option: []
            }
        )

        # run the post init again to add components
        self.__post_init__()

        await self._edit(edit_ctx=ctx)


    # remove an option
    async def remove_option(
        self,
        ctx: SlashContext,
        option: str
    ):
        try:
            self.data.pop(option)

            # run the post init again to remove components
            self.__post_init__()

            await self._edit(edit_ctx=ctx)
        except KeyError:
            await ctx.send(
                hidden=True,
                embed=embed_message(
                    "Error",
                    "That option doesn't exist"
                ),
            )


    # add a user to a poll option
    async def add_user(
        self,
        select_ctx: ComponentContext,
        member: discord.Member,
        option: str
    ):
        # remove user from all other options
        for option_users in self.data.values():
            try:
                option_users.remove(member.id)
            except ValueError:
                pass

        # add user to option
        self.data[option].append(member.id)
        await self._edit(
            select_ctx=select_ctx
        )


    # update poll
    async def _edit(
        self,
        select_ctx: ComponentContext = None,
        edit_ctx: SlashContext = None
    ):
        assert (select_ctx or edit_ctx), "Only one param can be chosen and one must be"

        embed = self._get_embed()
        await self._dump_to_db()

        if edit_ctx:
            await self.message.edit(
                embed=embed,
                components=self.select,
            )
            await edit_ctx.send(
                hidden=True,
                embed=embed_message(
                    "Success",
                    "Your poll was edited"
                ),
            )

        else:
            await select_ctx.edit_origin(
                embed=embed,
                components=self.select,
            )


    # create poll
    async def create(
        self,
        create_ctx: SlashContext
    ) -> None:
        # dumping to db twice to get the ID
        self.id = await self._dump_to_db()
        embed = self._get_embed()
        self.message = await create_ctx.send(
            embed=embed,
            components=self.select,
        )
        await self._dump_to_db()


    # disable poll
    async def disable(
        self,
        edit_ctx: SlashContext
    ):
        await self.message.edit(
            components=[],
        )
        await edit_ctx.send(
            hidden=True,
            embed=embed_message(
                "Success",
                "Your poll was edited"
            ),
        )


# get the poll object
async def get_poll_object(
    guild: discord.Guild,
    poll_id: int = None,
    poll_message_id: int = None
) -> Optional[Poll]:
    assert (poll_id or poll_message_id), "Only one param can be chosen and one must be"

    # get the DB entry
    record = await get_poll(
        poll_id=int(poll_id) if poll_id else None,
        poll_message_id=poll_message_id,
    )

    # check if the poll is from that guild
    if guild.id != record["guild_id"]:
        return None

    channel = guild.get_channel(record["channel_id"])

    return Poll(
        id=record["id"],
        name=record["name"],
        description=record["description"],
        data=record["data"],
        guild=guild,
        channel=channel,
        author=guild.get_member(record["author_id"]),
        message=await channel.fetch_message(record["message_id"]),
    )


# create the poll
async def create_poll_object(
    ctx: SlashContext,
    name: str,
    description: str,
    guild: discord.Guild,
    channel: discord.TextChannel
) -> None:
    poll = Poll(
        name=name,
        description=description,
        guild=guild,
        channel=channel,
        author=ctx.author,
    )
    await poll.create(ctx)
