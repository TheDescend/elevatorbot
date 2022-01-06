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
from dis_snek.models.events import Component

from ElevatorBot.backendNetworking.destiny.account import DestinyAccount
from ElevatorBot.commandHelpers.optionTemplates import default_user_option
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message, format_progress
from NetworkingSchemas.destiny.account import SeasonalChallengesTopicsModel


class SeasonalChallenges(BaseScale):
    @slash_command(
        name="challenges", description="Shows you the current Destiny 2 seasonal challenges and your completion status"
    )
    @default_user_option()
    async def challenges(
        self,
        ctx: InteractionContext,
        user: Member = None,
    ):
        member = user or ctx.author
        destiny_account = DestinyAccount(ctx=ctx, discord_member=member, discord_guild=ctx.guild)

        # get the data
        result = await destiny_account.get_seasonal_challenges()

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
                        name=format_progress(
                            name=sc.name,
                            completion_status=sc.completion_status,
                            completion_percentage=sc.completion_percentage,
                        ),
                        value=sc.description,
                        inline=False,
                    )

        # send message
        if not select_ctx:
            message = await interaction_ctx.send(embeds=embed, components=select)
        else:
            await select_ctx.edit_origin(embeds=embed)

        # wait 60s for selection
        def check(component_check: Component):
            return component_check.context.author == author

        try:
            component: Component = await self.client.wait_for_component(components=select, timeout=60, check=check)
        except asyncio.TimeoutError:
            await message.edit(components=[])
            return
        else:
            select_ctx = component.context
            new_week = select_ctx.values[0]

            # recursively call this function
            await self._send_challenge_info(
                author=author,
                member=member,
                week=new_week,
                seasonal_challenges=seasonal_challenges,
                select_ctx=select_ctx,
                message=message,
                select=select,
            )


def setup(client):
    SeasonalChallenges(client)
