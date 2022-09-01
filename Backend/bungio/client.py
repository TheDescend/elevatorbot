import datetime
import logging
import os

from aiohttp_client_cache import RedisBackend
from bungio import Client
from bungio.models import AuthData

from Backend.database import acquire_db_session, is_test_mode, setup_engine
from Shared.functions.readSettingsFile import get_setting


class MyClient(Client):
    async def on_token_update(self, before: AuthData | None, after: AuthData) -> None:
        from Backend.crud.destiny.discordUsers import discord_users

        async with acquire_db_session() as db:
            user = await discord_users.get_profile_from_destiny_id(destiny_id=after.membership_id, db=db)
            await discord_users.update(
                db=db,
                to_update=user,
                token=after.token,
                refresh_token=after.refresh_token,
                token_expiry=after.token_expiry,
                refresh_token_expiry=after.refresh_token_expiry,
            )

        self.logger.debug(f"Updated token for {before.membership_id=}: {before.token=} -> {after.token=}")

    async def on_manifest_update(self) -> None:
        from Backend.bungio.manifest import destiny_manifest

        await destiny_manifest.reset()
        self.logger.debug(f"Destiny manifest was updated by bungie")


# noinspection PyTypeChecker
_BUNGIO_CLIENT: MyClient = None


def get_bungio_client() -> MyClient:
    global _BUNGIO_CLIENT

    if not _BUNGIO_CLIENT:
        _BUNGIO_CLIENT = MyClient(
            bungie_client_id=get_setting("BUNGIE_APPLICATION_CLIENT_ID"),
            bungie_client_secret=get_setting("BUNGIE_APPLICATION_CLIENT_SECRET"),
            bungie_token=get_setting("BUNGIE_APPLICATION_API_KEY"),
            logger=logging.getLogger("bungio"),
            cache=RedisBackend(
                cache_name="backend",
                address=f"""redis://{os.environ.get("REDIS_HOST")}:{os.environ.get("REDIS_PORT")}""",
                allowed_methods=["GET"],
                expire_after=datetime.timedelta(minutes=5),
                urls_expire_after={
                    "**/platform/app/oauth/token": 0,  # do not save token stuff
                    "**/Destiny2/Stats/PostGameCarnageReport": 0,  # do not save pgcr. We save them anyway and don't look them up more than once
                    "**/Destiny2/*/Profile/**components=": datetime.timedelta(minutes=30),  # profile call
                    "**/Destiny2/*/Account/*/Stats": datetime.timedelta(minutes=60),  # stats
                    "**/Destiny2/*/Account/*/Character/*/Stats/Activities": datetime.timedelta(
                        minutes=5
                    ),  # activity history
                    "**/GroupV2/*/Members": datetime.timedelta(minutes=60),  # all clan member stuff
                    "**/GroupV2/*/AdminsAndFounder": datetime.timedelta(minutes=60),  # all clan admin stuff
                    "**/GroupV2": datetime.timedelta(days=1),  # all clan stuff
                },
            ),
            manifest_storage=setup_engine(),
        )

    return _BUNGIO_CLIENT
