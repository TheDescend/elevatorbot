from Backend.backgroundEvents.base import BaseEvent
from Backend.crud import d2_steam_players
from Backend.database.base import get_async_session
from Backend.networking.bungieApi import BungieApi
from settings import STEAM_APPLICATION_API_KEY


class SteamPlayerUpdater(BaseEvent):
    """Check for Steam Players hourly"""

    def __init__(self):
        interval_minutes = 60
        super().__init__(scheduler_type="interval", interval_minutes=interval_minutes)

    async def run(self):
        async with get_async_session().begin() as db:
            # init api connection
            headers = {"X-API-Key": STEAM_APPLICATION_API_KEY}
            steam_api = BungieApi(db=db, user=None, headers=headers)

            # get current amount of players
            route = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"
            params = {"appid": "1085660"}
            current_players = await steam_api.get(route=route, params=params, use_cache=False)
            number_of_players = int(current_players.content["response"]["player_count"])

            # update the db info
            await d2_steam_players.upsert(db=db, player_count=number_of_players)
