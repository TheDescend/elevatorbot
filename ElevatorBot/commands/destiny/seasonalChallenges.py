import asyncio

from dis_snek.models import (
    ActionRow,
    ComponentContext,
    InteractionContext,
    Member,
    Message,
    Select,
    SelectOption,
    slash_command,
)

from ElevatorBot.backendNetworking.destiny.account import DestinyAccount
from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message
from NetworkingSchemas.destiny.account import SeasonalChallengesTopicsModel


class SeasonalChallenges(BaseScale):
    @slash_command(
        name="challenges", description="Shows you the current seasonal challenges and your completion status"
    )
    @default_user_option()
    async def _challenges(
        self,
        ctx: InteractionContext,
        user: Member = None,
    ):
        member = user or ctx.author
        destiny_account = DestinyAccount(ctx=ctx, client=ctx.bot, discord_member=member, discord_guild=ctx.guild)

        # get the data
        result = await destiny_account.get_seasonal_challenges()
        if not result:
            return

        # create select components
        select = [
            ActionRow(
                Select(
                    options=[
                        SelectOption(
                            emoji="📅",
                            label=topic.name,
                            value=topic.name,
                        )
                        for topic in result.topics
                    ],
                    placeholder="Select the week you want to see",
                    min_values=1,
                    max_values=1,
                )
            ),
        ]

        # send data and wait for new user input
        await self._send_challenge_info(
            author=ctx.author,
            member=member,
            week=result.topics[0].name,
            seasonal_challenges=result.topics,
            select=select,
            interaction_ctx=ctx,
        )

    async def _send_challenge_info(
        self,
        author: Member,
        member: Member,
        week: str,
        seasonal_challenges: list[SeasonalChallengesTopicsModel],
        select: list[ActionRow] = None,
        interaction_ctx: InteractionContext = None,
        select_ctx: ComponentContext = None,
        message: Message = None,
    ) -> None:
        """this is a recursive command. send the info to the user"""

        # get the embed
        embed = embed_message(f"{member.display_name}'s Seasonal Challenges - {week}")

        # loop through the records and add them to the embed
        for topic in seasonal_challenges:
            if topic.name == week:
                for sc in topic.seasonal_challenges:
                    embed.add_field(
                        name=f"""{sc.name}   |   {sc.completion_status}  {int(sc.completion_percentage * 100)}%""",
                        value=sc.description,
                        inline=False,
                    )

        # send message
        if not select_ctx:
            message = await interaction_ctx.send(embeds=embed, components=select)
        else:
            await select_ctx.edit_origin(embeds=embed)

        # todo
        # wait 60s for selection
        def check(select_ctx: ComponentContext):
            return select_ctx.author == author

        try:
            select_ctx: ComponentContext = await manage_components.wait_for_component(
                select_ctx.bot if select_ctx else ctx.bot,
                components=select,
                timeout=60,
            )
        except asyncio.TimeoutError:
            await message.edit(components=[])
            return
        else:
            new_week = select_ctx.values[0]

            # recursively call this function
            await self._send_challenge_info(
                author=author,
                member=member,
                week=new_week,
                seasonal_challenges=seasonal_challenges,
                select_ctx=select_ctx,
                message=message,
            )


def setup(client):
    SeasonalChallenges(client)
