from sqlalchemy import (
    ARRAY,
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Integer,
    JSON,
    Numeric,
    SmallInteger,
    Text,
    text,
)
from sqlalchemy.engine import Engine

from Backend.database.base import Base, is_test_mode


""" All table models are in here, allowing for easy generation """

################################################################
# Authentication


class BackendUser(Base):
    __tablename__ = "backendUser"

    user_name = Column(Text, primary_key=True)
    hashed_password = Column(Text)  # this includes salt
    allowed_scopes = Column(ARRAY(Text()))  # where access is allowed. Empty for full access maybe?
    has_write_permission = Column(Boolean)
    has_read_permission = Column(Boolean)
    disabled = Column(Boolean, default=False)


################################################################
# Activities


class PgcrActivitiesFailToGet(Base):
    __tablename__ = "pgcrActivitiesFailToGet"

    id = Column("instanceid", BigInteger, primary_key=True)
    date = Column("period", DateTime)


class PgcrActivity(Base):
    __tablename__ = "pgcrActivities"

    id = Column("instanceid", BigInteger, primary_key=True)
    reference_id = Column("referenceid", BigInteger)
    director_activity_hash = Column("directoractivityhash", BigInteger)
    date = Column("period", DateTime)
    starting_phase_index = Column("startingphaseindex", SmallInteger)
    mode = Column("mode", SmallInteger)
    modes = Column("modes", ARRAY(SmallInteger()))
    is_private = Column("isprivate", Boolean)
    membership_type = Column("membershiptype", SmallInteger)


class PgcrActivitiesUsersStat(Base):
    __tablename__ = "pgcrActivitiesUsersStats"

    id = Column("instanceid", BigInteger, primary_key=True, nullable=False)
    system = Column("membershipid", BigInteger, primary_key=True, nullable=False)
    character_id = Column("characterid", BigInteger, primary_key=True, nullable=False)
    character_class = Column("characterclass", Text)
    character_level = Column("characterlevel", SmallInteger)
    membership_type = Column("membershiptype", SmallInteger)
    light_level = Column("lightlevel", Integer)
    emblem_hash = Column("emblemhash", BigInteger)
    standing = Column("standing", SmallInteger)
    assists = Column("assists", Integer)
    completed = Column("completed", SmallInteger)
    deaths = Column("deaths", Integer)
    kills = Column("kills", Integer)
    opponents_defeated = Column("opponentsdefeated", Integer)
    efficiency = Column("efficiency", Numeric)
    kills_deaths_ratio = Column("killsdeathsratio", Numeric)
    kills_deaths_assists = Column("killsdeathsassists", Numeric)
    score = Column("score", Integer)
    activity_duration_seconds = Column("activitydurationseconds", Integer)
    completion_reason = Column("completionreason", SmallInteger)
    start_seconds = Column("startseconds", Integer)
    time_played_seconds = Column("timeplayedseconds", Integer)
    player_count = Column("playercount", SmallInteger)
    team_score = Column("teamscore", Integer)
    precision_kills = Column("precisionkills", Integer)
    weapon_kills_grenade = Column("weaponkillsgrenade", Integer)
    weapon_kills_melee = Column("weaponkillsmelee", Integer)
    weapon_kills_super = Column("weaponkillssuper", Integer)
    weapon_kills_ability = Column("weaponkillsability", Integer)


class PgcrActivitiesUsersStatsWeapon(Base):
    __tablename__ = "pgcrActivitiesUsersStatsWeapons"

    id = Column("instanceid", BigInteger, primary_key=True, nullable=False)
    character_id = Column("characterid", BigInteger, primary_key=True, nullable=False)
    system = Column("membershipid", BigInteger, primary_key=True, nullable=False)
    weapon_id = Column("weaponid", BigInteger, primary_key=True, nullable=False)
    unique_weapon_kills = Column("uniqueweaponkills", Integer)
    unique_weapon_precision_kills = Column("uniqueweaponprecisionkills", Integer)


################################################################
# Userdata


class DiscordGuardiansToken(Base):
    __tablename__ = "discordGuardiansToken"

    discord_id = Column("discordsnowflake", BigInteger, nullable=False, primary_key=True)
    destiny_id = Column("destinyid", BigInteger, nullable=False, unique=True)
    system = Column("systemid", Integer, nullable=False)
    token = Column("token", Text, nullable=False)
    refresh_token = Column("__refresh_token", Text, nullable=False)
    token_expiry = Column("token_expiry", DateTime, nullable=False)
    refresh_token_expiry = Column("refresh_token_expiry", DateTime, nullable=False)
    signup_date = Column("signupdate", Date, nullable=False)
    signup_server_id = Column("serverid", BigInteger, nullable=False)
    steam_join_id = Column("steamjoinid", BigInteger, nullable=True)
    activities_last_updated = Column(
        "activitieslastupdated",
        DateTime,
        nullable=False,
        server_default=text("'2000-01-01 00:00:00'::timestamp without time zone"),
    )


class DestinyClanLinks(Base):
    __tablename__ = "destinyClanLinks"

    discord_guild_id = Column(BigInteger, primary_key=True, nullable=False)
    destiny_clan_id = Column(BigInteger, unique=True, nullable=False)
    link_date = Column(DateTime, nullable=False)
    linked_by_discord_id = Column(BigInteger, nullable=False)


class OwnedEmblem(Base):
    __tablename__ = "ownedEmblems"

    destiny_id = Column(BigInteger, primary_key=True)
    emblem_hash = Column(BigInteger)


################################################################
# Destiny Manifest


class ManifestVersion(Base):
    __tablename__ = "versions"

    name = Column(Text, primary_key=True)
    version = Column(Text)


class DestinyActivityDefinition(Base):
    __tablename__ = "destinyActivityDefinition"

    id = Column("referenceid", BigInteger, primary_key=True)
    description = Column("description", Text)
    name = Column("name", Text)
    activity_level = Column("activitylevel", SmallInteger)
    activity_light_level = Column("activitylightlevel", Integer)
    destination_hash = Column("destinationhash", BigInteger)
    place_hash = Column("placehash", BigInteger)
    activity_type_hash = Column("activitytypehash", BigInteger)
    is_pvp = Column("ispvp", Boolean)
    direct_activity_mode_hash = Column("directactivitymodehash", BigInteger)
    direct_activity_mode_type = Column("directactivitymodetype", SmallInteger)
    activity_mode_hashes = Column("activitymodehashes", ARRAY(BigInteger()))
    activity_mode_types = Column("activitymodetypes", ARRAY(SmallInteger()))


class DestinyActivityModeDefinition(Base):
    __tablename__ = "destinyActivityModeDefinition"

    id = Column("referenceid", SmallInteger, primary_key=True)
    description = Column("description", Text)
    name = Column("name", Text)
    hash = Column("hash", BigInteger)
    activity_mode_category = Column("activitymodecategory", SmallInteger)
    is_team_based = Column("isteambased", Boolean)
    friendly_name = Column("friendlyname", Text)


class DestinyActivityTypeDefinition(Base):
    __tablename__ = "destinyActivityTypeDefinition"

    id = Column("referenceid", BigInteger, primary_key=True)
    description = Column("description", Text)
    name = Column("name", Text)


class DestinyCollectibleDefinition(Base):
    __tablename__ = "destinyCollectibleDefinition"

    id = Column("referenceid", BigInteger, primary_key=True)
    description = Column("description", Text)
    name = Column("name", Text)
    source_hash = Column("sourcehash", BigInteger)
    item_hash = Column("itemhash", BigInteger)
    parent_node_hashes = Column("parentnodehashes", ARRAY(BigInteger()))


class DestinyInventoryBucketDefinition(Base):
    __tablename__ = "destinyInventoryBucketDefinition"

    id = Column("referenceid", BigInteger, primary_key=True)
    description = Column("description", Text)
    name = Column("name", Text)
    category = Column("category", SmallInteger)
    item_count = Column("itemcount", SmallInteger)
    location = Column("location", SmallInteger)


class DestinyInventoryItemDefinition(Base):
    __tablename__ = "destinyInventoryItemDefinition"

    id = Column("referenceid", BigInteger, primary_key=True)
    description = Column("description", Text)
    name = Column("name", Text)
    class_type = Column("classtype", SmallInteger)
    bucket_type_hash = Column("buckettypehash", BigInteger)
    tier_type_hash = Column("tiertypehash", BigInteger)
    tier_type_name = Column("tiertypename", Text)
    equippable = Column("equippable", Boolean)


class DestinyPresentationNodeDefinition(Base):
    __tablename__ = "destinyPresentationNodeDefinition"

    id = Column("referenceid", BigInteger, primary_key=True)
    description = Column("description", Text)
    name = Column("name", Text)
    objective_hash = Column("objectivehash", BigInteger)
    presentation_node_type = Column("presentationnodetype", SmallInteger)
    children_presentation_node_hash = Column("childrenpresentationnodehash", ARRAY(BigInteger()))
    children_collectible_hash = Column("childrencollectiblehash", ARRAY(BigInteger()))
    children_record_hash = Column("childrenrecordhash", ARRAY(BigInteger()))
    children_metric_hash = Column("childrenmetrichash", ARRAY(BigInteger()))
    parent_node_hashes = Column("parentnodehashes", ARRAY(BigInteger()))
    index = Column("index", SmallInteger)
    redacted = Column("redacted", Boolean)


class DestinyRecordDefinition(Base):
    __tablename__ = "destinyRecordDefinition"

    id = Column("referenceid", BigInteger, primary_key=True)
    description = Column("description", Text)
    name = Column("name", Text)
    has_title = Column("hastitle", Boolean)
    title_name = Column("titlename", Text)
    objective_hashes = Column("objectivehashes", ARRAY(BigInteger()))
    score_value = Column("scorevalue", Integer)
    parent_node_hashes = Column("parentnodehashes", ARRAY(BigInteger()))


################################################################
# LFG System


class LfgMessage(Base):
    __tablename__ = "lfgMessages"

    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger)
    channel_id = Column(BigInteger)
    message_id = Column(BigInteger)
    author_id = Column(BigInteger)
    activity = Column(Text)
    description = Column(Text)
    start_time = Column(DateTime(True))
    max_joined_members = Column(Integer)
    joined_members = Column(ARRAY(BigInteger()))
    alternate_members = Column(ARRAY(BigInteger()))
    creation_time = Column(DateTime(True))
    voice_channel_id = Column(BigInteger)


class LfgUser(Base):
    __tablename__ = "lfgUsers"

    user_id = Column(BigInteger, primary_key=True)
    blacklisted_members = Column(ARRAY(BigInteger()))


################################################################
# Misc


class D2SteamPlayer(Base):
    __tablename__ = "d2SteamPlayers"

    date = Column("dateobj", DateTime, primary_key=True)
    number_of_players = Column("numberofplayers", Integer)


class Poll(Base):
    __tablename__ = "polls"

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    description = Column(Text)
    data = Column(JSON)
    author_id = Column(BigInteger)
    guild_id = Column(BigInteger)
    channel_id = Column(BigInteger)
    message_id = Column(BigInteger)


class RssFeedItem(Base):
    __tablename__ = "rssFeedItems"

    id = Column(Text, primary_key=True)


class PersistentMessage(Base):
    __tablename__ = "persistentMessages"

    message_name = Column("messagename", Text, primary_key=True, nullable=False)
    guild_id = Column("guildid", BigInteger, primary_key=True, nullable=False)
    channel_id = Column("channelid", BigInteger)
    message_id = Column("messageid", BigInteger)
    reaction_ids = Column("reactionsidlist", ARRAY(BigInteger()))


# _insert all tables
_TABLES_CREATED = False


async def create_tables(engine: Engine):
    global _TABLES_CREATED

    if not _TABLES_CREATED:
        _TABLES_CREATED = True

        async with engine.begin() as connection:
            if is_test_mode():
                await connection.run_sync(Base.metadata.drop_all)

            await connection.run_sync(Base.metadata.create_all)
