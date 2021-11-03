from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud import lfg
from Backend.database.models import LfgMessage
from Backend.dependencies import get_db_session
from Backend.misc.helperFunctions import get_now_with_tz
from NetworkingSchemas.destiny.lfgSystem import (
    AllLfgOutputModel,
    LfgCreateInputModel,
    LfgOutputModel,
    LfgUpdateInputModel,
)
from NetworkingSchemas.empty import EmptyResponseModel

router = APIRouter(
    prefix="/destiny/{guild_id}/lfg",
    tags=["destiny", "lfg"],
)


@router.get("/get/all", response_model=AllLfgOutputModel)
async def get_all(guild_id: int, db: AsyncSession = Depends(get_db_session)):
    """Gets all the lfg events and info belonging to the guild"""

    objs = await lfg.get_all(db=db, guild_id=guild_id)

    result = AllLfgOutputModel()
    for obj in objs:
        result.events.append(LfgOutputModel.from_orm(obj))

    return result


@router.get("/get/{lfg_id}", response_model=LfgOutputModel)
async def get(guild_id: int, lfg_id: int, db: AsyncSession = Depends(get_db_session)):
    """Gets the lfg info belonging to the lfg id and guild"""

    obj = await lfg.get(db=db, lfg_id=lfg_id, guild_id=guild_id)

    return LfgOutputModel.from_orm(obj)


@router.post("/{discord_id}/update/{lfg_id}", response_model=LfgOutputModel)
async def update(
    guild_id: int,
    discord_id: int,
    lfg_id: int,
    lfg_data: LfgUpdateInputModel,
    db: AsyncSession = Depends(get_db_session),
):
    """Updates the lfg info belonging to the lfg id and guild"""

    # todo check if has admin role @elevator site

    obj = await lfg.update(db=db, lfg_id=lfg_id, guild_id=guild_id, discord_id=discord_id, **lfg_data.dict())

    return LfgOutputModel.from_orm(obj)


@router.post("/{discord_id}/create", response_model=LfgOutputModel)
async def create(
    guild_id: int, discord_id: int, lfg_data: LfgCreateInputModel, db: AsyncSession = Depends(get_db_session)
):
    """
    Inserts the lfg info and gives it a new id
    Guild_id describes the guild where the lfg message got created and discord_id the author
    """

    # todo get channel_id from db
    channel_id = None

    # get the creation time
    creation_time = get_now_with_tz()

    # create the sql alchemy model
    to_create = LfgMessage(
        guild_id=guild_id, channel_id=channel_id, author_id=discord_id, creation_time=creation_time, **lfg_data.dict()
    )

    # insert that
    await lfg.insert(db=db, to_create=to_create)

    return LfgOutputModel.from_orm(to_create)


@router.delete("/{discord_id}/delete/{lfg_id}", response_model=EmptyResponseModel)
async def delete(guild_id: int, discord_id: int, lfg_id: int, db: AsyncSession = Depends(get_db_session)):
    """
    Delete the lfg info belonging to the lfg id and guild
    discord_id has to be the creator or an guild admin. If they are guild admin, set discord_id to 1
    """

    # todo check if has admin role @elevator site

    await lfg.delete(db=db, lfg_id=lfg_id, guild_id=guild_id, discord_id=discord_id)

    return EmptyResponseModel()
