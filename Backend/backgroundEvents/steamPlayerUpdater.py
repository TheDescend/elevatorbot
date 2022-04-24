from Backend.backgroundEvents.base import BaseEvent
from Backend.crud import d2_steam_players
from Backend.database.base import acquire_db_session, is_test_mode
from Backend.networking.http import NetworkBase
from Shared.functions.readSettingsFile import get_setting


class SteamPlayerUpdater(BaseEvent):
    """Check for Steam Players hourly"""

    def __init__(self):
        interval_minutes = 60
        super().__init__(scheduler_type="interval", interval_minutes=interval_minutes)

    async def run(self):
        async with acquire_db_session() as db:
            # init api connection
            headers = {"X-API-Key": get_setting("STEAM_APPLICATION_API_KEY")}
            steam_api = NetworkBase(db=db)

            # get current amount of players
            route = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"
            params = {"appid": "1085660"}
            current_players = await steam_api.get(route=route, params=params, headers=headers)
            number_of_players = int(current_players.content["response"]["player_count"])

            # update the db info
            if not is_test_mode():
                await d2_steam_players.upsert(db=db, player_count=number_of_players)
