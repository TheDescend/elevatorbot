import dataclasses

from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.crud import discord_users
from Backend.database.models import DiscordUsers
from Backend.misc.helperFunctions import get_datetime_from_bungie_entry
from Backend.networking.bungieApi import BungieApi
from Backend.networking.bungieRoutes import (
    clan_admins_route,
    clan_get_route,
    clan_invite_route,
    clan_members_route,
)
from NetworkingSchemas.destiny.clan import DestinyClanMemberModel


@dataclasses.dataclass
class DestinyClan:
    """Clan specific API calls"""

    db: AsyncSession
    user: DiscordUsers

    def __post_init__(self):
        # some shortcuts
        self.discord_id = self.user.discord_id
        self.destiny_id = self.user.destiny_id
        self.system = self.user.system

        # the network class
        self.api = BungieApi(db=self.db, user=self.user)

    async def get_clan_id_and_name(self) -> tuple[int, str]:
        """Gets clan information"""

        route = clan_get_route.format(system=self.system, destiny_id=self.destiny_id)
        result = await self.api.get(
            route=route,
        )

        # check if clan exists
        if not result.content["results"]:
            raise CustomException("UserNotInClan")

        # we only care about the first one
        clan = result.content["results"][0]
        return int(clan["group"]["groupId"]), clan["group"]["name"]

    async def search_clan_for_member(
        self,
        member_name: str,
        clan_id: int = None,
    ) -> list[DestinyClanMemberModel]:
        """Search the clan for members with that name"""

        if not clan_id:
            clan_id, _ = await self.get_clan_id_and_name()

        route = clan_members_route.format(clan_id=clan_id)
        params = {"nameSearch": member_name}

        results = (await self.api.get(route=route, params=params)).content["results"]

        members = []
        for result in results:
            destiny_id = int(result["destinyUserInfo"]["membershipId"])

            # get discord data
            try:
                discord_data = await discord_users.get_profile_from_destiny_id(db=self.db, destiny_id=destiny_id)
            except CustomException:
                discord_data = None

            members.append(
                DestinyClanMemberModel(
                    system=result["destinyUserInfo"]["membershipType"],
                    destiny_id=destiny_id,
                    name=f"""{result["destinyUserInfo"]["bungieGlobalDisplayName"]}#{result["destinyUserInfo"]["bungieGlobalDisplayNameCode"]}""",
                    is_online=result["isOnline"],
                    last_online_status_change=get_datetime_from_bungie_entry(result["lastOnlineStatusChange"]),
                    join_date=get_datetime_from_bungie_entry(result["joinDate"]),
                    discord_id=discord_data.discord_id if discord_data else None,
                )
            )

        return members

    async def get_clan_members(self, clan_id: int = None) -> list[DestinyClanMemberModel]:
        """Get all clan members from a clan"""

        # searching for an empty string results in the same. Just less duplicated code this way
        return await self.search_clan_for_member(member_name="", clan_id=clan_id)

    async def is_clan_admin(self, clan_id: int = None) -> bool:
        """Returns whether the user is an admin in the clan"""

        if not clan_id:
            clan_id, _ = await self.get_clan_id_and_name()

        route = clan_admins_route.format(clan_id=clan_id)

        results = (await self.api.get(route=route)).content["results"]

        # look if destiny_id is in there
        for result in results:
            if int(result["destinyUserInfo"]["membershipId"]) == self.destiny_id:
                return True

        return False

    async def invite_to_clan(
        self,
        to_invite_destiny_id: int,
        to_invite_system: int,
    ):
        """Invite the User to the clan"""

        clan_id, clan_name = await self.get_clan_id_and_name()

        # check if inviter actually is admin
        if not await self.is_clan_admin(clan_id=clan_id):
            raise CustomException("ClanNoPermissions")

        route = clan_invite_route.format(clan_id=clan_id, system=to_invite_system, destiny_id=to_invite_destiny_id)

        welcome_message = {"message": f"Welcome to {clan_name}"}

        # todo error out if already in clan. that should return a nice error by the api
        await self.api.post(route=route, json=welcome_message)
