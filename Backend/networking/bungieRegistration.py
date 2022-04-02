import dataclasses

import aiohttp
from orjson import orjson

from Backend.networking.bungieApi import BungieApi, bungie_auth_headers
from Backend.networking.bungieRoutes import auth_route
from Shared.networkingSchemas.misc.auth import BungieRegistrationInput, BungieTokenInput


@dataclasses.dataclass
class BungieRegistration(BungieApi):
    async def get_first_token(self, user_input: BungieRegistrationInput) -> BungieTokenInput:
        """Returns the first token of the user with their authorization code"""

        data = {
            "grant_type": "authorization_code",
            "code": user_input.code,
        }

        # get the token
        async with aiohttp.ClientSession(json_serialize=lambda x: orjson.dumps(x).decode()) as session:
            response = await self._request(
                session=session,
                method="POST",
                route=auth_route,
                form_data=data,
                headers=bungie_auth_headers,
            )

            # parse the token data and return it
            return BungieTokenInput(
                access_token=response.content["access_token"],
                token_type=response.content["token_type"],
                expires_in=int(response.content["expires_in"]),
                refresh_token=response.content["refresh_token"],
                refresh_expires_in=int(response.content["refresh_expires_in"]),
                membership_id=response.content["membership_id"],
                state=user_input.state,
            )
