"""Create initial database tables

Revision ID: 37f73a9d15d5
Revises:
Create Date: 2022-04-02 10:42:18.076326+00:00

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "37f73a9d15d5"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "activities",
        sa.Column("instance_id", sa.BigInteger(), nullable=False),
        sa.Column("period", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reference_id", sa.BigInteger(), nullable=False),
        sa.Column("director_activity_hash", sa.BigInteger(), nullable=False),
        sa.Column("starting_phase_index", sa.SmallInteger(), nullable=False),
        sa.Column("mode", sa.SmallInteger(), nullable=False),
        sa.Column("modes", sa.ARRAY(sa.SmallInteger()), nullable=False),
        sa.Column("is_private", sa.Boolean(), nullable=False),
        sa.Column("system", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint("instance_id"),
    )
    op.create_table(
        "activitiesFailToGet",
        sa.Column("instance_id", sa.BigInteger(), nullable=False),
        sa.Column("period", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("instance_id"),
    )
    op.create_table(
        "backendUser",
        sa.Column("user_name", sa.Text(), nullable=False),
        sa.Column("hashed_password", sa.Text(), nullable=False),
        sa.Column("allowed_scopes", sa.ARRAY(sa.Text()), nullable=True),
        sa.Column("has_write_permission", sa.Boolean(), nullable=False),
        sa.Column("has_read_permission", sa.Boolean(), nullable=False),
        sa.Column("disabled", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("user_name"),
    )
    op.create_table(
        "collectibles",
        sa.Column("destiny_id", sa.BigInteger(), nullable=False),
        sa.Column("collectible_id", sa.BigInteger(), nullable=False),
        sa.Column("owned", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("destiny_id", "collectible_id"),
    )
    op.create_table(
        "d2SteamPlayers",
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("number_of_players", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("date"),
    )
    op.create_table(
        "destinyActivityDefinition",
        sa.Column("reference_id", sa.BigInteger(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("pgcr_image_url", sa.Text(), nullable=True),
        sa.Column("activity_light_level", sa.Integer(), nullable=False),
        sa.Column("destination_hash", sa.BigInteger(), nullable=False),
        sa.Column("place_hash", sa.BigInteger(), nullable=False),
        sa.Column("activity_type_hash", sa.BigInteger(), nullable=False),
        sa.Column("is_pvp", sa.Boolean(), nullable=False),
        sa.Column("direct_activity_mode_hash", sa.BigInteger(), nullable=False),
        sa.Column("direct_activity_mode_type", sa.SmallInteger(), nullable=False),
        sa.Column("activity_mode_hashes", sa.ARRAY(sa.BigInteger()), nullable=False),
        sa.Column("activity_mode_types", sa.ARRAY(sa.SmallInteger()), nullable=False),
        sa.Column("matchmade", sa.Boolean(), nullable=False),
        sa.Column("max_players", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint("reference_id"),
    )
    op.create_table(
        "destinyActivityModeDefinition",
        sa.Column("reference_id", sa.BigInteger(), nullable=False),
        sa.Column("parent_hashes", sa.ARRAY(sa.BigInteger()), nullable=True),
        sa.Column("mode_type", sa.SmallInteger(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("activity_mode_category", sa.SmallInteger(), nullable=False),
        sa.Column("is_team_based", sa.Boolean(), nullable=False),
        sa.Column("friendly_name", sa.Text(), nullable=False),
        sa.Column("display", sa.Boolean(), nullable=False),
        sa.Column("redacted", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("reference_id"),
    )
    op.create_table(
        "destinyActivityTypeDefinition",
        sa.Column("reference_id", sa.BigInteger(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("reference_id"),
    )
    op.create_table(
        "destinyClanLinks",
        sa.Column("discord_guild_id", sa.BigInteger(), nullable=False),
        sa.Column("destiny_clan_id", sa.BigInteger(), nullable=False),
        sa.Column("link_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("linked_by_discord_id", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("discord_guild_id"),
        sa.UniqueConstraint("destiny_clan_id"),
    )
    op.create_table(
        "destinyCollectibleDefinition",
        sa.Column("reference_id", sa.BigInteger(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("source_hash", sa.BigInteger(), nullable=False),
        sa.Column("item_hash", sa.BigInteger(), nullable=False),
        sa.Column("parent_node_hashes", sa.ARRAY(sa.BigInteger()), nullable=False),
        sa.PrimaryKeyConstraint("reference_id"),
    )
    op.create_table(
        "destinyInventoryBucketDefinition",
        sa.Column("reference_id", sa.BigInteger(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("category", sa.SmallInteger(), nullable=False),
        sa.Column("item_count", sa.SmallInteger(), nullable=False),
        sa.Column("location", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint("reference_id"),
    )
    op.create_table(
        "destinyInventoryItemDefinition",
        sa.Column("reference_id", sa.BigInteger(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("flavor_text", sa.Text(), nullable=False),
        sa.Column("item_type", sa.SmallInteger(), nullable=False),
        sa.Column("item_sub_type", sa.SmallInteger(), nullable=False),
        sa.Column("class_type", sa.SmallInteger(), nullable=False),
        sa.Column("bucket_type_hash", sa.BigInteger(), nullable=False),
        sa.Column("tier_type", sa.SmallInteger(), nullable=False),
        sa.Column("tier_type_name", sa.Text(), nullable=False),
        sa.Column("equippable", sa.Boolean(), nullable=False),
        sa.Column("default_damage_type", sa.SmallInteger(), nullable=False),
        sa.Column("ammo_type", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint("reference_id"),
    )
    op.create_table(
        "destinyLoreDefinition",
        sa.Column("reference_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("sub_title", sa.Text(), nullable=True),
        sa.Column("redacted", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("reference_id"),
    )
    op.create_table(
        "destinyPresentationNodeDefinition",
        sa.Column("reference_id", sa.BigInteger(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("objective_hash", sa.BigInteger(), nullable=True),
        sa.Column("presentation_node_type", sa.SmallInteger(), nullable=False),
        sa.Column("children_presentation_node_hash", sa.ARRAY(sa.BigInteger()), nullable=False),
        sa.Column("children_collectible_hash", sa.ARRAY(sa.BigInteger()), nullable=False),
        sa.Column("children_record_hash", sa.ARRAY(sa.BigInteger()), nullable=False),
        sa.Column("children_metric_hash", sa.ARRAY(sa.BigInteger()), nullable=False),
        sa.Column("parent_node_hashes", sa.ARRAY(sa.BigInteger()), nullable=False),
        sa.Column("index", sa.SmallInteger(), nullable=False),
        sa.Column("redacted", sa.Boolean(), nullable=False),
        sa.Column("completion_record_hash", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("reference_id"),
    )
    op.create_table(
        "destinyRecordDefinition",
        sa.Column("reference_id", sa.BigInteger(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("for_title_gilding", sa.Boolean(), nullable=False),
        sa.Column("title_name", sa.Text(), nullable=True),
        sa.Column("objective_hashes", sa.ARRAY(sa.BigInteger()), nullable=False),
        sa.Column("score_value", sa.Integer(), nullable=False),
        sa.Column("parent_node_hashes", sa.ARRAY(sa.BigInteger()), nullable=False),
        sa.PrimaryKeyConstraint("reference_id"),
    )
    op.create_table(
        "destinySeasonPassDefinition",
        sa.Column("reference_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("reward_progression_hash", sa.BigInteger(), nullable=False),
        sa.Column("prestige_progression_hash", sa.BigInteger(), nullable=False),
        sa.Column("index", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint("reference_id"),
    )
    op.create_table(
        "discordUsers",
        sa.Column("discord_id", sa.BigInteger(), nullable=False),
        sa.Column("destiny_id", sa.BigInteger(), nullable=False),
        sa.Column("system", sa.Integer(), nullable=False),
        sa.Column("bungie_name", sa.Text(), nullable=False),
        sa.Column("private_profile", sa.Boolean(), nullable=False),
        sa.Column("token", sa.Text(), nullable=True),
        sa.Column("refresh_token", sa.Text(), nullable=False),
        sa.Column("token_expiry", sa.DateTime(timezone=True), nullable=False),
        sa.Column("refresh_token_expiry", sa.DateTime(timezone=True), nullable=False),
        sa.Column("signup_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("signup_server_id", sa.BigInteger(), nullable=False),
        sa.Column("activities_last_updated", sa.DateTime(timezone=True), nullable=False),
        sa.Column("collectibles_last_updated", sa.DateTime(timezone=True), nullable=False),
        sa.Column("triumphs_last_updated", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("discord_id"),
        sa.UniqueConstraint("destiny_id"),
    )
    op.create_table(
        "elevatorServers",
        sa.Column("guild_id", sa.BigInteger(), nullable=False),
        sa.Column("join_date", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("guild_id"),
    )
    op.create_table(
        "giveaway",
        sa.Column("message_id", sa.BigInteger(), nullable=False),
        sa.Column("author_id", sa.BigInteger(), nullable=False),
        sa.Column("guild_id", sa.BigInteger(), nullable=False),
        sa.Column("discord_ids", sa.ARRAY(sa.BigInteger()), nullable=False),
        sa.PrimaryKeyConstraint("message_id"),
    )
    op.create_table(
        "lfgMessages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("guild_id", sa.BigInteger(), nullable=False),
        sa.Column("channel_id", sa.BigInteger(), nullable=False),
        sa.Column("author_id", sa.BigInteger(), nullable=False),
        sa.Column("message_id", sa.BigInteger(), nullable=True),
        sa.Column("activity", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("max_joined_members", sa.Integer(), nullable=False),
        sa.Column("joined_members", sa.ARRAY(sa.BigInteger()), nullable=False),
        sa.Column("backup_members", sa.ARRAY(sa.BigInteger()), nullable=False),
        sa.Column("creation_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("voice_channel_id", sa.BigInteger(), nullable=True),
        sa.Column("started", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "moderationLog",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("guild_id", sa.BigInteger(), nullable=False),
        sa.Column("discord_id", sa.BigInteger(), nullable=False),
        sa.Column("mod_discord_id", sa.BigInteger(), nullable=False),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("duration_in_seconds", sa.BigInteger(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("date", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "persistentMessages",
        sa.Column("message_name", sa.Text(), autoincrement=False, nullable=False),
        sa.Column("guild_id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("channel_id", sa.BigInteger(), nullable=False),
        sa.Column("message_id", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("message_name", "guild_id"),
    )
    op.create_table(
        "polls",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("author_id", sa.BigInteger(), nullable=False),
        sa.Column("guild_id", sa.BigInteger(), nullable=False),
        sa.Column("channel_id", sa.BigInteger(), nullable=False),
        sa.Column("message_id", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "records",
        sa.Column("destiny_id", sa.BigInteger(), nullable=False),
        sa.Column("record_id", sa.BigInteger(), nullable=False),
        sa.Column("completed", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("destiny_id", "record_id"),
    )
    op.create_table(
        "roles",
        sa.Column("role_id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("guild_id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("role_data", sa.JSON(), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint("role_id"),
    )
    op.create_table("rssFeedItems", sa.Column("id", sa.Text(), nullable=False), sa.PrimaryKeyConstraint("id"))
    op.create_table(
        "versions",
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("version", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("name"),
    )
    op.create_table(
        "activitiesUsers",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("destiny_id", sa.BigInteger(), nullable=False),
        sa.Column("bungie_name", sa.Text(), nullable=False),
        sa.Column("character_id", sa.BigInteger(), nullable=False),
        sa.Column("character_class", sa.Text(), nullable=True),
        sa.Column("character_level", sa.SmallInteger(), nullable=False),
        sa.Column("system", sa.SmallInteger(), nullable=False),
        sa.Column("light_level", sa.Integer(), nullable=False),
        sa.Column("emblem_hash", sa.BigInteger(), nullable=False),
        sa.Column("standing", sa.SmallInteger(), nullable=False),
        sa.Column("assists", sa.Integer(), nullable=False),
        sa.Column("completed", sa.SmallInteger(), nullable=False),
        sa.Column("deaths", sa.Integer(), nullable=False),
        sa.Column("kills", sa.Integer(), nullable=False),
        sa.Column("opponents_defeated", sa.Integer(), nullable=False),
        sa.Column("efficiency", sa.Numeric(), nullable=False),
        sa.Column("kills_deaths_ratio", sa.Numeric(), nullable=False),
        sa.Column("kills_deaths_assists", sa.Numeric(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("activity_duration_seconds", sa.Integer(), nullable=False),
        sa.Column("completion_reason", sa.SmallInteger(), nullable=False),
        sa.Column("start_seconds", sa.Integer(), nullable=False),
        sa.Column("time_played_seconds", sa.Integer(), nullable=False),
        sa.Column("player_count", sa.SmallInteger(), nullable=False),
        sa.Column("team_score", sa.Integer(), nullable=False),
        sa.Column("precision_kills", sa.Integer(), nullable=False),
        sa.Column("weapon_kills_grenade", sa.Integer(), nullable=False),
        sa.Column("weapon_kills_melee", sa.Integer(), nullable=False),
        sa.Column("weapon_kills_super", sa.Integer(), nullable=False),
        sa.Column("weapon_kills_ability", sa.Integer(), nullable=False),
        sa.Column("activity_instance_id", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["activity_instance_id"],
            ["activities.instance_id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "activitiesUsersWeapons",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("weapon_id", sa.BigInteger(), nullable=False),
        sa.Column("unique_weapon_kills", sa.Integer(), nullable=False),
        sa.Column("unique_weapon_precision_kills", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["activitiesUsers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("activitiesUsersWeapons")
    op.drop_table("activitiesUsers")
    op.drop_table("versions")
    op.drop_table("rssFeedItems")
    op.drop_table("roles")
    op.drop_table("records")
    op.drop_table("polls")
    op.drop_table("persistentMessages")
    op.drop_table("moderationLog")
    op.drop_table("lfgMessages")
    op.drop_table("giveaway")
    op.drop_table("elevatorServers")
    op.drop_table("discordUsers")
    op.drop_table("destinySeasonPassDefinition")
    op.drop_table("destinyRecordDefinition")
    op.drop_table("destinyPresentationNodeDefinition")
    op.drop_table("destinyLoreDefinition")
    op.drop_table("destinyInventoryItemDefinition")
    op.drop_table("destinyInventoryBucketDefinition")
    op.drop_table("destinyCollectibleDefinition")
    op.drop_table("destinyClanLinks")
    op.drop_table("destinyActivityTypeDefinition")
    op.drop_table("destinyActivityModeDefinition")
    op.drop_table("destinyActivityDefinition")
    op.drop_table("d2SteamPlayers")
    op.drop_table("collectibles")
    op.drop_table("backendUser")
    op.drop_table("activitiesFailToGet")
    op.drop_table("activities")
    # ### end Alembic commands ###