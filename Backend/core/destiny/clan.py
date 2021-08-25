import dataclasses
import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.database.models import DiscordUsers
from Backend.networking.bungieApi import BungieApi
from Backend.core.destiny.routes import (
    clan_admins_route,
    clan_get_route,
    clan_invite_route,
    clan_members_route,
)
from Backend.schemas.destiny.clan import DestinyClanLink, DestinyClanMemberModel


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
        self.api = BungieApi(discord_id=self.discord_id)

    async def get_clan_id_and_name(self) -> tuple[int, str]:
        """Gets clan information"""

        route = clan_get_route.format(system=self.system, destiny_id=self.destiny_id)
        result = await self.api.get_json_from_url(
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

        results = (await self.api.get_json_from_url(route=route, params=params)).content["results"]

        members = []
        for result in results:
            members.append(
                DestinyClanMemberModel(
                    system=result["destinyUserInfo"]["membershipType"],
                    destiny_id=int(result["destinyUserInfo"]["membershipId"]),
                    name=f"""{result["destinyUserInfo"]["bungieGlobalDisplayName"]}#{result["destinyUserInfo"]["bungieGlobalDisplayNameCode"]}""",
                    is_online=result["isOnline"],
                    last_online_status_change=datetime.datetime.strptime(
                        result["lastOnlineStatusChange"], "%Y-%m-%dT%H:%M:%SZ"
                    ),
                    join_date=datetime.datetime.strptime(result["joinDate"], "%Y-%m-%dT%H:%M:%SZ"),
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

        results = (await self.api.get_json_from_url(route=route)).content["results"]

        # look if destiny_id is in there
        for result in results:
            if int(result["destinyUserInfo"]["membershipId"]) == self.destiny_id:
                return True

        return False

    async def invite_to_clan(
        self,
        to_invite_discord_id: int,
        to_invite_system: int,
    ):
        """Invite the User to the clan"""

        clan_id, clan_name = await self.get_clan_id_and_name()

        route = clan_invite_route.format(clan_id=clan_id, system=to_invite_system, destiny_id=to_invite_discord_id)

        welcome_message = {"message": f"Welcome to {clan_name}"}

        # catch the exception if it fails and send a new one
        try:
            await self.api.post_json_to_url(db=self.db, route=route, json=welcome_message)
        except CustomException:
            raise CustomException("ClanInviteFailed")
