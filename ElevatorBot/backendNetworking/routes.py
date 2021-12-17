import os

base_route = f"""http://{os.environ.get("BACKEND_HOST")}:{os.environ.get("BACKEND_PORT")}/"""
destiny_base_route = base_route + "destiny/{guild_id}/{discord_id}/"

# elevators discord guilds
elevator_servers_get = base_route + "elevator/discordServers/get/"  # GET
elevator_servers_add = base_route + "elevator/discordServers/add/{guild_id}/"  # POST
elevator_servers_delete = base_route + "elevator/discordServers/delete/{guild_id}/"  # DELETE

# profile
destiny_profile_route = base_route + "profile/"
destiny_profile_from_discord_id_route = destiny_profile_route + "discord/{discord_id}/"  # GET
destiny_profile_from_destiny_id_route = destiny_profile_route + "destiny/{destiny_id}/"  # GET
destiny_profile_has_token_route = destiny_profile_route + "discord/{discord_id}/has_token/"  # GET
destiny_profile_delete_route = destiny_profile_route + "delete/{discord_id}/"  # DELETE
destiny_profile_registration_role_route = (
    destiny_profile_route + "discord/{discord_id}/guild/{guild_id}/registration_role/"
)  # GET

# account
destiny_account_route = destiny_base_route + "account/"
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


# lfg system
destiny_lfg_route = base_route + "destiny/{guild_id}/lfg/"
destiny_lfg_get_route = destiny_lfg_route + "get/{lfg_id}/"  # GET
destiny_lfg_get_all_route = destiny_lfg_route + "get/all/"  # GET
destiny_lfg_user_get_all_route = destiny_lfg_route + "{discord_id}/get/all/"  # GET
destiny_lfg_update_route = destiny_lfg_route + "{discord_id}/update/{lfg_id}/"  # POST
destiny_lfg_delete_route = destiny_lfg_route + "{discord_id}/delete/{lfg_id}/"  # DELETE
destiny_lfg_create_route = destiny_lfg_route + "{discord_id}/create/"  # POST
destiny_lfg_delete_all_route = destiny_lfg_route + "delete/all/"  # POST


# clan
destiny_clan_route = base_route + "destiny/{guild_id}/clan/"
destiny_clan_get_route = destiny_clan_route + "get/"  # GET
destiny_clan_get_members_route = destiny_clan_route + "get/members/"  # GET
destiny_clan_get_members_no_cache_route = destiny_clan_route + "get/members/no_cache/"  # GET
destiny_clan_search_members_route = destiny_clan_route + "get/members/search/{search_phrase}/"  # GET
destiny_clan_invite_route = destiny_clan_route + "{discord_id}/invite/"  # POST
destiny_clan_kick_route = destiny_clan_route + "{discord_id}/kick/"  # POST
destiny_clan_link_route = destiny_clan_route + "{discord_id}/link/"  # POST
destiny_clan_unlink_route = destiny_clan_route + "{discord_id}/unlink/"  # DELETE

# roles
destiny_role_route = base_route + "destiny/{guild_id}/roles/"
destiny_role_get_all_route = destiny_role_route + "get/all/"  # GET
destiny_role_get_all_user_route = destiny_role_route + "get/all/{discord_id}/"  # GET
destiny_role_get_missing_user_route = destiny_role_route + "get/missing/{discord_id}/"  # GET
destiny_role_get_user_route = destiny_role_route + "get/{role_id}/{discord_id}/"  # GET
destiny_role_create_route = destiny_role_route + "create/"  # POST
destiny_role_update_route = destiny_role_route + "update/{role_id}/"  # POST
destiny_role_delete_all_route = destiny_role_route + "delete/all/"  # DELETE
destiny_role_delete_route = destiny_role_route + "delete/{role_id}/"  # DELETE

# persistent messages
persistent_messages_route = base_route + "persistentMessages/"
persistent_messages_get_route = persistent_messages_route + "{guild_id}/get/{message_name}/"  # GET
persistent_messages_get_all_route = persistent_messages_route + "{guild_id}/get/all/"  # GET
persistent_messages_upsert_route = persistent_messages_route + "{guild_id}/upsert/{message_name}/"  # POST
persistent_messages_delete_route = persistent_messages_route + "{guild_id}/delete/{message_name}/"  # DELETE
persistent_messages_delete_all_route = persistent_messages_route + "{guild_id}/delete/all/"  # DELETE


# polls
polls_route = base_route + "polls/{guild_id}/"
polls_insert_route = polls_route + "{discord_id}/insert/"  # POST
polls_get_route = polls_route + "{discord_id}/{poll_id}/get/{"  # GET
polls_delete_option_route = polls_route + "{{discord_id}/poll_id}/delete_option/{option_name}"  # DELETE
polls_user_input_route = polls_route + "{discord_id}/{poll_id}/user_input/"  # POST
polls_delete_route = polls_route + "{discord_id}/{poll_id}/delete/{"  # DELETE
polls_delete_all_route = polls_route + "delete/all{"  # DELETE


# activities
destiny_activities_route = base_route + "activities/"
destiny_activities_get_all_route = destiny_activities_route + "get/all/"  # GET
destiny_activities_get_grandmaster_route = destiny_activities_route + "get/grandmaster/"  # GET
destiny_activities_last_route = destiny_activities_route + "{guild_id}/{discord_id}/last/"  # GET
destiny_activities_activity_route = destiny_activities_route + "{guild_id}/{discord_id}/activity/"  # GET

# d2 steam player count
steam_player_route = base_route + "steam_players/"
steam_player_get_route = steam_player_route + "get/"  # GET

# weapons
destiny_weapons_route = base_route + "destiny/"
destiny_weapons_get_all_route = destiny_weapons_route + "weapons/"  # GET
destiny_weapons_get_top_route = destiny_weapons_route + "{guild_id}/{discord_id}/weapons/top/"  # GET
destiny_weapons_get_weapon_route = destiny_weapons_route + "{guild_id}/{discord_id}/weapons/weapon/"  # GET

# items
destiny_items_route = base_route + "destiny/items/"
destiny_collectible_name_route = destiny_items_route + "collectible/{collectible_id}/"  # GET
destiny_triumph_name_route = destiny_items_route + "triumph/{triumph_id}/"  # GET
destiny_get_all_lore_route = destiny_items_route + "lore/get/all/"  # GET

# moderation
moderation_route = base_route + "moderation/{guild_id}/{discord_id}/"
moderation_mute = moderation_route + "mute/"  # GET / POST
moderation_warning = moderation_route + "warning/"  # GET / POST
