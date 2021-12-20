import dataclasses
import datetime
import time

import aiohttp
from base64 import b64encode
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.crud import discord_users
from Backend.database.models import DiscordUsers
from Backend.misc.helperFunctions import get_now_with_tz, localize_datetime
from Backend.networking.base import NetworkBase
from settings import BUNGIE_APPLICATION_CLIENT_SECRET, BUNGIE_APPLICATION_CLIENT_ID


@dataclasses.dataclass
class BungieAuth(NetworkBase):
    db: AsyncSession
    user: DiscordUsers

    route = "https://www.bungie.net/platform/app/oauth/token/"
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "authorization": "Basic " + b64encode(f"{BUNGIE_APPLICATION_CLIENT_ID}:{BUNGIE_APPLICATION_CLIENT_SECRET}".encode("ascii")).decode("ascii"),
    }

    bungie_request: bool = True

    async def get_working_token(self) -> str:
        """Returns token or raises an error"""

        # check refresh token expiry and that it exists
        if await discord_users.token_is_expired(db=self.db, user=self.user):
            raise CustomException("NoToken")

        token = self.user.token

        current_time = get_now_with_tz()
        if current_time > self.user.refresh_token_expiry:
            # set token to None
            await discord_users.invalidate_token(db=self.db, user=self.user)

            raise CustomException("NoToken")

        # refresh token if outdated
        if current_time > self.user.token_expiry:
            token = await self.__refresh_token()

        return token

    async def __refresh_token(self) -> str:
        """Updates the token and saves it to the DB. Raises an error if failed"""

        data = {
            "grant_type": "refresh_token",
            "refresh_token": str(self.user.refresh_token),
        }

        # get a new token
        async with aiohttp.ClientSession() as session:
            current_time = int(time.time())

            try:
                response = await self._request(
                    session=session,
                    method="POST",
                    route=self.route,
                    form_data=data,
                    headers=self.headers,
                )
                if response:
                    access_token = response.content["access_token"]

                    await discord_users.update(
                        db=self.db,
                        to_update=self.user,
                        token=access_token,
                        refresh_token=response.content["refresh_token"],
                        token_expiry=localize_datetime(
                            datetime.datetime.fromtimestamp(current_time + int(response.content["expires_in"]))
                        ),
                        refresh_token_expiry=localize_datetime(
                            datetime.datetime.fromtimestamp(current_time + int(response.content["refresh_expires_in"]))
                        ),
                    )

                    return access_token

            except CustomException as exc:
                if exc.error == "NoToken":
                    # catch the NoToken error to invalidate the db
                    await discord_users.invalidate_token(db=self.db, user=self.user)

                raise exc
