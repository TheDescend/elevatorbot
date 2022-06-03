from fastapi import APIRouter

from Backend.crud import d2_steam_players
from Backend.database import acquire_db_session
from Shared.networkingSchemas.destiny import DestinySteamPlayerCountModel, DestinySteamPlayersCountModel

router = APIRouter(
    prefix="/destiny/steam_players",
    tags=["destiny", "steam_players"],
)


@router.get("/get/all", response_model=DestinySteamPlayersCountModel)
async def get():
    """Return the steam players and times"""

    async with acquire_db_session() as db:
        data = DestinySteamPlayersCountModel()

        # get and prepare data
        result = await d2_steam_players.get_all(db=db)
        for entry in result:
            data.entries.append(DestinySteamPlayerCountModel.from_orm(entry))

        return data
