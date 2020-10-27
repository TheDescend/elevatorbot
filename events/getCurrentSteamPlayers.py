import os
from datetime import datetime

import pandas as pd

from events.base_event import BaseEvent
from functions.network import getJSONfromURL
from static.config import STEAM_TOKEN


class getCurrentSteamPlayers(BaseEvent):
    def __init__(self):
        interval_minutes = 60  # Set the interval for this event
        super().__init__(interval_minutes)


    # Override the run() method
    # It will be called once every {interval_minutes} minutes
    async def run(self, client):
        if not os.path.exists('database/steamPlayerData.pickle'):
            steamdf = pd.DataFrame(columns=["datetime", "players"])
        else:
            steamdf = pd.read_pickle('database/steamPlayerData.pickle')
        now = datetime.now()

        try:
            # get current amount of players
            rep = await getJSONfromURL(
                requestURL='https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/',
                headers={'X-API-Key': STEAM_TOKEN},
                params={'appid': '1085660'}
            )
            players = int(rep['response']["player_count"])

            entry = {
                'datetime': now,
                'players': players
            }

            old_time = steamdf["datetime"].iloc[-1]
            old_players = steamdf["players"].iloc[-1]

            # adding that info to the database, should be be a new day / higher than the last entry for the day
            if old_time.date() == now.date():
                if old_players < players:
                    steamdf.drop(steamdf.tail(1).index, inplace=True)
                    steamdf = steamdf.append(entry, ignore_index=True)
                    steamdf.to_pickle('database/steamPlayerData.pickle')
            else:
                steamdf = steamdf.append(entry, ignore_index=True)
                steamdf.to_pickle('database/steamPlayerData.pickle')

        except:
            print("error getting current steam players")