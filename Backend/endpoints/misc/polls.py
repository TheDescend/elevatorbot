from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud import polls
from Backend.dependencies import get_db_session
from NetworkingSchemas.basic import EmptyResponseModel
from NetworkingSchemas.misc.polls import (
    PollInsertSchema,
    PollSchema,
    PollUserInputSchema,
)

router = APIRouter(
    prefix="/polls/{guild_id}",
    tags=["polls"],
)


@router.post("/{discord_id}/insert", response_model=PollSchema)
async def insert(
    guild_id: int, discord_id: int, insert_data: PollInsertSchema, db: AsyncSession = Depends(get_db_session)
):
    """Insert a poll"""

    result = await polls.upsert(db=db, **insert_data.dict())
    return PollSchema.from_orm(result)


@router.get("/{discord_id}/get/{poll_id}", response_model=PollSchema)
async def get(guild_id: int, discord_id: int, poll_id: int, db: AsyncSession = Depends(get_db_session)):
    """Gets a poll"""

    result = await polls.get(db=db, poll_id=poll_id)
    return PollSchema.from_orm(result)


@router.delete("/{discord_id}/{poll_id}/delete_option/{option_name}", response_model=PollSchema)
async def delete_option(
    guild_id: int,
    discord_id: int,
    poll_id: int,
    option_name: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Update a poll. The poll data can be get from the embed clientside"""

    result = await polls.delete_option(db=db, poll_id=poll_id, invoker_user_id=discord_id, option=option_name)
    return PollSchema.from_orm(result)


@router.post("/{discord_id}/user_input/{poll_id}", response_model=PollSchema)
async def user_input(
    guild_id: int,
    discord_id: int,
    poll_id: int,
    user_input_data: PollUserInputSchema,
    db: AsyncSession = Depends(get_db_session),
):
    """Called when a user pressed voted."""

    result = await polls.user_input(db=db, poll_id=poll_id, **user_input_data.dict())
    return PollSchema.from_orm(result)


@router.delete("/{discord_id}/delete/{poll_id}", response_model=PollSchema)
async def delete(guild_id: int, discord_id: int, poll_id: int, db: AsyncSession = Depends(get_db_session)):
    """Deletes a poll"""

    result = await polls.delete(db=db, poll_id=poll_id, invoker_user_id=discord_id)
    return PollSchema.from_orm(result)


@router.delete("/delete/all", response_model=EmptyResponseModel)
async def delete(guild_id: int, db: AsyncSession = Depends(get_db_session)):
    """Deletes all polls for a guild"""

    await polls.delete_all(db=db, guild_id=guild_id)
    return EmptyResponseModel()
