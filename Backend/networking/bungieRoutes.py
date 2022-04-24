bungie_route = "https://www.bungie.net/"
base_route = bungie_route + "Platform/"
destiny_route = base_route + "Destiny2/"

auth_route = base_route + "app/oauth/token/"

profile_route = destiny_route + "{system}/Profile/{destiny_id}/"
item_route = profile_route + "Item/{item_instance_id}/"

stat_route = destiny_route + "{system}/Account/{destiny_id}/Stats/"
stat_route_characters = stat_route + "Character/{character_id}/Stats/AggregateActivityStats/"

activities_route = destiny_route + "{system}/Account/{destiny_id}/Character/{character_id}/Stats/Activities/"

clan_route = base_route + "GroupV2/"
clan_user_route = clan_route + "User/{system}/{destiny_id}/0/1/"
clan_members_route = clan_route + "{clan_id}/Members/"
clan_admins_route = clan_route + "{clan_id}/AdminsAndFounder/"
clan_invite_route = clan_members_route + "IndividualInvite/{system}/{destiny_id}/"
clan_kick_route = clan_members_route + "{system}/{destiny_id}/Kick/"
clan_get_route = clan_route + "{clan_id}/"

# routes without user data
manifest_route = destiny_route + "Manifest/"
pgcr_route = destiny_route + "Stats/PostGameCarnageReport/{instance_id}/"
