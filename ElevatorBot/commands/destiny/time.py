from dis_snek.models import InteractionContext, Member, slash_command

from ElevatorBot.backendNetworking.destiny.account import DestinyAccount
from ElevatorBot.commandHelpers.optionTemplates import (
    default_class_option,
    default_mode_option,
    default_stat_option,
    default_user_option,
)
from ElevatorBot.commandHelpers.subCommandTemplates import stat_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.destiny.stat import get_stat_and_send, stat_translation
from ElevatorBot.misc.formating import embed_message, format_timedelta
from ElevatorBot.misc.helperFunctions import get_now_with_tz
from ElevatorBot.static.destinyDates import (
    expansion_dates,
    season_and_expansion_dates,
    season_dates,
)
from ElevatorBot.static.destinyEnums import ModeScope, StatScope


class Time(BaseScale):
    @slash_command(
        name="time",
        description="Shows you your Destiny 2 playtime split up by season",
    )
    @default_mode_option(description="Restrict the game mode where the playtime counts. Default: All modes")
    @default_class_option(description="Restrict the class where the playtime counts. Default: All classes")
    @default_user_option()
    async def _time(self, ctx: InteractionContext, destiny_class: str = None, mode: int = None, user: Member = None):
        # might take a sec
        await ctx.defer()

        member = user or ctx.author
        account = DestinyAccount(discord_guild=ctx.guild, discord_member=member, client=ctx.bot)

        # get the modes
        # default is total and pve/pve, else its total and specified
        if mode:
            modes = [ModeScope(0), ModeScope(mode)]
        else:
            modes = [ModeScope(0), ModeScope(7), ModeScope(5)]
        modes_names = {
            mode_scope: " ".join(
                [part.capitalize().replace("Pve", "PvE").replace("Pvp", "PvP") for part in mode_scope.name.split["_"]]
            )
            for mode_scope in modes
        }

        # loop through the seasons and get the time played for each
        data = {}
        total = {mode_name: 0 for mode_name in modes_names.values()}
        for season in season_and_expansion_dates:
            # get the next seasons start time as the cutoff or now if its the current season
            try:
                next_season_date = season_and_expansion_dates[(season_and_expansion_dates.index(season) + 1)].start
            except IndexError:
                next_season_date = get_now_with_tz()

            # get the time played
            result = await account.get_time(
                start_time=season.start,
                end_time=next_season_date,
                modes=list(modes_names),
                character_class=destiny_class,
            )
            if not result:
                await result.send_error_message(ctx=ctx)
                return

            # save that info
            data.update(
                {
                    season: {
                        modes_names[ModeScope(mode_int)]: time_played["time_played"]
                        for mode_int, time_played in result.result.items()
                    }
                }
            )

            # add to the total amount
            for mode_int, time_played in result.result.items():
                total[modes_names[ModeScope(mode_int)]] += time_played["time_played"]

        # prepare the embed
        embed = embed_message(
            f"{user.display_name} D2 Time Played",
            "\n".join([f"**{name}**: {format_timedelta(value)}" for name, value in total.items()]),
        )

        # set footer
        footer = []
        if destiny_class:
            footer.append(f"Class: {destiny_class}")
        if mode:
            footer.append(f"Mode: {modes_names[ModeScope(mode)]}")
        if footer:
            embed.set_footer(" | ".join(footer))

        # loop through the results and add embed fields
        for season, season_values in data.items():
            # only append season info if they actually played that season
            if season_values[ModeScope.ALL] == 0:
                continue

            embed.add_field(
                name=season.name,
                value="\n".join([f"**{name}**: {format_timedelta(value)}" for name, value in season_values.items()]),
                inline=True,
            )

        await ctx.send(embeds=embed)


def setup(client):
    Time(client)
