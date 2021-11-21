import dataclasses
import datetime
from io import BytesIO
from typing import Optional

import matplotlib.pyplot as plt
from dis_snek.models import File, InteractionContext, slash_command
from pandas import DataFrame

from ElevatorBot.backendNetworking.destiny.steamPlayers import SteamPlayers
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message
from ElevatorBot.misc.helperFunctions import get_now_with_tz
from ElevatorBot.static.destinyDates import (
    other_important_dates_part_1,
    other_important_dates_part_2,
    season_and_expansion_dates,
)


@dataclasses.dataclass
class PopTimelineCache:
    """This saves the url in the cache for an hour"""

    _time: datetime.datetime = dataclasses.field(init=False, default=datetime.datetime.min)
    _url: str = dataclasses.field(init=False, default=None)

    @property
    def url(self) -> Optional[str]:
        """Get the url if its not an hour old else None"""

        if self._time + datetime.timedelta(hours=1) > get_now_with_tz():
            return self._url

    @url.setter
    def url(self, new_url: str):
        """Set the url"""

        self._url = new_url
        self._time = get_now_with_tz()


cache = PopTimelineCache()


class PopTimeline(BaseScale):
    @slash_command(name="pop_timeline", description="Shows the Destiny 2 steam maximum population timeline")
    async def _pop_timeline(self, ctx: InteractionContext):
        embed = embed_message("Destiny 2 - Steam Player Count")

        # do we have an url cached?
        cache_url = cache.url
        if cache_url:
            embed.set_image(url=cache_url)
            await ctx.send(embeds=embed)

        else:
            # get the data from the DB
            result = await SteamPlayers(ctx=ctx).get()

            if not result:
                return

            # convert to dataframe
            dict_entries = [entry.dict() for entry in result.entries]
            data_frame = DataFrame(data=dict_entries)

            # create figure and plot space
            fig, ax = plt.subplots(figsize=(20, 10))
            ax.yaxis.grid(True)

            # filling plot
            ax.plot(data_frame["date"], data_frame["number_of_players"], "darkred", zorder=2)

            # Set title and labels for axes
            ax.set_xlabel("Date", fontsize=20, fontweight="bold")
            ax.set_ylabel("Players", fontsize=20, fontweight="bold")

            # adding nice lines to mark important events
            for date in season_and_expansion_dates[7:]:
                ax.axvline(date, color="darkgreen", zorder=1)
                ax.text(
                    date.start + datetime.timedelta(days=2),
                    (max(data_frame["number_of_players"]) - min(data_frame["number_of_players"])) * 1.02
                    + min(data_frame["number_of_players"]),
                    date.name,
                    color="darkgreen",
                    fontweight="bold",
                    bbox=dict(facecolor="white", edgecolor="darkgreen", pad=4, zorder=3),
                )
            for date in other_important_dates_part_1:
                ax.axvline(date, color="mediumaquamarine", zorder=1)
                ax.text(
                    date + datetime.timedelta(days=2),
                    (max(data_frame["number_of_players"]) - min(data_frame["number_of_players"])) * 0.95
                    + min(data_frame["number_of_players"]),
                    date.name,
                    color="mediumaquamarine",
                    bbox=dict(
                        facecolor="white",
                        edgecolor="mediumaquamarine",
                        boxstyle="round",
                        zorder=3,
                    ),
                )
            for date in other_important_dates_part_2:
                ax.axvline(date, color="mediumaquamarine", zorder=1)
                ax.text(
                    date + datetime.timedelta(days=2),
                    (max(data_frame["number_of_players"]) - min(data_frame["number_of_players"])) * 0.90
                    + min(data_frame["number_of_players"]),
                    date.name,
                    color="mediumaquamarine",
                    bbox=dict(
                        facecolor="white",
                        edgecolor="mediumaquamarine",
                        boxstyle="round",
                        zorder=3,
                    ),
                )

            # saving file im memory
            buffer = BytesIO()
            title = "d2population.png"
            plt.savefig(buffer, format="png", bbox_inches="tight")

            # start reading from beginning
            buffer.seek(0)

            # sending them the file
            image = File(file_name="d2population.png", file=buffer)
            embed.set_image(url=f"attachment://{title}")
            message = await ctx.send(file=image, embeds=embed)

            # save the url in cache
            cache.url = message.attachments[0].url

            # todo cache this for an hour


def setup(client):
    PopTimeline(client)
