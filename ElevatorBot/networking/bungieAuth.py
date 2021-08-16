import time
from typing import Optional

import aiohttp

from database.database import getRefreshToken, lookupDestinyID, updateToken, getToken, getTokenExpiry
from networking.models import BungieToken
from networking.networkBackend import post_request
from static.config import B64_SECRET


async def handle_and_return_token(
    discord_id: int
) -> BungieToken:
    """ Returns token if exists with an error message """

    token = BungieToken(
        token=await getToken(discord_id)
    )
    if not token.token:
        token.error = "User has not registered"
        return token

    # refresh token if expired
    expiry = await getTokenExpiry(discord_id)
    if not expiry:
        token.error = "User tokens have no expiry date"
        return token

    current_time = int(time.time())

    # check refresh token first, since they need to re-register otherwise
    if current_time > expiry[1]:
        token.error = "Registration is outdated, please re-register using `/registerdesc"
        return token

    # refresh token if outdated
    if current_time > expiry[0]:
        token.token = await refresh_token(discord_id)
        if not token.token:
            token.error = "Token refresh failed"
            return token

    return token


async def refresh_token(
    discord_id: int
) -> Optional[str]:
    """
    takes the discord snowflakes, writes a new refresh token, access token to the DB and
    returns the access token or None if failed
    """

    url = 'https://www.bungie.net/platform/app/oauth/token/'
    oauth_headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'authorization': 'Basic ' + str(B64_SECRET)
    }
    oauth_refresh_token = await getRefreshToken(discord_id)
    if not oauth_refresh_token:
        return None

    destiny_id = await lookupDestinyID(discord_id)

    data = {
        "grant_type": "refresh_token",
        "refresh_token": str(oauth_refresh_token),
    }

    # get a new token
    async with aiohttp.ClientSession() as session:
        current_time = int(time.time())
        response = await post_request(
            session=session,
            url=url,
            data=data,
            headers=oauth_headers,
            bungie_request=True,
        )
        if response:
            access_token = response.content['access_token']
            new_refresh_token = response.content['refresh_token']
            token_expiry = current_time + response.content['expires_in']
            refresh_token_expiry = current_time + response.content['refresh_expires_in']

            # update db entry
            await updateToken(destiny_id, discord_id, access_token, new_refresh_token, token_expiry, refresh_token_expiry)

            return access_token

        else:
            return
