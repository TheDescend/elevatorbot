import dataclasses
import time

import aiohttp

from Backend.core.errors import CustomException
from Backend.networking.models import BungieToken
from Backend.networking.base import NetworkBase
from settings import B64_SECRET


@dataclasses.dataclass
class BungieAuth(NetworkBase):
    discord_id: int

    route = "https://www.bungie.net/platform/app/oauth/token/"
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "authorization": "Basic " + str(B64_SECRET),
    }

    bungie_request = True


    async def get_working_token(
        self,
    ) -> BungieToken:
        """ Returns token or raises an error """

        token = BungieToken(token=await getToken(discord_id))
        if not token.token:
            raise CustomException("DiscordIdNotFound")

        # check expiry
        expiry = await getTokenExpiry(discord_id)
        current_time = int(time.time())

        # check refresh token first, since they need to re-register otherwise
        if current_time > expiry[1]:
            raise CustomException("NoToken")

        # refresh token if outdated
        if current_time > expiry[0]:
            token.token = await self.__refresh_token()
            if not token.token:
                raise CustomException("NoToken")

        return token


    async def __refresh_token(
        self,
    ) -> str:
        """ Updates the token and saves it to the DB. Raises an error if failed """

        oauth_refresh_token = await getRefreshToken(discord_id)
        if not oauth_refresh_token:
            raise CustomException("NoToken")

        data = {
            "grant_type": "__refresh_token",
            "refresh_token": str(oauth_refresh_token),
        }

        # get a new token
        async with aiohttp.ClientSession() as session:
            current_time = int(time.time())
            response = await self._post_request(
                session=session,
                route=self.route,
                data=data,
                headers=self.headers,
            )
            if response:
                access_token = response.content["access_token"]
                new_refresh_token = response.content["refresh_token"]
                token_expiry = current_time + response.content["expires_in"]
                refresh_token_expiry = current_time + response.content["refresh_expires_in"]

                # update db entry
                await updateToken(

                )

                return access_token
