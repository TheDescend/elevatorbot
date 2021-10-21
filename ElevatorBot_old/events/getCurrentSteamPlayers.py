# class getCurrentSteamPlayers(BaseEvent):
#     def __init__(self):
#         interval_minutes = 60  # Set the interval for this event
#         super().__init__(scheduler_type="interval", interval_minutes=interval_minutes)
#
#     # Override the run() method
#     # It will be called once every {interval_minutes} minutes
#     async def run(self, client):
#         now = datetime.date.today()
#
#         # _get current amount of players
#         rep = await get_json_from_url(
#             url="https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/",
#             headers={"X-API-Key": STEAM_TOKEN},
#             params={"appid": "1085660"},
#             use_cache=False,
#         )
#         number_of_players = int(rep.content["response"]["player_count"])
#
#         await update_d2_steam_players(now, number_of_players)
#
#         # _update the status
#         await bot_status(
#             client,
#             "Steam Player Update",
#             datetime.datetime.now(tz=datetime.timezone.utc),
#         )
