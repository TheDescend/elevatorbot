import dataclasses
import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.crud import destiny_clan_links, discord_users
from Backend.database.models import DiscordUsers
from Backend.misc.helperFunctions import (
    get_datetime_from_bungie_entry,
    localize_datetime,
)
from Backend.networking.bungieApi import BungieApi
from Backend.networking.bungieRoutes import (
    clan_admins_route,
    clan_get_route,
    clan_invite_route,
    clan_kick_route,
    clan_members_route,
)
from NetworkingSchemas.destiny.clan import DestinyClanMemberModel, DestinyClanModel


@dataclasses.dataclass
class DestinyClan:
    """Clan specific API calls"""

    db: AsyncSession
    guild_id: int
    user: Optional[DiscordUsers] = None

    def __post_init__(self):
        # some shortcuts
        if self.user:
            self.discord_id = self.user.discord_id
            self.destiny_id = self.user.destiny_id
            self.system = self.user.system

        # the network class
        self.api = BungieApi(
            db=self.db, user=self.user, i_understand_what_im_doing_and_that_setting_this_to_true_might_break_stuff=True
        )

    async def get_clan(self) -> DestinyClanModel:
        """Gets clan information"""

        # get data from db
        link = await destiny_clan_links.get_link(db=self.db, discord_guild_id=self.guild_id)

        route = clan_get_route.format(clan_id=link.destiny_clan_id)
        result = await self.api.get(route=route)

        # check if clan exists
        if not result:
            raise CustomException("NoClan")

        return DestinyClanModel(id=link.destiny_clan_id, name=result.content["detail"]["name"])

    async def search_clan_for_member(
        self, member_name: str, clan_id: Optional[int] = None, use_cache: bool = True
    ) -> list[DestinyClanMemberModel]:
        """Search the clan for members with that name"""

        if not clan_id:
            clan = await self.get_clan()
            clan_id = clan.id

        route = clan_members_route.format(clan_id=clan_id)
        params = {"nameSearch": member_name}

        results = (await self.api.get(route=route, params=params, use_cache=use_cache)).content["results"]

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
                    last_online_status_change=localize_datetime(
                        datetime.datetime.fromtimestamp(int(result["lastOnlineStatusChange"]))
                    ),
                    join_date=get_datetime_from_bungie_entry(result["joinDate"]),
                    discord_id=discord_data.discord_id if discord_data else None,
                )
            )

        return members

    async def get_clan_members(
        self, clan_id: Optional[int] = None, use_cache: bool = True
    ) -> list[DestinyClanMemberModel]:
        """Get all clan members from a clan"""

        # searching for an empty string results in the same. Just less duplicated code this way
        return await self.search_clan_for_member(member_name="", clan_id=clan_id, use_cache=use_cache)

    async def is_clan_admin(self, clan_id: Optional[int] = None) -> bool:
        """Returns whether the user is an admin in the clan"""

        if not clan_id:
            clan = await self.get_clan()
            clan_id = clan.id

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

        clan = await self.get_clan()

        # check if inviter actually is admin
        if not await self.is_clan_admin(clan_id=clan.id):
            raise CustomException("ClanNoPermissions")

        route = clan_invite_route.format(clan_id=clan.id, system=to_invite_system, destiny_id=to_invite_destiny_id)

        welcome_message = {"message": f"Welcome to {clan.name}"}

        # todo error out if already in clan. that should return a nice error by the api
        await self.api.post(route=route, json=welcome_message)

    async def remove_from_clan(
        self,
        to_remove_destiny_id: int,
        to_remove_system: int,
    ):
        """Remove the User from the clan if they are in it"""

        clan = await self.get_clan()

        # check if remover actually is admin
        if not await self.is_clan_admin(clan_id=clan.id):
            raise CustomException("ClanNoPermissions")

        route = clan_kick_route.format(clan_id=clan.id, system=to_remove_system, destiny_id=to_remove_destiny_id)

        await self.api.post(route=route)
