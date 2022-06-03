from fastapi import APIRouter

from Backend.crud import lfg
from Backend.database import acquire_db_session
from Backend.database.models import LfgMessage
from Shared.functions.helperFunctions import get_now_with_tz
from Shared.networkingSchemas import EmptyResponseModel
from Shared.networkingSchemas.destiny.lfgSystem import (
    AllLfgDeleteOutputModel,
    AllLfgOutputModel,
    LfgCreateInputModel,
    LfgOutputModel,
    LfgUpdateInputModel,
    UserAllLfgOutputModel,
)

router = APIRouter(
    prefix="/destiny/lfg/{guild_id}",
    tags=["destiny", "lfg"],
)


@router.get("/get/all", response_model=AllLfgOutputModel)  # has test
async def get_all(guild_id: int):
    """Gets all the lfg events and info belonging to the guild"""

    async with acquire_db_session() as db:
        voice_category_channel_id = await lfg.get_voice_category_channel_id(db=db, guild_id=guild_id)
        objs = await lfg.get_all(db=db, guild_id=guild_id)

        result = AllLfgOutputModel()
        for obj in objs:
            model = LfgOutputModel.from_orm(obj)
            model.voice_category_channel_id = voice_category_channel_id

            result.events.append(model)

        return result


@router.get("/get/{lfg_id}", response_model=LfgOutputModel)  # has test
async def get(guild_id: int, lfg_id: int):
    """Gets the lfg info belonging to the lfg id and guild"""

    async with acquire_db_session() as db:
        voice_category_channel_id = await lfg.get_voice_category_channel_id(db=db, guild_id=guild_id)
        obj = await lfg.get(db=db, lfg_id=lfg_id, guild_id=guild_id)

        result = LfgOutputModel.from_orm(obj)
        result.voice_category_channel_id = voice_category_channel_id

        return result


@router.get("/{discord_id}/get/all", response_model=UserAllLfgOutputModel)  # has test
async def user_get_all(guild_id: int, discord_id: int):
    """Gets the lfg infos belonging to the discord_id"""

    async with acquire_db_session() as db:
        return await lfg.get_user(db=db, discord_id=discord_id)


@router.post("/{discord_id}/update/{lfg_id}", response_model=LfgOutputModel)  # has test
async def update(
    guild_id: int,
    discord_id: int,
    lfg_id: int,
    lfg_data: LfgUpdateInputModel,
):
    """Updates the lfg info belonging to the lfg id and guild"""

    async with acquire_db_session() as db:
        voice_category_channel_id = await lfg.get_voice_category_channel_id(db=db, guild_id=guild_id)
        obj = await lfg.update(db=db, lfg_id=lfg_id, guild_id=guild_id, discord_id=discord_id, **lfg_data.dict())

        result = LfgOutputModel.from_orm(obj)
        result.voice_category_channel_id = voice_category_channel_id

        return result


@router.post("/{discord_id}/create", response_model=LfgOutputModel)  # has test
async def create(guild_id: int, discord_id: int, lfg_data: LfgCreateInputModel):
    """
    Inserts the lfg info and gives it a new id
    Guild_id describes the guild where the lfg message got created and discord_id the author
    """

    async with acquire_db_session() as db:
        # get the linked lfg channel
        channel_id = await lfg.get_channel_id(db=db, guild_id=guild_id)

        # get the creation time
        creation_time = get_now_with_tz()

        # create the sql alchemy model
        to_create = LfgMessage(
            guild_id=guild_id,
            channel_id=channel_id,
            author_id=discord_id,
            creation_time=creation_time,
            started=False,
            **lfg_data.dict(),
        )

        # insert that
        await lfg.insert(db=db, to_create=to_create)

        result = LfgOutputModel.from_orm(to_create)

        voice_category_channel_id = await lfg.get_voice_category_channel_id(db=db, guild_id=guild_id)
        result.voice_category_channel_id = voice_category_channel_id

        return result


@router.delete("/{discord_id}/delete/{lfg_id}", response_model=EmptyResponseModel)  # has test
async def delete(guild_id: int, discord_id: int, lfg_id: int):
    """
    Delete the lfg info belonging to the lfg id and guild
    discord_id has to be the creator or an guild admin. If they are guild admin, set discord_id to 1
    """

    async with acquire_db_session() as db:
        await lfg.delete(db=db, lfg_id=lfg_id, guild_id=guild_id, discord_id=discord_id)

        return EmptyResponseModel()


@router.delete("/delete/all", response_model=AllLfgDeleteOutputModel)  # has test
async def delete_all(guild_id: int):
    """
    Delete all lfg events for the guild
    """

    async with acquire_db_session() as db:
        return await lfg.delete_all(db=db, guild_id=guild_id)
