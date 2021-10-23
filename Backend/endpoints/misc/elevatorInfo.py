from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud import elevator_servers
from Backend.dependencies import get_db_session
from Backend.schemas.empty import EmptyResponseModel
from Backend.schemas.misc.elevatorInfo import ElevatorGuildModel, ElevatorGuildsModel

router = APIRouter(
    prefix="/elevator",
    tags=["elevator"],
)


@router.get("/discordServers/get", response_model=ElevatorGuildsModel)
async def get_discord_servers(db: AsyncSession = Depends(get_db_session)):
    """Saves a bungie token"""

    results = await elevator_servers.get(db)
    return ElevatorGuildsModel(guilds=[ElevatorGuildModel.from_orm(result) for result in results])


@router.post("/discordServers/add/{guild_id}", response_model=EmptyResponseModel)
async def add_discord_server(guild_id: int, db: AsyncSession = Depends(get_db_session)):
    """Add a discord server to the ones Elevator is currently in"""

    await elevator_servers.insert(db, guild_id)
    return EmptyResponseModel()


@router.delete("/discordServers/delete/{guild_id}", response_model=EmptyResponseModel)
async def delete_discord_server(guild_id: int, db: AsyncSession = Depends(get_db_session)):
    """Delete a discord server from the ones Elevator is currently in"""

    await elevator_servers.delete(db, guild_id)
    return EmptyResponseModel()
