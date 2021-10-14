import dataclasses

from dis_snek.client import Snake
from dis_snek.models.context import InteractionContext
from dis_snek.models.discord_objects.guild import Guild
from dis_snek.models.discord_objects.user import Member

from ElevatorBot.backendNetworking.destiny.roles import DestinyRoles


@dataclasses.dataclass()
class Roles:
    """Class to update achievement Roles"""

    client: Snake
    guild: Guild
    member: Member

    def __post_init__(self):
        self.roles = DestinyRoles(client=self.client, discord_guild=self.guild, discord_member=self.member)

    async def update(self, ctx: InteractionContext = None):
        """Get and update a members roles"""

        result = await self.roles.get()

        if not result:
            if ctx:
                await result.send_error_message(ctx=ctx)

        else:
            earned_roles = result.result["earned"]
            earned_but_replaced_by_higher_role_roles = result.result["earned_but_replaced_by_higher_role"]
            not_earned_roles = result.result["not_earned"]

            # assign new roles
            for role_id in earned_roles:
                await self.member.add_role(role=role_id)

            # remove old roles
            for role_id in earned_but_replaced_by_higher_role_roles:
                await self.member.remove_role(role=role_id)
            for role_id in not_earned_roles:
                await self.member.remove_role(role=role_id)
