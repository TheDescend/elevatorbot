import os


base_route = f"""http://{os.environ.get("BACKEND_HOST")}:{os.environ.get("BACKEND_PORT")}/"""
destiny_base_route = base_route + "destiny/{guild_id}/{discord_id}/"

destiny_profile_from_discord_id_route = base_route + "profile/discord/{discord_id}/"
destiny_profile_from_destiny_id_route = base_route + "profile/destiny/{destiny_id}/"
destiny_profile_delete_route = base_route + "profile/delete/{discord_id}/"

destiny_account_route = destiny_base_route + "account/"

destiny_name_route = destiny_account_route + "name/"

destiny_clan_route = destiny_base_route + "clan/"
destiny_clan_get_route = destiny_clan_route + "get/"
destiny_clan_get_members_route = destiny_clan_route + "get/members/"
destiny_clan_search_members_route = destiny_clan_route + "get/members/search/{search_phrase}/"
destiny_clan_invite_route = destiny_clan_route + "invite/{to_invite_discord_id}/"
destiny_clan_link_route = destiny_clan_route + "link/"
destiny_clan_unlink_route = destiny_clan_route + "unlink/"
