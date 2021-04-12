import datetime
import os

import discord
import matplotlib.pyplot as plt
import pandas as pd

from commands.base_command import BaseCommand


# has been slashified
class poptimeline(BaseCommand):
    def __init__(self):
        description = f'Shows the steam d2 population timeline'
        params = []
        topic = "Destiny"
        super().__init__(description, params, topic)

    async def handle(self, params, message, mentioned_user, client):
        season_dates = [
            ["2019-10-01", "Shadowkeep"],
            ["2019-12-10", "Season of Dawn"],
            ["2020-03-10", "Season of the Worthy"],
            ["2020-06-09", "Season of Arrivals"],
            ["2020-11-10", "Beyond Light"],
            ["2021-02-09", "Season of the Chosen"],
        ]
        other_dates = [
            ["2019-10-04", "GoS"],
            ["2019-10-29", "PoH"],
            ["2020-01-14", "Corridors of Time"],
            ["2020-04-21", "Guardian Games"],
            ["2020-06-06", "Almighty Live Event"],
            ["2020-08-11", "Solstice of Heroes"],
            ["2020-11-21", "DSC"],
        ]
        other_dates_lower = [
            ["2020-02-04", "Empyrean Foundation"],
            ["2020-07-07", "Moments of Triumph"],
        ]

        # reading data and preparing it
        data = pd.read_pickle('database/steamPlayerData.pickle')
        data['datetime'] = pd.to_datetime(data['datetime'])
        data['players'] = pd.to_numeric(data['players'])

        # Create figure and plot space
        fig, ax = plt.subplots(figsize=(20, 10))
        ax.yaxis.grid(True)

        # filling plot
        ax.plot(
            data['datetime'],
            data['players'],
            "darkred"
        )

        # Set title and labels for axes
        ax.set_title("Destiny 2 - Steam Player Count", fontweight="bold", size=30, pad=20)
        ax.set_xlabel("Date", fontsize=20)
        ax.set_ylabel("Players", fontsize=20)

        # adding nice lines to mark important events
        for dates in season_dates:
            date = datetime.datetime.strptime(dates[0], '%d/%m/%y')
            ax.axvline(date, color="darkgreen")
            ax.text(date + datetime.timedelta(days=2), (max(data['players']) - min(data['players'])) * 1.02 + min(data['players']), dates[1], color="darkgreen", fontweight="bold", bbox=dict(facecolor='white', edgecolor='darkgreen', pad=4))
        for dates in other_dates:
            date = datetime.datetime.strptime(dates[0], '%d/%m/%y')
            ax.axvline(date, color="mediumaquamarine")
            ax.text(date + datetime.timedelta(days=2), (max(data['players']) - min(data['players'])) * 0.95 + min(data['players']), dates[1], color="mediumaquamarine", bbox=dict(facecolor='white', edgecolor='mediumaquamarine', boxstyle='round'))
        for dates in other_dates_lower:
            date = datetime.datetime.strptime(dates[0], '%d/%m/%y')
            ax.axvline(date, color="mediumaquamarine")
            ax.text(date + datetime.timedelta(days=2), (max(data['players']) - min(data['players'])) * 0.90 + min(data['players']), dates[1], color="mediumaquamarine", bbox=dict(facecolor='white', edgecolor='mediumaquamarine', boxstyle='round'))

        # saving file
        title = "players.png"
        plt.savefig(title)

        # sending them the file
        await message.reply(file=discord.File(title))

        # delete file
        os.remove(title)
