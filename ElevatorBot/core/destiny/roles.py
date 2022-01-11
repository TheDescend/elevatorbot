import dataclasses
from typing import Optional

from dis_snek.models import Role
from dis_snek.models.context import InteractionContext
from dis_snek.models.discord_objects.guild import Guild
from dis_snek.models.discord_objects.user import Member

from ElevatorBot.backendNetworking.destiny.roles import DestinyRoles
from ElevatorBot.commandHelpers.autocomplete import activities_by_id
from ElevatorBot.misc.cache import collectible_cache, triumph_cache
from ElevatorBot.misc.discordShortcutFunctions import (
    assign_roles_to_member,
    remove_roles_from_member,
)
from ElevatorBot.misc.formating import embed_message
from Shared.NetworkingSchemas.destiny.roles import RolesCategoryModel


@dataclasses.dataclass()
class Roles:
    """Class to handle achievement Roles"""

    guild: Guild
    member: Member
    ctx: Optional[InteractionContext] = None

    def __post_init__(self):
        self.roles = DestinyRoles(ctx=self.ctx, discord_guild=self.guild, discord_member=self.member)

    async def get_requirements(self, role: Role):
        """Get a roles get_requirements and what user has done"""

        # get info what get_requirements the user fulfills and which not and info on the role
        result = await self.roles.get_detail(role)

        role_data = result.role.role_data
        user_data = result.user_role_data

        # construct reply msg
        embed = embed_message(
            f"{self.member.display_name}'s '{role.name}' Eligibility", f"**Status: {result.earned.value}**"
        )

        # loop through the requirements and their statuses
        activities: list[str] = []
        for activity_info, user_activity in zip(
            role_data.require_activity_completions, user_data.require_activity_completions
        ):
            activities.append(f"{activities_by_id[activity_info.allowed_activity_hashes[0]].name}: {user_activity}")

        collectibles: list[str] = []
        for collectible_id, user_collectible in zip(role_data.require_collectibles, user_data.require_collectibles):
            collectibles.append(
                f"[{await collectible_cache.get_name(collectible_id=collectible_id)}](https://www.light.gg/db/items/{collectible_id}): {user_collectible}"
            )

        records: list[str] = []
        for triumph_id, user_triumph in zip(role_data.require_collectibles, user_data.require_collectibles):
            records.append(
                f"[{await triumph_cache.get_name(triumph_id=triumph_id)}](https://www.light.gg/db/legend/triumphs/{triumph_id}): {user_triumph}"
            )

        roles: list[str] = []
        for role_id, user_role in zip(role_data.require_collectibles, user_data.require_collectibles):
            roles.append(f"{(await self.guild.get_role(role_id.id)).mention}: {user_role}")

        # add the embed fields
        if activities:
            embed.add_field(name="Required Activity Completions", value="\n".join(activities), inline=False)
        if collectibles:
            embed.add_field(name="Required Collectibles", value="\n".join(collectibles), inline=False)
        if records:
            embed.add_field(name="Required Triumphs", value="\n".join(records), inline=False)
        if roles:
            embed.add_field(name="Required Roles", value="\n".join(roles), inline=False)

        await self.ctx.send(embeds=embed)

    async def get_missing(self):
        """Get a members missing roles"""

        result = await self.roles.get_missing()

        # do the missing roles display
        embed = embed_message(f"{self.member.display_name}'s Roles")

        # only do this if there are roles to get
        if result.acquirable:
            embed.add_field(name="⁣", value="__**Acquirable Roles:**__", inline=False)

            # sort by category
            by_category = await self.__sort_by_category(result.acquirable)

            for category, role_mentions in by_category.items():
                embed.add_field(
                    name=category,
                    value="\n".join(role_mentions),
                    inline=True,
                )
        else:
            embed.description = "Wow, you got every single role. Congrats!"

        # Do the same for the deprecated roles
        if result.deprecated:
            embed.add_field(name="⁣", value="__**Deprecated Roles:**__", inline=False)

            # sort by category
            by_category = await self.__sort_by_category(result.deprecated)

            for category, role_mentions in by_category.items():
                embed.add_field(
                    name=category,
                    value="\n".join(role_mentions),
                    inline=True,
                )

        await self.ctx.send(embeds=embed)

    async def update(self):
        """Get and update a members roles"""

        result = await self.roles.get()

        roles_at_start = [role.id for role in self.member.roles]

        # assign new roles
        await assign_roles_to_member(
            member=self.member,
            *[role_data.discord_role_id for role_data in result.earned],
            reason="Destiny 2 Role Update",
        )

        # remove old roles
        await remove_roles_from_member(
            member=self.member,
            *[role_data.discord_role_id for role_data in result.earned_but_replaced_by_higher_role],
            reason="Destiny 2 Role Update",
        )
        await remove_roles_from_member(
            member=self.member,
            *[role_data.discord_role_id for role_data in result.not_earned],
            reason="Destiny 2 Role Update",
        )

        # send a message
        if self.ctx:
            # if user has no roles show this
            if not result.earned:
                await self.ctx.send(
                    # todo link to where you can see all the roles
                    embeds=embed_message(
                        "Info",
                        "You don't have any roles. \nUse `/roles missing` to see available roles and then `/roles requirements <role>` to view its requirements.",
                    )
                )
                return

            all_earned_roles = result.earned + result.earned_but_replaced_by_higher_role

            # now separate into newly earned roles and the old ones
            old_roles = {}
            new_roles = {}
            for role_data in all_earned_roles:
                discord_role = await self.guild.get_role(role_data.discord_role_id)
                category = role_data.category

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
            embed = embed_message(f"{self.member.display_name}'s New Roles", "__Previous Roles:__")
            if not old_roles:
                embed.add_field(name="You didn't have any roles before", value="⁣", inline=True)

            for topic in old_roles:
                roles = []
                for role_name in topic:
                    roles.append(role_name)
                embed.add_field(name=topic, value="\n".join(old_roles[topic]), inline=True)

            embed.add_field(name="⁣", value="__New Roles:__", inline=False)
            if not new_roles:
                embed.add_field(name="No new roles have been achieved", value="⁣", inline=True)

            for topic in new_roles:
                roles = []
                for role_name in topic:
                    roles.append(role_name)
                embed.add_field(name=topic, value="\n".join(new_roles[topic]), inline=True)

            await self.ctx.send(embeds=embed)

    async def __sort_by_category(self, items: list[RolesCategoryModel]) -> dict[str, list[str]]:
        """Sort list[RolesCategoryModel] by category"""

        by_category: dict[str, list[str]] = {}
        for role_data in items:
            if role_data.category not in by_category:
                by_category.update({role_data.category: []})
            by_category[role_data.category].append((await self.guild.get_role(role_data.discord_role_id)).mention)

        return by_category
