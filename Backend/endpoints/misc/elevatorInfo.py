from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud import elevator_servers
from Backend.dependencies import get_db_session
from Shared.NetworkingSchemas import (
    ElevatorGuildModel,
    ElevatorGuildsModel,
    EmptyResponseModel,
)

router = APIRouter(
    prefix="/elevator/discord_servers",
    tags=["elevator"],
)


@router.get("/get/all", response_model=ElevatorGuildsModel)  # has test
async def get_discord_servers(db: AsyncSession = Depends(get_db_session)):
    """Get all discord servers Elevator is currently in"""

    results = await elevator_servers.get(db)
    return ElevatorGuildsModel(guilds=[ElevatorGuildModel.from_orm(result) for result in results])


@router.post("/add/{guild_id}", response_model=EmptyResponseModel)  # has test
async def add_discord_server(guild_id: int, db: AsyncSession = Depends(get_db_session)):
    """Add a discord server to the ones Elevator is currently in"""

    await elevator_servers.insert(db, guild_id)
    return EmptyResponseModel()


@router.delete("/delete/{guild_id}", response_model=EmptyResponseModel)  # has test
async def delete_discord_server(guild_id: int, db: AsyncSession = Depends(get_db_session)):
    """Delete a discord server from the ones Elevator is currently in"""

    await elevator_servers.delete(db, guild_id)
    return EmptyResponseModel()
