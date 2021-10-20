import dataclasses

from dis_snek.client import Snake
from dis_snek.models import Role
from dis_snek.models.context import InteractionContext
from dis_snek.models.discord_objects.guild import Guild
from dis_snek.models.discord_objects.user import Member

from ElevatorBot.backendNetworking.destiny.roles import DestinyRoles
from ElevatorBot.misc.formating import embed_message


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
            roles_at_start = [role.id for role in ctx.author.roles]

            earned_roles: dict[str, list[int]] = result.result["earned"]
            earned_but_replaced_by_higher_role_roles: dict[str, list[int]] = result.result[
                "earned_but_replaced_by_higher_role"
            ]
            not_earned_roles: dict[str, list[int]] = result.result["not_earned"]

            # assign new roles
            for category in earned_roles.values():
                for role_id in category:
                    await self.member.add_role(role=role_id)

            # remove old roles
            for category in earned_but_replaced_by_higher_role_roles.values():
                for role_id in category:
                    await self.member.remove_role(role=role_id)
            for category in not_earned_roles.values():
                for role_id in category:
                    await self.member.remove_role(role=role_id)

            # send a message
            if ctx:
                # if user has no roles show this
                if not earned_roles:
                    await ctx.send(
                        # todo link to where you can see all the roles
                        embeds=embed_message(
                            "Info",
                            f"You don't have any roles. \nUse `/roles overview` to see all available roles and then `/roles requirements <role>` to view its requirements.",
                        )
                    )
                    return

                # combine earned_roles and earned_but_replaced_by_higher_role_roles
                all_earned_roles = earned_roles.copy()
                for category, role_ids in earned_but_replaced_by_higher_role_roles.items():
                    for role_id in role_ids:
                        if category not in all_earned_roles:
                            all_earned_roles.update({category: []})
                        all_earned_roles[category].append(role_id)

                # now separate into newly earned roles and the old ones
                old_roles = {}
                new_roles = {}
                for category, role_ids in all_earned_roles.items():
                    for role_id in role_ids:
                        discord_role = await self.guild.get_role(role_id)

                        if discord_role:
                            # check if they had the role
                            if discord_role.id in roles_at_start:
                                if category not in old_roles:
                                    old_roles.update({category: []})
                                old_roles[category].append(discord_role.mention)

                            else:
                                if category not in new_roles:
                                    new_roles.update({category: []})
                                new_roles[category].append(discord_role.mention)

                # construct reply msg
                embed = embed_message(f"{ctx.author.display_name}'s new Roles", f"__Previous Roles:__")
                if not old_roles:
                    embed.add_field(name=f"You didn't have any roles before", value="⁣", inline=True)

                for topic in old_roles:
                    roles = []
                    for role_name in topic:
                        roles.append(role_name)
                    embed.add_field(name=topic, value="\n".join(old_roles[topic]), inline=True)

                embed.add_field(name="⁣", value=f"__New Roles:__", inline=False)
                if not new_roles:
                    embed.add_field(name="No new roles have been achieved", value="⁣", inline=True)

                for topic in new_roles:
                    roles = []
                    for role_name in topic:
                        roles.append(role_name)
                    embed.add_field(name=topic, value="\n".join(new_roles[topic]), inline=True)

                await ctx.send(embeds=embed)
