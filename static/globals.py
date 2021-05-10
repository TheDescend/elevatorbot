# bot dev channel id and clan id are in static.config.py

""" Role IDs """
admin_role_id = 670383817147809814
dev_role_id = 670397357120159776
mod_role_id = 671261823584043040
member_role_id = 769612980978843668
registered_role_id = 670396064007979009
not_registered_role_id = 670396109088358437
clan_role_id = 670384239489056768
muted_role_id = 681944329698541585
role_ban_id = 794685157712855040

divider_misc_role_id = 670395920327639085
divider_achievement_role_id = 670385837044662285
divider_raider_role_id = 670385313994113025
divider_legacy_role_id = 776854211585376296

among_us_role_id = 750409552075423753
barotrauma_role_id = 738438622553964636
gta_role_id = 709120893728718910
valorant_role_id = 709378171832893572
lol_role_id = 756076447881363486
eft_role_id = 800862253279608854


""" Channel IDs """
admin_discussions_channel_id = 671264040974024705
admin_workboard_channel_id = 769608204618563625
steam_join_codes_channel_id = 701060424535113738


""" Emoji IDs """
thumps_up_emoji_id = 754946723612196975
thumps_down_emoji_id = 754946723503276124
yes_emoji_id = 768908985557844028
enter_emoji_id = 768906489103384688
destiny_emoji_id = 768906489472876574

among_us_emoji_id = 751020830376591420
barotrauma_emoji_id = 756077724870901830
gta_emoji_id = 751020831382962247
valorant_emoji_id = 751020830414209064
lol_emoji_id = 756076309527920661
eft_emoji_id = 800866459286503445

warlock_emoji_id = 830747907488612402
hunter_emoji_id = 830747907829006346
titan_emoji_id = 830747907576823808
light_level_icon_emoji_id = 830750430816108564


""" Persistent Messages """
other_game_roles = [
    (among_us_emoji_id, among_us_role_id),
    (barotrauma_emoji_id, barotrauma_role_id),
    (gta_emoji_id, gta_role_id),
    (valorant_emoji_id, valorant_role_id),
    (lol_emoji_id, lol_role_id),
    (eft_emoji_id, eft_role_id),
]
clan_join_request = [
    destiny_emoji_id
]
tournament = [
    destiny_emoji_id
]


# guild ids for testing purposes. If not in it, command can take up to an hour to load
guild_ids = [280456587464933376]