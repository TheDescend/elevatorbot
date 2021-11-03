from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud import polls
from Backend.dependencies import get_db_session
from NetworkingSchemas.misc.polls import (
    PollInsertSchema,
    PollSchema,
    PollUserInputSchema,
)

router = APIRouter(
    prefix="/polls/{guild_id}/{discord_id}",
    tags=["polls"],
)

# todo check that users have perms to update / delete poll
# todo check that the guild is correct


@router.post("/insert", response_model=PollSchema)
async def insert(
    guild_id: int, discord_id: int, insert_data: PollInsertSchema, db: AsyncSession = Depends(get_db_session)
):
    """Insert a poll"""

    result = await polls.upsert(db=db, **insert_data.dict())
    return PollSchema.from_orm(result)


@router.get("/{poll_id}/get", response_model=PollSchema)
async def get(guild_id: int, discord_id: int, poll_id: int, db: AsyncSession = Depends(get_db_session)):
    """Gets a persistent message"""

    result = await polls.get(db=db, poll_id=poll_id)
    return PollSchema.from_orm(result)


@router.delete("/{poll_id}/delete_option/{option_name}", response_model=PollSchema)
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


@router.post("/{poll_id}/user_input", response_model=PollSchema)
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


@router.delete("/{poll_id}/delete", response_model=PollSchema)
async def delete(guild_id: int, discord_id: int, poll_id: int, db: AsyncSession = Depends(get_db_session)):
    """Deletes a poll"""

    result = await polls.delete(db=db, poll_id=poll_id, invoker_user_id=discord_id)
    return PollSchema.from_orm(result)
