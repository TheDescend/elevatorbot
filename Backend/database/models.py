import datetime

from sqlalchemy import (
    ARRAY,
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    SmallInteger,
    Text,
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import relationship

from Backend.database.base import Base, is_test_mode


""" All table models are in here, allowing for easy generation """

################################################################
# Authentication


class BackendUser(Base):
    __tablename__ = "backendUser"

    user_name = Column(Text, nullable=False, primary_key=True)
    hashed_password = Column(Text, nullable=False)  # this includes salt
    allowed_scopes = Column(ARRAY(Text()))  # where access is allowed. Empty for full access maybe?
    has_write_permission = Column(Boolean, nullable=False)
    has_read_permission = Column(Boolean, nullable=False)
    disabled = Column(Boolean, nullable=False, default=False)


################################################################
# Activities


class ActivitiesFailToGet(Base):
    __tablename__ = "activitiesFailToGet"

    instance_id = Column(BigInteger, nullable=False, primary_key=True)
    period = Column(DateTime(timezone=True), nullable=False)


class Activities(Base):
    __tablename__ = "activities"

    instance_id = Column(BigInteger, nullable=False, primary_key=True)
    period = Column(DateTime(timezone=True), nullable=False)
    reference_id = Column(BigInteger, nullable=False)
    director_activity_hash = Column(BigInteger, nullable=False)
    starting_phase_index = Column(SmallInteger, nullable=False)
    mode = Column(SmallInteger, nullable=False)
    modes = Column(ARRAY(SmallInteger()), nullable=False)
    is_private = Column(Boolean, nullable=False)
    system = Column(SmallInteger, nullable=False)

    users = relationship(
        "ActivitiesUsersStats", back_populates="activities", cascade="all, delete", passive_deletes=True
    )


class ActivitiesUsersStats(Base):
    __tablename__ = "activitiesUsersStats"

    id = Column(BigInteger, nullable=False, primary_key=True)

    destiny_id = Column(BigInteger, nullable=False)
    character_id = Column(BigInteger, nullable=False)
    character_class = Column(Text, nullable=False)
    character_level = Column(SmallInteger, nullable=False)
    system = Column(SmallInteger, nullable=False)
    light_level = Column(Integer, nullable=False)
    emblem_hash = Column(BigInteger, nullable=False)
    standing = Column(SmallInteger, nullable=False)
    assists = Column(Integer, nullable=False)
    completed = Column(SmallInteger, nullable=False)
    deaths = Column(Integer, nullable=False)
    kills = Column(Integer, nullable=False)
    opponents_defeated = Column(Integer, nullable=False)
    efficiency = Column(Numeric, nullable=False)
    kills_deaths_ratio = Column(Numeric, nullable=False)
    kills_deaths_assists = Column(Numeric, nullable=False)
    score = Column(Integer, nullable=False)
    activity_duration_seconds = Column(Integer, nullable=False)
    completion_reason = Column(SmallInteger, nullable=False)
    start_seconds = Column(Integer, nullable=False)
    time_played_seconds = Column(Integer, nullable=False)
    player_count = Column(SmallInteger, nullable=False)
    team_score = Column(Integer, nullable=False)
    precision_kills = Column(Integer, nullable=False)
    weapon_kills_grenade = Column(Integer, nullable=False)
    weapon_kills_melee = Column(Integer, nullable=False)
    weapon_kills_super = Column(Integer, nullable=False)
    weapon_kills_ability = Column(Integer, nullable=False)

    activity_instance_id = Column(BigInteger, ForeignKey(Activities.instance_id))
    activity = relationship("Activities", back_populates="activitiesUsersStats")

    weapons = relationship(
        "ActivitiesUsersStatsWeapons",
        back_populates="activitiesUsersStats",
        cascade="all, delete",
        passive_deletes=True,
    )


class ActivitiesUsersStatsWeapons(Base):
    __tablename__ = "activitiesUsersStatsWeapons"

    id = Column(BigInteger, nullable=False, primary_key=True)

    weapon_id = Column(BigInteger, nullable=False)
    unique_weapon_kills = Column(Integer, nullable=False)
    unique_weapon_precision_kills = Column(Integer, nullable=False)

    user_id = Column(BigInteger, ForeignKey(ActivitiesUsersStats.id))
    user = relationship("ActivitiesUsersStats", back_populates="activitiesUsersStatsWeapons")


################################################################
# Userdata


class DiscordUsers(Base):
    __tablename__ = "discordUsers"

    discord_id = Column(BigInteger, nullable=False, primary_key=True)

    destiny_id = Column(BigInteger, nullable=False, unique=True)
    system = Column(Integer, nullable=False)
    token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
    token_expiry = Column(DateTime(timezone=True), nullable=False)
    refresh_token_expiry = Column(DateTime(timezone=True), nullable=False)

    signup_date = Column(DateTime(timezone=True), nullable=False)
    signup_server_id = Column(BigInteger, nullable=False)

    activities_last_updated = Column(
        DateTime(timezone=True), nullable=False, default=datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)
    )


class DestinyClanLinks(Base):
    __tablename__ = "destinyClanLinks"

    discord_guild_id = Column(BigInteger, primary_key=True, nullable=False)
    destiny_clan_id = Column(BigInteger, unique=True, nullable=False)
    link_date = Column(DateTime(timezone=True), nullable=False)
    linked_by_discord_id = Column(BigInteger, nullable=False)


################################################################
# Destiny Manifest


class ManifestVersion(Base):
    __tablename__ = "versions"

    name = Column(Text, nullable=False, primary_key=True)
    version = Column(Text, nullable=False)


class DestinyActivityDefinition(Base):
    __tablename__ = "destinyActivityDefinition"

    reference_id = Column(BigInteger, nullable=False, primary_key=True)
    description = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    activity_level = Column(SmallInteger, nullable=False)
    activity_light_level = Column(Integer, nullable=False)
    destination_hash = Column(BigInteger, nullable=False)
    place_hash = Column(BigInteger, nullable=False)
    activity_type_hash = Column(BigInteger, nullable=False)
    is_pvp = Column(Boolean, nullable=False)
    direct_activity_mode_hash = Column(BigInteger, nullable=False)
    direct_activity_mode_type = Column(SmallInteger, nullable=False)
    activity_mode_hashes = Column(ARRAY(BigInteger()), nullable=False)
    activity_mode_types = Column(ARRAY(SmallInteger()), nullable=False)


class DestinyActivityModeDefinition(Base):
    __tablename__ = "destinyActivityModeDefinition"

    reference_id = Column(SmallInteger, nullable=False, primary_key=True)
    description = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    hash = Column(BigInteger, nullable=False)
    activity_mode_category = Column(SmallInteger, nullable=False)
    is_team_based = Column(Boolean, nullable=False)
    friendly_name = Column(Text, nullable=False)


class DestinyActivityTypeDefinition(Base):
    __tablename__ = "destinyActivityTypeDefinition"

    reference_id = Column(BigInteger, nullable=False, primary_key=True)
    description = Column(Text, nullable=False)
    name = Column(Text, nullable=False)


class DestinyCollectibleDefinition(Base):
    __tablename__ = "destinyCollectibleDefinition"

    reference_id = Column(BigInteger, nullable=False, primary_key=True)
    description = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    source_hash = Column(BigInteger, nullable=False)
    item_hash = Column(BigInteger, nullable=False)
    parent_node_hashes = Column(ARRAY(BigInteger()), nullable=False)


class DestinyInventoryBucketDefinition(Base):
    __tablename__ = "destinyInventoryBucketDefinition"

    reference_id = Column(BigInteger, nullable=False, primary_key=True)
    description = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    category = Column(SmallInteger, nullable=False)
    item_count = Column(SmallInteger, nullable=False)
    location = Column(SmallInteger, nullable=False)


class DestinyInventoryItemDefinition(Base):
    __tablename__ = "destinyInventoryItemDefinition"

    reference_id = Column(BigInteger, nullable=False, primary_key=True)
    description = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    class_type = Column(SmallInteger, nullable=False)
    bucket_type_hash = Column(BigInteger, nullable=False)
    tier_type_hash = Column(BigInteger, nullable=False)
    tier_type_name = Column(Text, nullable=False)
    equippable = Column(Boolean, nullable=False)


class DestinyPresentationNodeDefinition(Base):
    __tablename__ = "destinyPresentationNodeDefinition"

    reference_id = Column(BigInteger, nullable=False, primary_key=True)
    description = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    objective_hash = Column(BigInteger, nullable=False)
    presentation_node_type = Column(SmallInteger, nullable=False)
    children_presentation_node_hash = Column(ARRAY(BigInteger()), nullable=False)
    children_collectible_hash = Column(ARRAY(BigInteger()), nullable=False)
    children_record_hash = Column(ARRAY(BigInteger()), nullable=False)
    children_metric_hash = Column(ARRAY(BigInteger()), nullable=False)
    parent_node_hashes = Column(ARRAY(BigInteger()), nullable=False)
    index = Column(SmallInteger, nullable=False)
    redacted = Column(Boolean, nullable=False)


class DestinyRecordDefinition(Base):
    __tablename__ = "destinyRecordDefinition"

    reference_id = Column(BigInteger, nullable=False, primary_key=True)
    description = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    has_title = Column(Boolean, nullable=False)
    title_name = Column(Text, nullable=False)
    objective_hashes = Column(ARRAY(BigInteger()), nullable=False)
    score_value = Column(Integer, nullable=False)
    parent_node_hashes = Column(ARRAY(BigInteger()), nullable=False)


################################################################
# LFG System


class LfgMessage(Base):
    __tablename__ = "lfgMessages"

    id = Column(Integer, nullable=False, primary_key=True)

    guild_id = Column(BigInteger, nullable=False)
    channel_id = Column(BigInteger, nullable=False)
    message_id = Column(BigInteger, nullable=False)
    author_id = Column(BigInteger, nullable=False)

    activity = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    start_time = Column(DateTime(True), nullable=False)
    max_joined_members = Column(Integer, nullable=False)
    joined_members = Column(ARRAY(BigInteger()), nullable=False)
    alternate_members = Column(ARRAY(BigInteger()), nullable=False)

    creation_time = Column(DateTime(True), nullable=False)
    voice_channel_id = Column(BigInteger, nullable=True)


class LfgUser(Base):
    __tablename__ = "lfgUsers"

    user_id = Column(BigInteger, nullable=False, primary_key=True)
    blacklisted_members = Column(ARRAY(BigInteger()), nullable=False)


################################################################
# Misc


class D2SteamPlayer(Base):
    __tablename__ = "d2SteamPlayers"

    date = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    number_of_players = Column(Integer, nullable=False)


class Poll(Base):
    __tablename__ = "polls"

    id = Column(Integer, nullable=False, primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    data = Column(JSON, nullable=False)

    author_id = Column(BigInteger, nullable=False)
    guild_id = Column(BigInteger, nullable=False)
    channel_id = Column(BigInteger, nullable=False)
    message_id = Column(BigInteger, nullable=False)


class RssFeedItem(Base):
    __tablename__ = "rssFeedItems"

    id = Column(Text, nullable=False, primary_key=True)


class PersistentMessage(Base):
    __tablename__ = "persistentMessages"

    message_name = Column(Text, nullable=False, primary_key=True)

    guild_id = Column(BigInteger, nullable=False, primary_key=True)
    channel_id = Column(BigInteger, nullable=False)
    message_id = Column(BigInteger, nullable=False)


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
