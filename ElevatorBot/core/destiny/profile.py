from __future__ import annotations

import dataclasses
from typing import Union

import discord

from ElevatorBot.core.http import BaseBackendConnection
from ElevatorBot.core.results import BackendResult
from ElevatorBot.core.routes import destiny_profile_from_destiny_id_route, destiny_profile_from_discord_id_route


@dataclasses.dataclass(init=False)
class DestinyProfile(BaseBackendConnection):
    """ Get basic destiny information (discord_member, destiny_id, system) """

    # save user information
    # these fields get populated via @classmethod calls
    discord_member: discord.Member
    discord_guild: discord.Guild
    destiny_id: int
    system: int


    @classmethod
    async def from_destiny_id(
        cls,
        client: discord.Client,
        discord_guild: discord.Guild,
        destiny_id: int
    ) -> Union[DestinyProfile, BackendResult]:
        """ Get the destiny profile with a destiny_id """

        class_instance = cls(
            client=client
        )

        # query the backend
        result = await class_instance._backend_get(
            destiny_profile_from_destiny_id_route.format(
                destiny_id=destiny_id
            )
        )

        # check if that id exists
        if not result:
            result.error_message = {
                "destiny_id": destiny_id
            }
            return result

        # set new attributes
        class_instance.destiny_id = destiny_id
        class_instance.system = result.result["system"]
        class_instance.discord_guild = discord_guild
        class_instance.discord_member = discord_guild.get_member(result.result["discord_id"])

        # check if the discord member is actually found
        if not class_instance.discord_member:
            result.error = "DestinyIdNotFound"
            result.error_message = {
                "destiny_id": destiny_id
            }
            return result

        return class_instance


    @classmethod
    async def from_discord_member(
        cls,
        client: discord.Client,
        discord_guild: discord.Guild,
        discord_member: discord.Member
    ) -> Union[DestinyProfile, BackendResult]:
        """ Get the destiny profile with a discord member object """

        class_instance = cls(
            client=client,
        )

        # query the backend
        result = await class_instance._backend_get(
            destiny_profile_from_discord_id_route.format(
                discord_id=discord_member.id
            )
        )

        # check if that id exists
        if not result:
            result.error_message = {
                "discord_member": discord_member
            }
            return result

        # set new attributes
        class_instance.destiny_id = result.result["destiny_id"]
        class_instance.system = result.result["system"]
        class_instance.discord_guild = discord_guild
        class_instance.discord_member = discord_member

        return class_instance


    async def delete(
        self
    ):
        """ Delete the profile """

        # todo delete info. fe on /unregister calls
        pass


