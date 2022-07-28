from __future__ import annotations

import asyncio
from typing import Optional

from bungio.models import AuthData, DestinyUser
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

    activity_instance_id = Column(BigInteger, ForeignKey(Activities.instance_id, ondelete="CASCADE"))
    activity: Activities = relationship("Activities", back_populates="users", lazy="selectin")

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

    user_id = Column(BigInteger, ForeignKey(ActivitiesUsers.id, ondelete="CASCADE"))
    user: ActivitiesUsers = relationship("ActivitiesUsers", back_populates="weapons", lazy="selectin")


class Records(Base):
    __tablename__ = "records"

    destiny_id = Column(BigInteger, nullable=False, primary_key=True)
    record_id = Column(BigInteger, nullable=False, primary_key=True)


class Collectibles(Base):
    __tablename__ = "collectibles"

    destiny_id = Column(BigInteger, nullable=False, primary_key=True)
    collectible_id = Column(BigInteger, nullable=False, primary_key=True)


################################################################
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

    @property
    def auth(self) -> Optional[AuthData]:
        if not self.token:
            return None
        return AuthData(
            token=self.token,
            token_expiry=self.token_expiry,
            refresh_token=self.refresh_token,
            refresh_token_expiry=self.refresh_token_expiry,
            membership_type=self.system,
            destiny_membership_id=self.destiny_id,
        )

    @property
    def bungio_user(self) -> DestinyUser:
        return DestinyUser(membership_id=self.destiny_id, membership_type=self.system)


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

    _id = Column(Integer, autoincrement=True, primary_key=True)
    role_id = Column(BigInteger, ForeignKey("roles.role_id", ondelete="CASCADE", onupdate="CASCADE"))

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

    allow_time_periods: list[RolesActivityAllowTimePeriod] = relationship(
        "RolesActivityAllowTimePeriod",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
    disallow_time_periods: list[RolesActivityDisallowTimePeriod] = relationship(
        "RolesActivityDisallowTimePeriod",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    inverse = Column(Boolean, nullable=False)


class RolesActivityAllowTimePeriod(Base):
    __tablename__ = "rolesActivityAllowTimePeriod"

    _id = Column(Integer, autoincrement=True, primary_key=True)
    role_activity_id = Column(Integer, ForeignKey("rolesActivity._id", ondelete="CASCADE", onupdate="CASCADE"))

    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)


class RolesActivityDisallowTimePeriod(Base):
    __tablename__ = "rolesActivityDisallowTimePeriod"

    _id = Column(Integer, autoincrement=True, primary_key=True)
    role_activity_id = Column(Integer, ForeignKey("rolesActivity._id", ondelete="CASCADE", onupdate="CASCADE"))

    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)


# for collectibles
class RolesCollectibles(Base):
    __tablename__ = "rolesCollectibles"

    _id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(BigInteger, ForeignKey("roles.role_id", ondelete="CASCADE", onupdate="CASCADE"))

    # the id of the collectible
    bungie_id = Column(BigInteger, nullable=False)

    inverse = Column(Boolean, nullable=False)


# for records
class RolesRecords(Base):
    __tablename__ = "rolesRecords"

    _id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(BigInteger, ForeignKey("roles.role_id", ondelete="CASCADE", onupdate="CASCADE"))

    # the id of the record
    bungie_id = Column(BigInteger, nullable=False)

    inverse = Column(Boolean, nullable=False)


# association table to link roles and their required roles - https://docs.sqlalchemy.org/en/14/orm/join_conditions.html#self-referential-many-to-many-relationship
required_roles_association_table = Table(
    "requiredRolesAssociation",
    Base.metadata,
    Column("parent_role_id", ForeignKey("roles.role_id", ondelete="CASCADE"), primary_key=True),
    Column("require_role_id", ForeignKey("roles.role_id", ondelete="CASCADE"), primary_key=True),
)


class Roles(Base):
    __tablename__ = "roles"

    _id = Column(Integer, autoincrement=True, primary_key=True)

    role_id = Column(BigInteger, nullable=False, unique=True)
    guild_id = Column(BigInteger, nullable=False)

    category = Column(Text, nullable=False)
    deprecated = Column(Boolean, nullable=False)
    acquirable = Column(Boolean, nullable=False)

    # requirement columns need to start with "requirement_"
    requirement_require_activity_completions: list[RolesActivity] = relationship(
        "RolesActivity", cascade="all, delete-orphan", passive_deletes=True, lazy="selectin"
    )
    requirement_require_collectibles: list[RolesCollectibles] = relationship(
        "RolesCollectibles",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
    requirement_require_records: list[RolesRecords] = relationship(
        "RolesRecords",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
    requirement_require_roles: list[Roles] = relationship(
        "Roles",
        secondary=required_roles_association_table,
        primaryjoin=role_id == required_roles_association_table.c.parent_role_id,
        secondaryjoin=role_id == required_roles_association_table.c.require_role_id,
        backref=backref("required_by_roles", cascade="all", lazy="selectin", join_depth=1),
        passive_deletes=True,
        lazy="selectin",
        join_depth=1,
    )

    _replaced_by_role_id = Column(BigInteger, ForeignKey("roles.role_id", ondelete="SET NULL"), nullable=True)
    requirement_replaced_by_role: Roles | None = relationship(
        "Roles", remote_side=[role_id], cascade="save-update, merge", lazy="selectin", join_depth=1
    )

    def __eq__(self, other: Roles | int) -> bool:
        if isinstance(other, Roles):
            return self.role_id == other.role_id
        else:
            return self.role_id == other


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
