import dataclasses
from typing import Optional
from urllib.parse import urljoin

from naff import Button, ButtonStyles, Guild, Member, Role

from ElevatorBot.commandHelpers import autocomplete
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from ElevatorBot.misc.cache import collectible_cache, triumph_cache
from ElevatorBot.misc.discordShortcutFunctions import assign_roles_to_member, remove_roles_from_member
from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.networking.destiny.roles import DestinyRoles
from ElevatorBot.networking.errors import BackendException
from Shared.functions.readSettingsFile import get_setting
from Shared.networkingSchemas.destiny.roles import RolesCategoryModel


@dataclasses.dataclass()
class Roles:
    """Class to handle achievement Roles"""

    guild: Guild
    member: Member
    ctx: Optional[ElevatorInteractionContext] = None

    def __post_init__(self):
        self.roles = DestinyRoles(ctx=self.ctx, discord_guild=self.guild, discord_member=self.member)

        self.view_on_web = Button(
            style=ButtonStyles.URL,
            label="View Online",
            url=urljoin(get_setting("WEBSITE_URL"), f"/server/{self.guild.id}/roles"),
        )

    async def get_requirements(self, role: Role):
        """Get a roles get_requirements and what user has done"""

        # get info what get_requirements the user fulfills and which not and info on the role
        result = await self.roles.get_detail(role)

        role_data = result.role
        user_data = result.user_role_data

        # construct reply msg
        embed = embed_message(f"'{role.name}' Eligibility", f"**Status: {result.earned.value}**", member=self.member)

        # loop through the requirements and their statuses
        activities: list[str] = []
        for activity_info, user_activity in zip(
            role_data.require_activity_completions, user_data.require_activity_completions
        ):
            activities.append(
                f"{autocomplete.activities_by_id[activity_info.allowed_activity_hashes[0]].name}: {user_activity}"
            )

        collectibles: list[str] = []
        for collectible, user_collectible in zip(role_data.require_collectibles, user_data.require_collectibles):
            collectibles.append(
                f"[{await collectible_cache.get_name(collectible_id=collectible.bungie_id)}](https://www.light.gg/db/items/{collectible.bungie_id}): {user_collectible}"
            )

        records: list[str] = []
        for triumph, user_triumph in zip(role_data.require_records, user_data.require_records):
            records.append(
                f"[{await triumph_cache.get_name(triumph_id=triumph.bungie_id)}](https://www.light.gg/db/legend/triumphs/{triumph.bungie_id}): {user_triumph}"
            )

        roles: list[str] = []
        for role_id, user_role in zip(role_data.require_role_ids, user_data.require_role_ids):
            roles.append(f"{(await self.guild.fetch_role(role_id)).mention}: {user_role}")

        # add the embed fields
        if activities:
            embed.add_field(name="Required Activity Completions", value="\n".join(activities), inline=False)
        if collectibles:
            embed.add_field(name="Required Collectibles", value="\n".join(collectibles), inline=False)
        if records:
            embed.add_field(name="Required Triumphs", value="\n".join(records), inline=False)
        if roles:
            embed.add_field(name="Required Roles", value="\n".join(roles), inline=False)

        await self.ctx.send(embeds=embed, components=self._view_on_web_details(role))

    def _view_on_web_details(self, role: Role):
        """Get the component to view the specific role"""

        return Button(
            style=ButtonStyles.URL,
            label="View Online",
            url=urljoin(get_setting("WEBSITE_URL"), f"/server/{self.guild.id}/roles#{role.id}"),
        )

    async def get_missing(self):
        """Get a members missing roles"""

        result = await self.roles.get_missing()

        # do the missing roles display
        embed = embed_message("Roles", member=self.member)

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

        await self.ctx.send(embeds=embed, components=self.view_on_web)

    async def update(self):
        """Get and update a members roles"""

        try:
            result = await self.roles.get()
        except BackendException as error:
            # ignore people that are not registered
            if error.error == "DiscordIdNotFound":
                return
            raise error

        roles_at_start = [role.id for role in self.member.roles]

        # assign new roles
        await assign_roles_to_member(
            self.member,
            *[role_data.discord_role_id for role_data in result.earned],
            reason="Destiny 2 Role Update",
        )

        # remove old roles
        await remove_roles_from_member(
            self.member,
            *[role_data.discord_role_id for role_data in result.earned_but_replaced_by_higher_role],
            reason="Destiny 2 Role Update",
        )
        await remove_roles_from_member(
            self.member,
            *[role_data.discord_role_id for role_data in result.not_earned],
            reason="Destiny 2 Role Update",
        )

        # send a message
        if self.ctx:
            # if user has no roles show this
            if not result.earned:
                await self.ctx.send(
                    embeds=embed_message(
                        "Roles",
                        f"""You don't have any roles. \nUse {self.ctx.client.get_command_by_name("roles missing").mention()} to see available roles and then {self.ctx.client.get_command_by_name("roles requirements").mention()} to view its requirements""",
                        member=self.member,
                    ),
                    components=self.view_on_web,
                )
                return

            all_earned_roles = result.earned

            # now separate into newly earned roles and the old ones
            old_roles = {}
            new_roles = {}
            for role_data in all_earned_roles:
                discord_role = await self.guild.fetch_role(role_data.discord_role_id)
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
            embed = embed_message("Roles", "__Previous Roles:__", member=self.member)
            if not old_roles:
                embed.add_field(name="You didn't have any roles before", value="⁣", inline=True)

            for topic in old_roles:
                embed.add_field(name=topic, value="\n".join(old_roles[topic]), inline=True)

            embed.add_field(name="⁣", value="__New Roles:__", inline=False)
            if not new_roles:
                embed.add_field(name="No new roles have been achieved", value="⁣", inline=True)

            for topic in new_roles:
                embed.add_field(name=topic, value="\n".join(new_roles[topic]), inline=True)

            await self.ctx.send(embeds=embed)

    async def __sort_by_category(self, items: list[RolesCategoryModel]) -> dict[str, list[str]]:
        """Sort list[RolesCategoryModel] by category"""

        by_category: dict[str, list[str]] = {}
        for role_data in items:
            if role_data.category not in by_category:
                by_category.update({role_data.category: []})
            by_category[role_data.category].append((await self.guild.fetch_role(role_data.discord_role_id)).mention)

        return by_category
