from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud import persistent_messages
from Backend.dependencies import get_db_session
from Backend.schemas.empty import EmptyResponseModel
from Backend.schemas.misc.persistentMessages import (
    PersistentMessage,
    PersistentMessageUpsert,
)

router = APIRouter(
    prefix="/persistentMessages",
    tags=["persistent messages"],
)


@router.get("/{guild_id}/get/{message_name}", response_model=PersistentMessage)
async def get(guild_id: int, message_name: str, db: AsyncSession = Depends(get_db_session)):
    """Gets a persistent message"""

    result = await persistent_messages.get(db=db, guild_id=guild_id, message_name=message_name)
    return PersistentMessage.from_orm(result)


@router.post("/{guild_id}/upsert/{message_name}", response_model=PersistentMessage)
async def upsert(
    guild_id: int, message_name: str, update_data: PersistentMessageUpsert, db: AsyncSession = Depends(get_db_session)
):
    """Upserts a persistent message"""

    result = await persistent_messages.upsert(
        db=db,
        guild_id=guild_id,
        message_name=message_name,
        channel_id=update_data.channel_id,
        message_id=update_data.message_id,
    )
    return PersistentMessage.from_orm(result)


@router.delete("/{guild_id}/delete/{message_name}", response_model=EmptyResponseModel)
async def delete(guild_id: int, message_name: str, db: AsyncSession = Depends(get_db_session)):
    """Deletes a persistent message"""

    await persistent_messages.delete(db=db, guild_id=guild_id, message_name=message_name)
    return EmptyResponseModel()
