import dataclasses
import datetime
from typing import Optional

from bungio.models import GroupApplicationRequest
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.core.errors import CustomException
from Backend.crud import destiny_clan_links, discord_users
from Backend.database.models import DiscordUsers
from Backend.networking.bungieApi import bungie_client
from Shared.functions.helperFunctions import localize_datetime
from Shared.networkingSchemas.destiny.clan import DestinyClanMemberModel, DestinyClanModel


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

    async def get_clan(self) -> DestinyClanModel:
        """Gets clan information"""

        # get data from db
        link = await destiny_clan_links.get_link(db=self.db, discord_guild_id=self.guild_id)

        result = await bungie_client.api.get_group(group_id=link.destiny_clan_id)

        # check if clan exists
        if not result:
            raise CustomException("NoClan")

        return DestinyClanModel(id=link.destiny_clan_id, name=result.detail.name)

    async def search_clan_for_member(
        self, member_name: str, clan_id: Optional[int] = None
    ) -> list[DestinyClanMemberModel]:
        """Search the clan for members with that name"""

        if not clan_id:
            clan = await self.get_clan()
            clan_id = clan.id

        result = await bungie_client.api.get_members_of_group(currentpage=1, group_id=clan_id, name_search=member_name)
        members = []
        for member in result.results:
            destiny_id = member.destiny_user_info.membership_id

            # get discord data
            try:
                discord_data = await discord_users.get_profile_from_destiny_id(db=self.db, destiny_id=destiny_id)
            except CustomException:
                discord_data = None

            members.append(
                DestinyClanMemberModel(
                    system=member.destiny_user_info.membership_type.value,
                    destiny_id=destiny_id,
                    name=member.destiny_user_info.full_bungie_name,
                    is_online=member.is_online,
                    last_online_status_change=localize_datetime(
                        datetime.datetime.fromtimestamp(member.last_online_status_change)
                    ),
                    join_date=member.join_date,
                    discord_id=discord_data.discord_id if discord_data else None,
                )
            )

        return members

    async def get_clan_members(
        self, clan_id: Optional[int] = None, use_cache: bool = True
    ) -> list[DestinyClanMemberModel]:
        """Get all clan members from a clan"""

        # searching for an empty string results in the same. Just less duplicated code this way
        return await self.search_clan_for_member(member_name="", clan_id=clan_id)

    async def is_clan_admin(self, clan_id: Optional[int] = None) -> bool:
        """Returns whether the user is an admin in the clan"""

        if not clan_id:
            clan = await self.get_clan()
            clan_id = clan.id

        results = await bungie_client.api.get_admins_and_founder_of_group(currentpage=1, group_id=clan_id)

        # look if destiny_id is in there
        for result in results.results:
            if result.destiny_user_info.membership_id == self.destiny_id:
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

        await bungie_client.api.individual_group_invite(
            group_id=clan.id,
            membership_id=to_invite_destiny_id,
            membership_type=to_invite_system,
            data=GroupApplicationRequest(message=f"ElevatorBot welcomes you to {clan.name}"),
            auth=self.user.auth,
        )

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

        await bungie_client.api.kick_member(
            group_id=clan.id,
            membership_id=to_remove_destiny_id,
            membership_type=to_remove_system,
            auth=self.user.auth,
        )
