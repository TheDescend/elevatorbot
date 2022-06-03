from fastapi import APIRouter

from Backend.crud import polls
from Backend.database import acquire_db_session
from Shared.networkingSchemas import EmptyResponseModel
from Shared.networkingSchemas.misc.polls import PollChoice, PollInsertSchema, PollSchema, PollUserInputSchema

router = APIRouter(
    prefix="/polls/{guild_id}",
    tags=["polls"],
)


@router.post("/{discord_id}/insert", response_model=PollSchema)  # has test
async def insert(guild_id: int, discord_id: int, insert_data: PollInsertSchema):
    """Insert a poll"""

    async with acquire_db_session() as db:
        result = await polls.upsert(db=db, **insert_data.dict())

        poll = PollSchema.from_orm(result)
        poll.choices = (
            [PollChoice(name=name, discord_ids=discord_ids) for name, discord_ids in result.data.items()]
            if result.data
            else []
        )
        return poll


@router.get("/{discord_id}/get/{poll_id}", response_model=PollSchema)  # has test
async def get(guild_id: int, discord_id: int, poll_id: int):
    """Gets a poll"""

    async with acquire_db_session() as db:
        result = await polls.get(db=db, poll_id=poll_id)

        poll = PollSchema.from_orm(result)
        poll.choices = (
            [PollChoice(name=name, discord_ids=discord_ids) for name, discord_ids in result.data.items()]
            if result.data
            else []
        )
        return poll


@router.delete("/{discord_id}/{poll_id}/delete_option/{option_name}", response_model=PollSchema)  # has test
async def delete_option(guild_id: int, discord_id: int, poll_id: int, option_name: str):
    """Update a poll. The poll data can be get from the embed clientside"""

    async with acquire_db_session() as db:
        result = await polls.delete_option(db=db, poll_id=poll_id, invoker_user_id=discord_id, option=option_name)

        poll = PollSchema.from_orm(result)
        poll.choices = (
            [PollChoice(name=name, discord_ids=discord_ids) for name, discord_ids in result.data.items()]
            if result.data
            else []
        )
        return poll


@router.post("/{discord_id}/{poll_id}/user_input", response_model=PollSchema)  # has test
async def user_input(guild_id: int, discord_id: int, poll_id: int, user_input_data: PollUserInputSchema):
    """Called when a user pressed voted."""

    async with acquire_db_session() as db:
        result = await polls.user_input(
            db=db, poll_id=poll_id, user_id=discord_id, choice_name=user_input_data.choice_name
        )

        poll = PollSchema.from_orm(result)
        poll.choices = (
            [PollChoice(name=name, discord_ids=discord_ids) for name, discord_ids in result.data.items()]
            if result.data
            else []
        )
        return poll


@router.delete("/delete/all", response_model=EmptyResponseModel)  # has test
async def delete_all(guild_id: int):
    """Deletes all polls for a guild"""

    async with acquire_db_session() as db:
        await polls.delete_all(db=db, guild_id=guild_id)
        return EmptyResponseModel()


@router.delete("/{discord_id}/{poll_id}/delete", response_model=PollSchema)  # has test
async def delete(guild_id: int, discord_id: int, poll_id: int):
    """Deletes a poll"""

    async with acquire_db_session() as db:
        result = await polls.delete(db=db, poll_id=poll_id, invoker_user_id=discord_id)

        poll = PollSchema.from_orm(result)
        poll.choices = (
            [PollChoice(name=name, discord_ids=discord_ids) for name, discord_ids in result.data.items()]
            if result.data
            else []
        )
        return poll
