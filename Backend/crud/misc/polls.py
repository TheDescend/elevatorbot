from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from Backend.core.errors import CustomException
from Backend.crud.base import CRUDBase
from Backend.database.models import Poll
from Backend.misc.helperFunctions import convert_kwargs_into_dict
from Shared.networkingSchemas.misc.polls import PollChoice


class CRUDPolls(CRUDBase):
    async def get(self, db: AsyncSession, poll_id: int) -> Poll:
        """Get the poll"""

        result = await self._get_with_key(db=db, primary_key=poll_id)

        if not result:
            raise CustomException("PollNotExist")

        return result

    async def upsert(
        self,
        db: AsyncSession,
        poll_id: Optional[int] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        author_id: Optional[str] = None,
        guild_id: Optional[str] = None,
        channel_id: Optional[str] = None,
        message_id: Optional[str] = None,
        choices: Optional[list[PollChoice]] = None,
    ) -> Poll:
        """Upsert the poll"""

        # convert kwargs into dict
        upsert_dict = convert_kwargs_into_dict(
            id=poll_id,
            name=name,
            description=description,
            data={choice.name: choice.discord_ids for choice in choices} if choices else {},
            author_id=author_id,
            guild_id=guild_id,
            channel_id=channel_id,
            message_id=message_id,
        )

        model = await self._upsert(db=db, model_data=upsert_dict)

        return model

    async def user_input(self, db: AsyncSession, poll_id: int, choice_name: str, user_id: int) -> Poll:
        """Update a user's choice"""

        poll = await self.get(db=db, poll_id=poll_id)

        # look if the user voted before and remove that
        for name, user_ids in poll.data.items():
            if user_id in user_ids:
                user_ids.remove(user_id)

        # now add the user vote
        # since the option might be new, checking that first
        if choice_name not in poll.data:
            poll.data.update({choice_name: []})
        poll.data[choice_name].append(user_id)

        # flag it as modified, otherwise sqlalchemy won't update it
        flag_modified(poll, "data")
        await db.flush()

        return poll

    async def delete_option(self, db: AsyncSession, poll_id: int, option: str, invoker_user_id: int) -> Poll:
        """Delete a poll option"""

        poll = await self.get(db=db, poll_id=poll_id)

        if poll.author_id != invoker_user_id:
            raise CustomException("PollNoPermission")

        if option not in poll.data:
            raise CustomException("PollOptionNotExist")

        poll.data.pop(option)

        # flag it as modified, otherwise sqlalchemy won't update it
        flag_modified(poll, "data")
        await db.flush()

        return poll

    async def delete(self, db: AsyncSession, poll_id: int, invoker_user_id: int) -> Poll:
        """Delete the poll"""

        poll = await self.get(db=db, poll_id=poll_id)

        if poll.author_id != invoker_user_id:
            raise CustomException("PollNoPermission")

        await self._delete(db=db, obj=poll)

        return poll

    async def delete_all(self, db: AsyncSession, guild_id: int):
        """Deletes all polls for the guild"""

        await self._delete_multi(db=db, guild_id=guild_id)


polls = CRUDPolls(Poll)
