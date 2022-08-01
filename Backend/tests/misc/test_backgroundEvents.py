import pytest
from anyio import create_task_group
from dummyData.insert import mock_bungio_request, mock_request
from dummyData.static import dummy_discord_id
from pytest_mock import MockerFixture

from Backend import backgroundEvents
from Backend.core.destiny.activities import DestinyActivities
from Backend.crud import discord_users
from Backend.database import acquire_db_session


@pytest.mark.asyncio
async def test_background_events(mocker: MockerFixture):
    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)
    mocker.patch("bungio.http.client.HttpClient._request", mock_bungio_request)
    mocker.patch("aiohttp.ClientSession._request", mock_request)

    for BackgroundEvent in backgroundEvents.BaseEvent.__subclasses__():
        event = BackgroundEvent()

        await event.run()


@pytest.mark.asyncio
async def test_activity_update_parallelisation(mocker: MockerFixture):
    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)
    mocker.patch("bungio.http.client.HttpClient._request", mock_bungio_request)
    mocker.patch("aiohttp.ClientSession._request", mock_request)

    async with create_task_group() as tg:
        async with acquire_db_session() as db:
            for _ in range(20):
                user = await discord_users.get_profile_from_discord_id(dummy_discord_id, db=db)
                activities = DestinyActivities(db=db, user=user)
                tg.start_soon(lambda: activities.update_activity_db())
