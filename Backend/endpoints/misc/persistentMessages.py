from fastapi import APIRouter

from Backend.crud import persistent_messages
from Backend.database import acquire_db_session
from Shared.networkingSchemas import EmptyResponseModel
from Shared.networkingSchemas.misc.persistentMessages import (
    PersistentMessage,
    PersistentMessageDeleteInput,
    PersistentMessages,
    PersistentMessageUpsert,
)

router = APIRouter(
    prefix="/persistentMessages/{guild_id}",
    tags=["persistent messages"],
)


@router.get("/get/all", response_model=PersistentMessages)  # has test
async def get_all(guild_id: int):
    """Gets all persistent messages for the guild"""

    async with acquire_db_session() as db:
        db_results = await persistent_messages.get_all_guild(db=db, guild_id=guild_id)
        return PersistentMessages(messages=[PersistentMessage.from_orm(result) for result in db_results])


@router.get("/get/{message_name}", response_model=PersistentMessage)  # has test
async def get(guild_id: int, message_name: str):
    """Gets a persistent message"""

    async with acquire_db_session() as db:
        result = await persistent_messages.get(db=db, guild_id=guild_id, message_name=message_name)
        return PersistentMessage.from_orm(result)


@router.post("/upsert/{message_name}", response_model=PersistentMessage)  # has test
async def upsert(guild_id: int, message_name: str, update_data: PersistentMessageUpsert):
    """Upserts a persistent message"""

    async with acquire_db_session() as db:
        result = await persistent_messages.upsert(
            db=db,
            guild_id=guild_id,
            message_name=message_name,
            channel_id=update_data.channel_id,
            message_id=update_data.message_id,
        )
        return PersistentMessage.from_orm(result)


@router.post("/delete", response_model=EmptyResponseModel)  # has test
async def delete(guild_id: int, to_delete: PersistentMessageDeleteInput):
    """Deletes a persistent message"""

    async with acquire_db_session() as db:
        await persistent_messages.delete(db=db, guild_id=guild_id, to_delete=to_delete)

    return EmptyResponseModel()


@router.delete("/delete/all", response_model=EmptyResponseModel)  # has test
async def delete_all(guild_id: int):
    """Deletes all persistent messages for a guild"""

    async with acquire_db_session() as db:
        await persistent_messages.delete_all(db=db, guild_id=guild_id)

    return EmptyResponseModel()
