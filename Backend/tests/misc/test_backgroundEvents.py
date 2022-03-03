import pytest
from dummyData.insert import mock_request
from pytest_mock import MockerFixture

from Backend import backgroundEvents


@pytest.mark.asyncio
async def test_background_events(mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)
    mocker.patch("aiohttp.ClientSession._request", mock_request)

    for BackgroundEvent in backgroundEvents.BaseEvent.__subclasses__():
        event = BackgroundEvent()

        await event.run()
