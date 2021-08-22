import os


base_route = f"""http://{os.environ.get("BACKEND_HOST")}:{os.environ.get("BACKEND_PORT")}/"""

destiny_profile_from_discord_id_route = base_route + "profile/discord/{discord_id}/"
destiny_profile_from_destiny_id_route = base_route + "profile/destiny/{destiny_id}/"
destiny_profile_delete_route = base_route + "profile/delete/{discord_id}/"

destiny_account_route = base_route + "destiny/{guild_id}/{discord_id}/account/"

destiny_name_route = destiny_account_route + "name/"
