import pytest as pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from static import (
    dummy_bungie_name,
    dummy_discord_guild_id,
    dummy_discord_id,
    dummy_gotten_collectible_id,
    dummy_not_gotten_collectible_id,
)


@pytest.mark.asyncio
async def test_destiny_name(db: AsyncSession, client: AsyncClient):
    r = await client.get(f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/name/")
    assert r.status_code == 200
    assert r.json() == {"name": dummy_bungie_name}

    r = await client.get(f"/destiny/0/0/account/name")
    assert r.status_code == 409
    assert r.json() == {"error": "DiscordIdNotFound"}


@pytest.mark.asyncio
async def test_has_collectible(db: AsyncSession, client: AsyncClient):
    r = await client.get(
        f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/collectible/{dummy_gotten_collectible_id}"
    )
    assert r.status_code == 200
    assert r.json() == {"bool": True}

    r = await client.get(
        f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/collectible/{dummy_not_gotten_collectible_id}"
    )
    assert r.status_code == 200
    assert r.json() == {"bool": False}
