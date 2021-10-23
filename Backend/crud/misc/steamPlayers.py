import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud.base import CRUDBase
from Backend.database.models import D2SteamPlayer


class CRUDSteamPlayers(CRUDBase):
    async def upsert(self, db: AsyncSession, player_count: int):
        """Upsert the data"""

        # get the current date
        now = datetime.date.today()

        # get the players for the current date
        current_value = await self._get_with_key(db=db, primary_key=now)

        # if that doesn't exist insert
        if not current_value:
            await self._insert(db=db, to_create=D2SteamPlayer(date=now, number_of_players=player_count))

        # otherwise check if the new value is higher before updating
        else:
            if current_value.number_of_players < player_count:
                await self._update(db=db, to_update=current_value, number_of_players=player_count)

    async def get_all(self, db: AsyncSession) -> list[D2SteamPlayer]:
        """Get all player counts for every date"""

        return await self._get_all(db=db)


d2_steam_players = CRUDSteamPlayers(D2SteamPlayer)
