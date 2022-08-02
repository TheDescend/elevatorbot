import asyncio
import datetime

import pytest
from bungio import Client
from bungio.models import AuthData
from dummyData.insert import mock_bungio_request, mock_request
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.bungio.client import get_bungio_client
from Backend.database import acquire_db_session
from Shared.functions.helperFunctions import get_min_with_tz, get_now_with_tz


class TestingClient(Client):
    MANIFEST_FIRST_UPDATE = True
    MANIFEST_SECOND_UPDATE = False

    async def on_token_update(self, before: AuthData | None, after: AuthData) -> None:
        from Backend.crud.destiny.discordUsers import discord_users

        # this should update the db entry
        if after.membership_id == 9999999:
            assert before.token_expiry == get_min_with_tz()

            async with acquire_db_session() as db:
                user = await discord_users.get_profile_from_discord_id(after.membership_id, db=db)
                await discord_users.update(
                    db=db,
                    to_update=user,
                    token=after.token,
                    refresh_token=after.refresh_token,
                    token_expiry=after.token_expiry,
                    refresh_token_expiry=after.refresh_token_expiry,
                )

            user = await discord_users.get_profile_from_discord_id(after.membership_id, db=db)
            assert user.token == "token"
            assert user.token == after.token
            assert user.token_expiry == after.token_expiry
            assert user.refresh_token == "refresh"
            assert user.refresh_token == after.refresh_token
            assert user.refresh_token_expiry == after.refresh_token_expiry

        # just testing if invalidating works
        elif after.membership_id == 1686521:
            assert after.token is None
            assert before.token is not None

    async def on_manifest_update(self) -> None:
        from Backend.bungio.manifest import destiny_manifest

        # noinspection PyProtectedMember
        async def assert_data():
            assert destiny_manifest._manifest_season_pass_definition
            assert destiny_manifest._manifest_seasonal_challenges_definition
            assert destiny_manifest._manifest_weapons
            assert destiny_manifest._manifest_collectibles
            assert destiny_manifest._manifest_lore
            assert destiny_manifest._manifest_triumphs
            assert destiny_manifest._manifest_seals
            assert destiny_manifest._manifest_catalysts
            assert destiny_manifest._manifest_activities
            assert destiny_manifest._manifest_grandmasters
            assert destiny_manifest._manifest_interesting_solos

        if self.MANIFEST_FIRST_UPDATE:
            self.MANIFEST_FIRST_UPDATE = False

        else:
            await destiny_manifest.reset()
            await assert_data()

            self.MANIFEST_SECOND_UPDATE = True


@pytest.mark.asyncio
async def test_manifest_update_count(db: AsyncSession, mocker: MockerFixture):
    mocker.patch("Backend.networking.http.NetworkBase._request", mock_request)
    mocker.patch("bungio.http.client.HttpClient._request", mock_bungio_request)

    # check for an update again, we do some funky manipulation to return a different version and check if it actually got updated
    get_bungio_client().manifest._Manifest__manifest_last_update = get_now_with_tz() - datetime.timedelta(hours=4)

    # noinspection PyProtectedMember
    await get_bungio_client().manifest._check_for_updates()

    # wait for all tasks to be done
    while get_bungio_client()._tasks:
        print("Tasks not done, sleeping")
        await asyncio.sleep(0.5)

    assert get_bungio_client().MANIFEST_FIRST_UPDATE is False
    assert get_bungio_client().MANIFEST_SECOND_UPDATE is True
