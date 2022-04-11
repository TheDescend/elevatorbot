from __future__ import annotations

import asyncio
from typing import Optional

from sqlalchemy import (
    ARRAY,
    JSON,
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    Text,
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import backref, relationship
from sqlalchemy.schema import Table

from Backend.database.base import Base, is_test_mode
from Shared.functions.helperFunctions import get_min_with_tz, get_now_with_tz

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
# Destiny Data


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

    users: list[ActivitiesUsers] = relationship(
        "ActivitiesUsers",
        back_populates="activity",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )


class ActivitiesUsers(Base):
    __tablename__ = "activitiesUsers"

    id = Column(BigInteger, nullable=False, primary_key=True)

    destiny_id = Column(BigInteger, nullable=False)
    bungie_name = Column(Text, nullable=False)
    character_id = Column(BigInteger, nullable=False)
    character_class = Column(Text, nullable=True)
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
    activity: list[Activities] = relationship("Activities", back_populates="users", lazy="selectin")

    weapons: list[ActivitiesUsersWeapons] = relationship(
        "ActivitiesUsersWeapons",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )


class ActivitiesUsersWeapons(Base):
    __tablename__ = "activitiesUsersWeapons"

    id = Column(BigInteger, nullable=False, primary_key=True)

    weapon_id = Column(BigInteger, nullable=False)
    unique_weapon_kills = Column(Integer, nullable=False)
    unique_weapon_precision_kills = Column(Integer, nullable=False)

    user_id = Column(BigInteger, ForeignKey(ActivitiesUsers.id))
    user: list[ActivitiesUsers] = relationship("ActivitiesUsers", back_populates="weapons", lazy="selectin")


class Records(Base):
    __tablename__ = "records"

    destiny_id = Column(BigInteger, nullable=False, primary_key=True)
    record_id = Column(BigInteger, nullable=False, primary_key=True)


class Collectibles(Base):
    __tablename__ = "collectibles"

    destiny_id = Column(BigInteger, nullable=False, primary_key=True)
    collectible_id = Column(BigInteger, nullable=False, primary_key=True)


################################################################
# Userdata


class DiscordUsers(Base):
    __tablename__ = "discordUsers"

    discord_id = Column(BigInteger, nullable=False, primary_key=True)

    destiny_id = Column(BigInteger, nullable=False, unique=True)
    system = Column(Integer, nullable=False)
    bungie_name = Column(Text, nullable=False)
    private_profile = Column(Boolean, nullable=False, default=False)

    token = Column(Text, nullable=True)  # if this is none, user (no longer) has no valid token
    refresh_token = Column(Text, nullable=False)
    token_expiry = Column(DateTime(timezone=True), nullable=False)
    refresh_token_expiry = Column(DateTime(timezone=True), nullable=False)

    signup_date = Column(DateTime(timezone=True), nullable=False)
    signup_server_id = Column(BigInteger, nullable=False)

    activities_last_updated = Column(DateTime(timezone=True), nullable=False, default=get_min_with_tz())
    collectibles_last_updated = Column(DateTime(timezone=True), nullable=False, default=get_min_with_tz())
    triumphs_last_updated = Column(DateTime(timezone=True), nullable=False, default=get_min_with_tz())


class DestinyClanLinks(Base):
    __tablename__ = "destinyClanLinks"

    discord_guild_id = Column(BigInteger, primary_key=True, nullable=False)
    destiny_clan_id = Column(BigInteger, unique=True, nullable=False)
    link_date = Column(DateTime(timezone=True), nullable=False)
    linked_by_discord_id = Column(BigInteger, nullable=False)


class ElevatorServers(Base):
    __tablename__ = "elevatorServers"

    guild_id = Column(BigInteger, nullable=False, primary_key=True)
    join_date = Column(DateTime(timezone=True), nullable=False, default=get_now_with_tz())


################################################################
# Roles

# for activities
class RolesActivity(Base):
    __tablename__ = "rolesActivity"

    role_id = Column(Integer, ForeignKey("roles.role_id", ondelete="CASCADE", onupdate="CASCADE"))
    id = Column(Integer, autoincrement=True, primary_key=True)

    allowed_activity_hashes = Column(ARRAY(BigInteger()), nullable=False)
    count = Column(Integer, nullable=False)

    allow_checkpoints = Column(Boolean, nullable=False)
    require_team_flawless = Column(Boolean, nullable=False)
    require_individual_flawless = Column(Boolean, nullable=False)

    require_score = Column(Integer, nullable=True)
    require_kills = Column(Integer, nullable=True)
    require_kills_per_minute = Column(Float, nullable=True)
    require_kda = Column(Float, nullable=True)
    require_kd = Column(Float, nullable=True)

    maximum_allowed_players = Column(Integer, nullable=False)

    allow_time_periods: list[RolesActivityTimePeriod] = relationship(
        "RolesActivityTimePeriod", cascade="all, delete-orphan", passive_deletes=True, lazy="selectin"
    )
    disallow_time_periods: list[RolesActivityTimePeriod] = relationship(
        "RolesActivityTimePeriod", cascade="all, delete-orphan", passive_deletes=True, lazy="selectin"
    )

    inverse = Column(Boolean, nullable=False)


class RolesActivityTimePeriod(Base):
    __tablename__ = "rolesActivityTimePeriod"

    role_activity_id = Column(Integer, ForeignKey("rolesActivity.id", ondelete="CASCADE", onupdate="CASCADE"))
    id = Column(Integer, autoincrement=True, primary_key=True)

    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)


# for collectibles, triumphs, etc.
class RolesInteger(Base):
    __tablename__ = "rolesInteger"

    role_id = Column(Integer, ForeignKey("roles.role_id", ondelete="CASCADE", onupdate="CASCADE"))

    # the id of the collectible / record
    id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=False)

    inverse = Column(Boolean, nullable=False)


# association table to link roles and their required roles - https://docs.sqlalchemy.org/en/14/orm/join_conditions.html#self-referential-many-to-many-relationship
required_roles_association_table = Table(
    "requiredRolesAssociation",
    Base.metadata,
    Column("parent_role_id", ForeignKey("roles.role_id"), primary_key=True),
    Column("require_role_id", ForeignKey("roles.role_id"), primary_key=True),
)


class Roles(Base):
    __tablename__ = "roles"

    # todo delete (also in alembic)
    role_data = Column(JSON, nullable=True)

    id = Column(Integer, autoincrement=True, primary_key=True)

    role_id = Column(BigInteger, nullable=False, unique=True)
    guild_id = Column(BigInteger, nullable=False)

    category = Column(Text, nullable=False)
    deprecated = Column(Boolean, nullable=False)
    acquirable = Column(Boolean, nullable=False)

    require_activity_completions: list[RolesActivity] = relationship(
        "RolesActivity", cascade="all, delete-orphan", passive_deletes=True, lazy="selectin"
    )
    require_collectibles: list[RolesInteger] = relationship(
        "RolesInteger", cascade="all, delete-orphan", passive_deletes=True, lazy="selectin"
    )
    require_records: list[RolesInteger] = relationship(
        "RolesInteger", cascade="all, delete-orphan", passive_deletes=True, lazy="selectin"
    )
    require_roles: list[Roles] = relationship(
        "Roles",
        secondary=required_roles_association_table,
        primaryjoin=role_id == required_roles_association_table.c.parent_role_id,
        secondaryjoin=role_id == required_roles_association_table.c.require_role_id,
        backref=backref("required_by_roles", cascade="all", lazy="selectin", join_depth=2),
        lazy="selectin",
        join_depth=2,
    )

    _replaced_by_role_id = Column(BigInteger, ForeignKey("roles.role_id"), nullable=True)
    replaced_by_role: Roles | None = relationship(
        "Roles", remote_side=[role_id], cascade="save-update, merge", lazy="selectin", join_depth=2
    )


################################################################
# Destiny Manifest


class Versions(Base):
    __tablename__ = "versions"

    name = Column(Text, nullable=False, primary_key=True)
    version = Column(Text, nullable=False)


class DestinyActivityDefinition(Base):
    __tablename__ = "destinyActivityDefinition"

    reference_id = Column(BigInteger, nullable=False, primary_key=True)
    description = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    pgcr_image_url = Column(Text, nullable=True)
    activity_light_level = Column(Integer, nullable=False)
    destination_hash = Column(BigInteger, nullable=False)
    place_hash = Column(BigInteger, nullable=False)
    activity_type_hash = Column(BigInteger, nullable=False)
    is_pvp = Column(Boolean, nullable=False)
    direct_activity_mode_hash = Column(BigInteger, nullable=False)
    direct_activity_mode_type = Column(SmallInteger, nullable=False)
    activity_mode_hashes = Column(ARRAY(BigInteger()), nullable=False)
    activity_mode_types = Column(ARRAY(SmallInteger()), nullable=False)
    matchmade = Column(Boolean, nullable=False)
    max_players = Column(SmallInteger, nullable=False)


class DestinyActivityModeDefinition(Base):
    __tablename__ = "destinyActivityModeDefinition"

    reference_id = Column(BigInteger, nullable=False, primary_key=True)
    parent_hashes = Column(ARRAY(BigInteger()), nullable=True)
    mode_type = Column(SmallInteger, nullable=False)
    description = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    activity_mode_category = Column(SmallInteger, nullable=False)
    is_team_based = Column(Boolean, nullable=False)
    friendly_name = Column(Text, nullable=False)
    display = Column(Boolean, nullable=False)
    redacted = Column(Boolean, nullable=False)


class DestinyActivityTypeDefinition(Base):
    __tablename__ = "destinyActivityTypeDefinition"

    reference_id = Column(BigInteger, nullable=False, primary_key=True)
    description = Column(Text, nullable=False, default="")
    name = Column(Text, nullable=True)  # sometimes activity types do not have a name -> 73015004


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
    description = Column(Text, nullable=False, default="")
    name = Column(Text, nullable=True)
    category = Column(SmallInteger, nullable=False)
    item_count = Column(SmallInteger, nullable=False)
    location = Column(SmallInteger, nullable=False)


class DestinyInventoryItemDefinition(Base):
    __tablename__ = "destinyInventoryItemDefinition"

    reference_id = Column(BigInteger, nullable=False, primary_key=True)
    description = Column(Text, nullable=False, default="")
    name = Column(Text, nullable=False)
    flavor_text = Column(Text, nullable=False, default="")
    item_type = Column(SmallInteger, nullable=False)
    item_sub_type = Column(SmallInteger, nullable=False)
    class_type = Column(SmallInteger, nullable=False)
    bucket_type_hash = Column(BigInteger, nullable=False)
    tier_type = Column(SmallInteger, nullable=False)
    tier_type_name = Column(Text, nullable=False)
    equippable = Column(Boolean, nullable=False)
    default_damage_type = Column(SmallInteger, nullable=False)
    ammo_type = Column(SmallInteger, nullable=False, default=0)  # 0 == no damage type


class DestinyPresentationNodeDefinition(Base):
    __tablename__ = "destinyPresentationNodeDefinition"

    reference_id = Column(BigInteger, nullable=False, primary_key=True)
    description = Column(Text, nullable=False, default="")
    name = Column(Text, nullable=False)
    objective_hash = Column(BigInteger, nullable=True)
    presentation_node_type = Column(SmallInteger, nullable=False)
    children_presentation_node_hash = Column(ARRAY(BigInteger()), nullable=False)
    children_collectible_hash = Column(ARRAY(BigInteger()), nullable=False)
    children_record_hash = Column(ARRAY(BigInteger()), nullable=False)
    children_metric_hash = Column(ARRAY(BigInteger()), nullable=False)
    parent_node_hashes = Column(ARRAY(BigInteger()), nullable=False)
    index = Column(SmallInteger, nullable=False)
    redacted = Column(Boolean, nullable=False)
    completion_record_hash = Column(BigInteger, nullable=True)


class DestinyRecordDefinition(Base):
    __tablename__ = "destinyRecordDefinition"

    reference_id = Column(BigInteger, nullable=False, primary_key=True)
    description = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    for_title_gilding = Column(Boolean, nullable=False)
    title_name = Column(Text, nullable=True)
    objective_hashes = Column(ARRAY(BigInteger()), nullable=False, default=[])
    score_value = Column(Integer, nullable=False, default=0)
    parent_node_hashes = Column(ARRAY(BigInteger()), nullable=False, default=[])


class DestinySeasonPassDefinition(Base):
    __tablename__ = "destinySeasonPassDefinition"

    reference_id = Column(BigInteger, nullable=False, primary_key=True)
    name = Column(Text, nullable=False)
    reward_progression_hash = Column(BigInteger, nullable=False)
    prestige_progression_hash = Column(BigInteger, nullable=False)
    index = Column(SmallInteger, nullable=False)


class DestinyLoreDefinition(Base):
    __tablename__ = "destinyLoreDefinition"

    reference_id = Column(BigInteger, nullable=False, primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    sub_title = Column(Text, nullable=True)
    redacted = Column(Boolean, nullable=False)


################################################################
# LFG System


class LfgMessage(Base):
    __tablename__ = "lfgMessages"

    id = Column(Integer, nullable=False, primary_key=True)

    guild_id = Column(BigInteger, nullable=False)
    channel_id = Column(BigInteger, nullable=False)
    author_id = Column(BigInteger, nullable=False)
    message_id = Column(BigInteger, nullable=True)

    activity = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    start_time = Column(DateTime(True), nullable=False)
    max_joined_members = Column(Integer, nullable=False)
    joined_members = Column(ARRAY(BigInteger()), nullable=False)
    backup_members = Column(ARRAY(BigInteger()), nullable=False)

    creation_time = Column(DateTime(True), nullable=False)
    voice_channel_id = Column(BigInteger, nullable=True)

    started = Column(Boolean, nullable=False)


################################################################
# Misc


class D2SteamPlayer(Base):
    __tablename__ = "d2SteamPlayers"

    date = Column(Date, nullable=False, primary_key=True)
    number_of_players = Column(Integer, nullable=False)


class Poll(Base):
    __tablename__ = "polls"

    id = Column(BigInteger, nullable=False, primary_key=True)
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

    message_name = Column(Text, nullable=False, primary_key=True, autoincrement=False)

    guild_id = Column(BigInteger, nullable=False, primary_key=True, autoincrement=False)
    channel_id = Column(BigInteger, nullable=False)
    message_id = Column(BigInteger, nullable=True)


class ModerationLog(Base):
    __tablename__ = "moderationLog"

    id = Column(BigInteger, nullable=False, primary_key=True)
    guild_id = Column(BigInteger, nullable=False)
    discord_id = Column(BigInteger, nullable=False)
    mod_discord_id = Column(BigInteger, nullable=False)

    type = Column(Text, nullable=False)
    duration_in_seconds = Column(BigInteger, nullable=True)
    reason = Column(Text, nullable=False)
    date = Column(DateTime(True), nullable=False)


class Giveaway(Base):
    __tablename__ = "giveaway"

    message_id = Column(BigInteger, nullable=False, primary_key=True)
    author_id = Column(BigInteger, nullable=False)
    guild_id = Column(BigInteger, nullable=False)
    discord_ids = Column(ARRAY(BigInteger()), nullable=False, default=[])


# insert all tables
_TABLES_CREATED = False

create_tables_lock = asyncio.Lock()


async def create_tables(engine: Engine):
    global _TABLES_CREATED

    async with create_tables_lock:
        if not _TABLES_CREATED:
            async with engine.begin() as connection:
                if is_test_mode():
                    await connection.run_sync(Base.metadata.drop_all)

                await connection.run_sync(Base.metadata.create_all)

            _TABLES_CREATED = True
