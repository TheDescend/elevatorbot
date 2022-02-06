import os

base_route = f"""http://{os.environ.get("BACKEND_HOST")}:{os.environ.get("BACKEND_PORT")}/"""


# ===========================================================================
# DESTINY

# account
destiny_account_route = base_route + "destiny/account/{guild_id}/{discord_id}/"
destiny_account_name_route = destiny_account_route + "name/"  # GET
destiny_account_solos_route = destiny_account_route + "solos/"  # GET
destiny_account_characters_route = destiny_account_route + "characters/"  # GET
destiny_account_stat_route = destiny_account_route + "stat/"  # POST
destiny_account_stat_characters_route = destiny_account_route + "stat/character/{character_id}/"  # POST
destiny_account_time_route = destiny_account_route + "time/"  # POST
destiny_account_collectible_route = destiny_account_route + "collectible/{collectible_id}/"  # GET
destiny_account_triumph_route = destiny_account_route + "triumph/{triumph_id}/"  # GET
destiny_account_metric_route = destiny_account_route + "metric/{metric_id}/"  # GET
destiny_account_seasonal_challenges_route = destiny_account_route + "seasonal_challenges/"  # GET
destiny_account_triumph_score_route = destiny_account_route + "triumphs/"  # GET
destiny_account_artifact_level_route = destiny_account_route + "artifact/"  # GET
destiny_account_season_pass_level_route = destiny_account_route + "season_pass/"  # GET
destiny_account_consumable_amount_route = destiny_account_route + "consumable/{consumable_id}"  # GET
destiny_account_max_power_route = destiny_account_route + "max_power/"  # GET
destiny_account_vault_space_route = destiny_account_route + "vault_space/"  # GET
destiny_account_bright_dust_route = destiny_account_route + "bright_dust/"  # GET
destiny_account_leg_shards_route = destiny_account_route + "shards/"  # GET
destiny_account_catalysts_route = destiny_account_route + "catalysts/"  # GET
destiny_account_seals_route = destiny_account_route + "seals/"  # GET

# activities
destiny_activities_route = base_route + "destiny/activities/"
destiny_activities_get_all_route = destiny_activities_route + "get/all/"  # GET
destiny_activities_get_grandmaster_route = destiny_activities_route + "get/grandmaster/"  # GET
destiny_activities_last_route = destiny_activities_route + "{guild_id}/{discord_id}/last/"  # POST
destiny_activities_activity_route = destiny_activities_route + "{guild_id}/{discord_id}/activity/"  # POST

# clan
destiny_clan_route = base_route + "destiny/clan/{guild_id}/"
destiny_clan_get_route = destiny_clan_route + "get/"  # GET
destiny_clan_get_members_route = destiny_clan_route + "members/"  # GET
destiny_clan_get_members_no_cache_route = destiny_clan_route + "members/no_cache/"  # GET
destiny_clan_search_members_route = destiny_clan_route + "members/search/{search_phrase}/"  # GET
destiny_clan_invite_route = destiny_clan_route + "invite/{discord_id}/"  # POST
destiny_clan_kick_route = destiny_clan_route + "kick/{discord_id}/"  # POST
destiny_clan_link_route = destiny_clan_route + "{discord_id}/link/"  # POST
destiny_clan_unlink_route = destiny_clan_route + "{discord_id}/unlink/"  # DELETE

# items
destiny_items_route = base_route + "destiny/items/"
destiny_collectible_name_route = destiny_items_route + "collectible/{collectible_id}/"  # GET
destiny_get_all_collectible_route = destiny_items_route + "collectible/get/all/"  # GET
destiny_triumph_name_route = destiny_items_route + "triumph/{triumph_id}/"  # GET
destiny_get_all_triumph_route = destiny_items_route + "triumph/get/all/"  # GET
destiny_get_all_lore_route = destiny_items_route + "lore/get/all/"  # GET

# lfg
destiny_lfg_route = base_route + "destiny/lfg/{guild_id}/"
destiny_lfg_get_route = destiny_lfg_route + "get/{lfg_id}/"  # GET
destiny_lfg_get_all_route = destiny_lfg_route + "get/all/"  # GET
destiny_lfg_user_get_all_route = destiny_lfg_route + "{discord_id}/get/all/"  # GET
destiny_lfg_update_route = destiny_lfg_route + "{discord_id}/update/{lfg_id}/"  # POST
destiny_lfg_delete_route = destiny_lfg_route + "{discord_id}/delete/{lfg_id}/"  # DELETE
destiny_lfg_create_route = destiny_lfg_route + "{discord_id}/create/"  # POST
destiny_lfg_delete_all_route = destiny_lfg_route + "delete/all/"  # POST

# profile
destiny_profile_route = base_route + "destiny/profile/"
destiny_profile_from_discord_id_route = destiny_profile_route + "discord/{discord_id}/"  # GET
destiny_profile_from_destiny_id_route = destiny_profile_route + "destiny/{destiny_id}/"  # GET
destiny_profile_has_token_route = destiny_profile_route + "{discord_id}/has_token/"  # GET
destiny_profile_delete_route = destiny_profile_route + "{discord_id}/delete/"  # DELETE
destiny_profile_registration_role_route = destiny_profile_route + "{guild_id}/{discord_id}/registration_role/"  # GET

# roles
destiny_role_route = base_route + "destiny/roles/{guild_id}/"
destiny_role_get_all_route = destiny_role_route + "get/all/"  # GET
destiny_role_get_all_user_route = destiny_role_route + "{discord_id}/get/all/"  # GET
destiny_role_get_missing_user_route = destiny_role_route + "{discord_id}/get/missing/"  # GET
destiny_role_get_user_route = destiny_role_route + "{discord_id}/get/{role_id}/"  # GET
destiny_role_create_route = destiny_role_route + "create/"  # POST
destiny_role_update_route = destiny_role_route + "update/{role_id}/"  # POST
destiny_role_delete_all_route = destiny_role_route + "delete/all/"  # DELETE
destiny_role_delete_route = destiny_role_route + "delete/{role_id}/"  # DELETE

# steam players
steam_player_route = base_route + "destiny/steam_players/"
steam_player_get_route = steam_player_route + "get/all"  # GET

# weapons
destiny_weapons_route = base_route + "destiny/weapons/"
destiny_weapons_get_all_route = destiny_weapons_route + "get/all/"  # GET
destiny_weapons_get_top_route = destiny_weapons_route + "{guild_id}/{discord_id}/top/"  # POST
destiny_weapons_get_weapon_route = destiny_weapons_route + "{guild_id}/{discord_id}/weapon/"  # POST


# ===========================================================================
# MISC

# elevators discord guilds
elevator_servers_route = base_route + "elevator/discord_servers/"
elevator_servers_get = elevator_servers_route + "get/all/"  # GET
elevator_servers_add = elevator_servers_route + "add/{guild_id}/"  # POST
elevator_servers_delete = elevator_servers_route + "delete/{guild_id}/"  # DELETE

# moderation
moderation_route = base_route + "moderation/{guild_id}/{discord_id}/"
moderation_mute = moderation_route + "mute/"  # GET / POST
moderation_warning = moderation_route + "warning/"  # GET / POST

# persistent messages
persistent_messages_route = base_route + "persistentMessages/{guild_id}/"
persistent_messages_get_route = persistent_messages_route + "get/{message_name}/"  # GET
persistent_messages_get_all_route = persistent_messages_route + "get/all/"  # GET
persistent_messages_upsert_route = persistent_messages_route + "upsert/{message_name}/"  # POST
persistent_messages_delete_route = persistent_messages_route + "delete/"  # POST
persistent_messages_delete_all_route = persistent_messages_route + "delete/all/"  # DELETE

# polls
polls_route = base_route + "polls/{guild_id}/"
polls_insert_route = polls_route + "{discord_id}/insert/"  # POST
polls_get_route = polls_route + "{discord_id}/get/{poll_id}/"  # GET
polls_delete_option_route = polls_route + "{discord_id}/{poll_id}/delete_option/{option_name}"  # DELETE
polls_user_input_route = polls_route + "{discord_id}/{poll_id}/user_input/"  # POST
polls_delete_route = polls_route + "{discord_id}/{poll_id}/delete"  # DELETE
polls_delete_all_route = polls_route + "delete/all{"  # DELETE

# giveaway
giveaway_route = base_route + "giveaway/{guild_id}/{discord_id}/{giveaway_id}/"
giveaway_get = giveaway_route + "get/"  # GET
giveaway_create = giveaway_route + "create/"  # POST
giveaway_insert = giveaway_route + "insert/"  # POST
giveaway_remove = giveaway_route + "remove/"  # POST
