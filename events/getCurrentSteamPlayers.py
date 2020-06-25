from static.config import STEAM_TOKEN

from events.base_event import BaseEvent

from datetime import datetime
import pandas as pd
import os
import requests


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
            rep = self.steamAPIrequest('https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/')
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


    # d2 steam appid = 1085660; steamAPI_URL = "https://api.steampowered.com"
    def steamAPIrequest(self, requestURL):
        headers = {'X-API-Key': STEAM_TOKEN}
        params = {'appid': '1085660'}
        session = requests.Session()

        """ Grabs JSON from the specified URL (no oauth)"""
        for i in range(3):
            try:
                if 'None' in requestURL:
                    break
                r = session.get(url=requestURL, headers=headers, params=params)
            except Exception as e:
                print('Exception was caught: ' + repr(e))
                continue

            if r.status_code == 200:
                returnval = r.json()
                return returnval
            elif r.status_code == 404:
                print('no stats found')
                return None
            elif r.status_code == 429:
                print('too many steam requests')
                return None
            elif r.status_code == 500:
                print(f'bad request for {requestURL}')
            elif r.status_code == 503:
                print(f'steam is ded')
                return None
            else:
                print('failed with code ' + str(r.status_code) + ' servers might be busy')
        print('request failed 3 times')
        return None