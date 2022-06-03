from fastapi import APIRouter

from Backend.crud import moderation
from Backend.crud.misc.moderation import ModerationTypes
from Backend.database import acquire_db_session
from Shared.networkingSchemas.misc.moderation import ModerationAddModel, ModerationModel, ModerationsModel

router = APIRouter(
    prefix="/moderation/{guild_id}/{discord_id}",
    tags=["moderation"],
)


@router.get("/mute", response_model=ModerationsModel)  # has test
async def get_mutes(guild_id: int, discord_id: int):
    """Gets all mutes for the user in the guild"""

    async with acquire_db_session() as db:
        entries = await moderation.get(db=db, discord_id=discord_id, guild_id=guild_id, mod_type=ModerationTypes.MUTE)
        return ModerationsModel(entries=[ModerationModel.from_orm(model) for model in entries])


@router.get("/warning", response_model=ModerationsModel)  # has test
async def get_warnings(guild_id: int, discord_id: int):
    """Gets all warnings for the user in the guild"""

    async with acquire_db_session() as db:
        entries = await moderation.get(
            db=db, discord_id=discord_id, guild_id=guild_id, mod_type=ModerationTypes.WARNING
        )
        return ModerationsModel(entries=[ModerationModel.from_orm(model) for model in entries])


@router.post("/mute", response_model=ModerationModel)  # has test
async def add_mute(guild_id: int, discord_id: int, data: ModerationAddModel):
    """Add a mute for the user in the guild"""

    async with acquire_db_session() as db:
        model = await moderation.add(
            db=db, discord_id=discord_id, guild_id=guild_id, mod_type=ModerationTypes.MUTE, **data.dict()
        )
        return ModerationModel.from_orm(model)


@router.post("/warning", response_model=ModerationModel)  # has test
async def add_warning(guild_id: int, discord_id: int, data: ModerationAddModel):
    """Add a warning for the user in the guild"""

    async with acquire_db_session() as db:
        model = await moderation.add(
            db=db, discord_id=discord_id, guild_id=guild_id, mod_type=ModerationTypes.WARNING, **data.dict()
        )
        return ModerationModel.from_orm(model)
