from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud import d2_steam_players
from Backend.dependencies import get_db_session
from NetworkingSchemas.destiny.steamPlayers import (
    DestinySteamPlayerCountModel,
    DestinySteamPlayersCountModel,
)

router = APIRouter(
    prefix="/steam_players",
    tags=["destiny", "steam_players"],
)


@router.get("/get", response_model=DestinySteamPlayersCountModel)
async def get(db: AsyncSession = Depends(get_db_session)):
    """Return the steam players and times"""

    data = DestinySteamPlayersCountModel()

    # get and prepare data
    result = await d2_steam_players.get_all(db=db)
    for entry in result:
        data.entries.append(DestinySteamPlayerCountModel(date=entry.date, number_of_players=entry.number_of_players))

    return result
