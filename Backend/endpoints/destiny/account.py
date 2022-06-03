from fastapi import APIRouter

from Backend.core.destiny.activities import DestinyActivities
from Backend.core.destiny.profile import DestinyProfile
from Backend.crud import discord_users
from Backend.database import acquire_db_session
from Shared.networkingSchemas import BoolModel, DestinyAllMaterialsModel, NameModel, ValueModel
from Shared.networkingSchemas.destiny import (
    BoolModelRecord,
    DestinyCatalystsModel,
    DestinyCharactersModel,
    DestinyCraftableModel,
    DestinyLowMansByCategoryModel,
    DestinySealsModel,
    DestinyStatInputModel,
    DestinyTimeInputModel,
    DestinyTimeModel,
    DestinyTimesModel,
    DestinyTriumphScoreModel,
    SeasonalChallengesModel,
)

router = APIRouter(
    prefix="/destiny/account/{guild_id}/{discord_id}",
    tags=["destiny", "account"],
)


@router.get("/name", response_model=NameModel)  # has test
async def destiny_name(guild_id: int, discord_id: int):
    """Return the bungie name"""

    async with acquire_db_session() as db:
        user = await discord_users.get_profile_from_discord_id(discord_id, db=db)
        return NameModel(name=user.bungie_name)


@router.get("/collectible/{collectible_id}", response_model=BoolModel)  # has test
async def has_collectible(guild_id: int, discord_id: int, collectible_id: int):
    """Return is the collectible is unlocked"""

    async with acquire_db_session() as db:
        user = await discord_users.get_profile_from_discord_id(discord_id, db=db)
        profile = DestinyProfile(db=db, user=user)
        return BoolModel(bool=await profile.has_collectible(collectible_hash=collectible_id))


@router.get("/craftables", response_model=list[DestinyCraftableModel])
async def get_craftables(guild_id: int, discord_id: int):
    """Return is the collectible is unlocked"""

    async with acquire_db_session() as db:
        user = await discord_users.get_profile_from_discord_id(discord_id, db=db)
        profile = DestinyProfile(db=db, user=user)
        return [DestinyCraftableModel(craftable=craftable) for craftable in (await profile.get_craftables())]


@router.get("/triumph/{triumph_id}", response_model=BoolModelRecord)  # has test
async def has_triumph(guild_id: int, discord_id: int, triumph_id: int):
    """Return is the triumph is unlocked"""

    async with acquire_db_session() as db:
        user = await discord_users.get_profile_from_discord_id(discord_id, db=db)
        profile = DestinyProfile(db=db, user=user)

        return await profile.has_triumph(triumph_hash=triumph_id, send_details=True)


@router.get("/metric/{metric_id}", response_model=ValueModel)  # has test
async def metric(guild_id: int, discord_id: int, metric_id: int):
    """Return the metric value"""

    async with acquire_db_session() as db:
        user = await discord_users.get_profile_from_discord_id(discord_id, db=db)
        profile = DestinyProfile(db=db, user=user)

        # get the metric value
        value = await profile.get_metric_value(metric_hash=metric_id)

        return ValueModel(value=value)


@router.get("/solos", response_model=DestinyLowMansByCategoryModel)  # has test
async def destiny_solos(guild_id: int, discord_id: int):
    """Return the destiny solos"""

    async with acquire_db_session() as db:
        user = await discord_users.get_profile_from_discord_id(discord_id, db=db)
        activities = DestinyActivities(db=db, user=user)

        # update the user's db entries
        await activities.update_activity_db()

        # get the solo data
        return await activities.get_solos()


@router.get("/characters", response_model=DestinyCharactersModel)  # has test
async def characters(guild_id: int, discord_id: int):
    """Return the characters with info on them"""

    async with acquire_db_session() as db:
        user = await discord_users.get_profile_from_discord_id(discord_id, db=db)
        profile = DestinyProfile(db=db, user=user)

        # get the characters
        return await profile.get_character_info()


@router.post("/stat/", response_model=ValueModel)  # has test
async def stat(guild_id: int, discord_id: int, stat_model: DestinyStatInputModel):
    """Return the stat value"""

    async with acquire_db_session() as db:
        user = await discord_users.get_profile_from_discord_id(discord_id, db=db)
        profile = DestinyProfile(db=db, user=user)

        # get the stat value
        value = await profile.get_stat_value(stat_name=stat_model.stat_name, stat_category=stat_model.stat_category)

        return ValueModel(value=value)


@router.post("/stat/character/{character_id}", response_model=ValueModel)  # has test
async def stat_characters(
    guild_id: int,
    discord_id: int,
    character_id: int,
    stat_model: DestinyStatInputModel,
):
    """Return the stat value by character_id"""

    async with acquire_db_session() as db:
        user = await discord_users.get_profile_from_discord_id(discord_id, db=db)
        profile = DestinyProfile(db=db, user=user)

        # get the stat value
        value = await profile.get_stat_value(
            stat_name=stat_model.stat_name, stat_category=stat_model.stat_category, character_id=character_id
        )

        return ValueModel(value=value)


@router.post("/time", response_model=DestinyTimesModel)  # has test
async def time(guild_id: int, discord_id: int, time_input: DestinyTimeInputModel):
    """
    Return the time played for the specified modes / activities
    """

    async with acquire_db_session() as db:
        user = await discord_users.get_profile_from_discord_id(discord_id, db=db)

        # update the user's db entries
        activities = DestinyActivities(db=db, user=user)
        await activities.update_activity_db()

        profile = DestinyProfile(db=db, user=user)

        entries = []
        if not time_input.activity_ids:
            # loop through the modes
            for mode in time_input.modes:
                entries.append(
                    DestinyTimeModel(
                        mode=mode,
                        time_played=await profile.get_time_played(
                            start_time=time_input.start_time,
                            end_time=time_input.end_time,
                            mode=mode,
                            character_class=time_input.character_class,
                        ),
                    )
                )

        else:
            # check the total then the activities
            entries.append(
                DestinyTimeModel(
                    mode=0,
                    time_played=await profile.get_time_played(
                        start_time=time_input.start_time,
                        end_time=time_input.end_time,
                        mode=0,
                        character_class=time_input.character_class,
                    ),
                )
            )
            entries.append(
                DestinyTimeModel(
                    activity_ids=time_input.activity_ids,
                    time_played=await profile.get_time_played(
                        start_time=time_input.start_time,
                        end_time=time_input.end_time,
                        activity_ids=time_input.activity_ids,
                        character_class=time_input.character_class,
                    ),
                )
            )

        return DestinyTimesModel(entries=entries)


@router.get("/seasonal_challenges", response_model=SeasonalChallengesModel)  # has test
async def seasonal_challenges(guild_id: int, discord_id: int):
    """Return the seasonal challenge's completion ratio"""

    async with acquire_db_session() as db:
        user = await discord_users.get_profile_from_discord_id(discord_id, db=db)
        profile = DestinyProfile(db=db, user=user)

        return await profile.get_seasonal_challenges()


@router.get("/triumphs", response_model=DestinyTriumphScoreModel)  # has test
async def triumph_score(guild_id: int, discord_id: int):
    """Return the user's triumph scores"""

    async with acquire_db_session() as db:
        user = await discord_users.get_profile_from_discord_id(discord_id, db=db)
        profile = DestinyProfile(db=db, user=user)

        return await profile.get_triumph_score()


@router.get("/artifact", response_model=ValueModel)  # has test
async def artifact_level(guild_id: int, discord_id: int):
    """Return the user's artifact power bonus"""

    async with acquire_db_session() as db:
        user = await discord_users.get_profile_from_discord_id(discord_id, db=db)
        profile = DestinyProfile(db=db, user=user)

        return await profile.get_artifact_level()


@router.get("/season_pass", response_model=ValueModel)  # has test
async def season_pass_level(guild_id: int, discord_id: int):
    """Return the user's season pass level"""

    async with acquire_db_session() as db:
        user = await discord_users.get_profile_from_discord_id(discord_id, db=db)
        profile = DestinyProfile(db=db, user=user)

        return await profile.get_season_pass_level()


@router.get("/materials", response_model=DestinyAllMaterialsModel)  # has test
async def get_material_amount(guild_id: int, discord_id: int):
    """Get all noteworthy materials of the user"""

    async with acquire_db_session() as db:
        user = await discord_users.get_profile_from_discord_id(discord_id, db=db)
        profile = DestinyProfile(db=db, user=user)

        return await profile.get_materials()


@router.get("/consumable/{consumable_id}", response_model=ValueModel)  # has test
async def get_consumable_amount(guild_id: int, discord_id: int, consumable_id: int):
    """Gets the amount of the given consumable that the player has"""

    async with acquire_db_session() as db:
        user = await discord_users.get_profile_from_discord_id(discord_id, db=db)
        profile = DestinyProfile(db=db, user=user)

        return ValueModel(
            value=await profile.get_consumable_amount(
                consumable_id=consumable_id, check_vault=True, check_postmaster=True
            )
        )


@router.get("/max_power", response_model=ValueModel)  # has test
async def get_max_power(guild_id: int, discord_id: int):
    """Gets the current max power of the player"""

    async with acquire_db_session() as db:
        user = await discord_users.get_profile_from_discord_id(discord_id, db=db)
        profile = DestinyProfile(db=db, user=user)

        return ValueModel(value=await profile.get_max_power())


@router.get("/vault_space", response_model=ValueModel)  # has test
async def get_vault_space(guild_id: int, discord_id: int):
    """Gets the current used vault space of the player"""

    async with acquire_db_session() as db:
        user = await discord_users.get_profile_from_discord_id(discord_id, db=db)
        profile = DestinyProfile(db=db, user=user)

        return ValueModel(value=await profile.get_used_vault_space())


@router.get("/bright_dust", response_model=ValueModel)  # has test
async def get_bright_dust(guild_id: int, discord_id: int):
    """Gets the current bright dust of the player"""

    async with acquire_db_session() as db:
        user = await discord_users.get_profile_from_discord_id(discord_id, db=db)
        profile = DestinyProfile(db=db, user=user)

        return ValueModel(value=await profile.get_bright_dust())


@router.get("/shards", response_model=ValueModel)  # has test
async def get_legendary_shards(guild_id: int, discord_id: int):
    """Gets the current legendary shards of the player"""

    async with acquire_db_session() as db:
        user = await discord_users.get_profile_from_discord_id(discord_id, db=db)
        profile = DestinyProfile(db=db, user=user)

        return ValueModel(value=await profile.get_legendary_shards())


@router.get("/catalysts", response_model=DestinyCatalystsModel)  # has test
async def get_catalyst_completion(guild_id: int, discord_id: int):
    """Gets all catalysts and the user's completion status"""

    async with acquire_db_session() as db:
        user = await discord_users.get_profile_from_discord_id(discord_id, db=db)
        profile = DestinyProfile(db=db, user=user)

        return await profile.get_catalyst_completion()


@router.get("/seals", response_model=DestinySealsModel)
async def get_seal_completion(guild_id: int, discord_id: int):
    """Gets all seals and the user's completion status"""

    async with acquire_db_session() as db:
        user = await discord_users.get_profile_from_discord_id(discord_id, db=db)
        profile = DestinyProfile(db=db, user=user)

        return await profile.get_seal_completion()
