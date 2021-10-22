bungie_route = "https://www.bungie.net/"
base_route = bungie_route + "Platform/"
destiny_route = base_route + "Destiny2/"

profile_route = destiny_route + "{system}/Profile/{destiny_id}/"

stat_route = destiny_route + "{system}/Account/{destiny_id}/Stats/"
stat_route_characters = stat_route + "Character/{character_id}/Stats/AggregateActivityStats/"

activities_route = destiny_route + "{system}/Account/{destiny_id}/Character/{character_id}/Stats/Activities/"
pgcr_route = destiny_route + "Stats/PostGameCarnageReport/{instance_id}/"


clan_route = base_route + "GroupV2/"
clan_members_route = clan_route + "{clan_id}/Members/"
clan_admins_route = clan_route + "{clan_id}/Members/"
clan_invite_route = "IndividualInvite/{system}/{destiny_id}/"
clan_get_route = clan_route + "User/{system}/{destiny_id}/0/1/"

manifest_route = destiny_route + "Manifest/"
