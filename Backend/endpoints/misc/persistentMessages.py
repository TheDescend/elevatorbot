from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud import persistent_messages
from Backend.dependencies import get_db_session
from NetworkingSchemas.basic import EmptyResponseModel
from NetworkingSchemas.misc.persistentMessages import (
    PersistentMessage,
    PersistentMessageDeleteInput,
    PersistentMessages,
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


@router.get("/{guild_id}/get/all", response_model=PersistentMessages)
async def get_all(guild_id: int, db: AsyncSession = Depends(get_db_session)):
    """Gets all persistent messages for the guild"""

    db_results = await persistent_messages.get(db=db, guild_id=guild_id)
    return PersistentMessages(messages=[PersistentMessage.from_orm(result) for result in db_results])


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


@router.delete("/{guild_id}/delete", response_model=EmptyResponseModel)
async def delete(guild_id: int, to_delete: PersistentMessageDeleteInput, db: AsyncSession = Depends(get_db_session)):
    """Deletes a persistent message"""

    await persistent_messages.delete(db=db, guild_id=guild_id, to_delete=to_delete)
    return EmptyResponseModel()


@router.delete("/{guild_id}/delete/all", response_model=EmptyResponseModel)
async def delete_all(guild_id: int, db: AsyncSession = Depends(get_db_session)):
    """Deletes all persistent messages for a guild"""

    await persistent_messages.delete_all(db=db, guild_id=guild_id)
    return EmptyResponseModel()
