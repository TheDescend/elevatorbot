import os
import datetime

import pandas as pd

from events.base_event import BaseEvent
from functions.database import update_d2_steam_players
from functions.network import getJSONfromURL
from functions.persistentMessages import botStatus
from static.config import STEAM_TOKEN


class getCurrentSteamPlayers(BaseEvent):
    def __init__(self):
        interval_minutes = 60  # Set the interval for this event
        super().__init__(scheduler_type="interval", interval_minutes=interval_minutes)

    # Override the run() method
    # It will be called once every {interval_minutes} minutes
    async def run(self, client):
        now = datetime.date.today()

        # get current amount of players
        rep = await getJSONfromURL(
            requestURL='https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/',
            headers={'X-API-Key': STEAM_TOKEN},
            params={'appid': '1085660'}
        )
        number_of_players = int(rep['response']["player_count"])

        await update_d2_steam_players(now, number_of_players)

        # update the status
        await botStatus(client, "Steam Player Update", datetime.datetime.now(tz=datetime.timezone.utc))
