import os


base_route = f"""http://{os.environ.get("BACKEND_HOST")}:{os.environ.get("BACKEND_PORT")}/"""

base_id_route = base_route + "{guild_id}/{discord_id}/"
base_destiny_path = base_id_route + "destiny/"

destiny_profile_from_discord_id_route = base_route + "profile/discord/{discord_id}/"
destiny_profile_from_destiny_id_route = base_route + "profile/destiny/{destiny_id}/"
