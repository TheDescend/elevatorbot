import dataclasses
import datetime
import time

import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.crud import discord_users
from Backend.database.models import DiscordUsers
from Backend.misc.helperFunctions import get_now_with_tz, localize_datetime
from Backend.networking.base import NetworkBase
from settings import B64_SECRET


@dataclasses.dataclass
class BungieAuth(NetworkBase):
    discord_id: int
    db: AsyncSession

    route = "https://www.bungie.net/platform/app/oauth/token/"
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "authorization": "Basic " + str(B64_SECRET),
    }

    bungie_request = True
    user: DiscordUsers = dataclasses.field(init=False)

    async def get_working_token(
        self,
    ) -> str:
        """Returns token or raises an error"""

        self.user = discord_users.get_profile_from_discord_id(db=self.db, discord_id=self.discord_id)
        if not self.user.token:
            raise CustomException(
                error="NoToken",
            )

        token = self.user.token

        # check refresh token expiry
        current_time = get_now_with_tz()
        if current_time > self.user.refresh_token_expiry:
            raise CustomException("NoToken")

        # refresh token if outdated
        if current_time > self.user.token_expiry:
            token = await self.__refresh_token()

        return token

    async def __refresh_token(
        self,
    ) -> str:
        """Updates the token and saves it to the DB. Raises an error if failed"""

        data = {
            "grant_type": "refresh_token",
            "refresh_token": str(self.user.refresh_token),
        }

        # get a new token
        async with aiohttp.ClientSession() as session:
            current_time = int(time.time())
            response = await self._post_request(
                session=session,
                route=self.route,
                form_data=data,
                headers=self.headers,
            )
            if response:
                access_token = response.content["access_token"]

                await discord_users.refresh_tokens(
                    db=self.db,
                    user=self.user,
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
