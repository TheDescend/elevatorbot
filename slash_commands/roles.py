from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option

from functions.dataLoading import updateDB
from functions.formating import embed_message
from functions.roleLookup import get_player_roles, assignRolesToUser, removeRolesFromUser, has_role
from functions.slashCommandFunctions import get_user_obj, get_user_obj_admin, get_destinyID_and_system
from static.config import GUILD_IDS
from static.dict import requirementHashes
from static.globals import dev_role_id
from static.slashCommandOptions import options_user


class RoleCommands(commands.Cog):
    def __init__(self, client):
        self.client = client


    @cog_ext.cog_subcommand(
        base="roles",
        base_description="Various commands concerning Destiny 2 achievement discord roles",
        name="overview",
        description="Shows you what roles you can still achieve in this clan",
        options=[
            options_user()
        ]
    )
    async def _roles_overview(self, ctx: SlashContext, **kwargs):
        user = await get_user_obj(ctx, kwargs)

        # might take a sec
        await ctx.defer()

        # get the users roles
        active_roles, deprecated_roles = self.missingRoles(user)

        # do the missing roles display
        embed = embed_message(
            f"{user.display_name}'s missing Roles"
        )
        embed.add_field(name="⁣", value=f"__**Achievable Roles:**__", inline=False)

        # only do this if there are roles to get
        if active_roles:
            for topic in active_roles:
                embed.add_field(name=topic, value=("\n".join(active_roles[topic]) or "None"), inline=True)
        else:
            embed.add_field(name="Wow, you got every single role that is currently achievable. Congrats!", value="⁣", inline=False)

        # Do the same for the deprecated roles
        if deprecated_roles:
            embed.add_field(name="⁣", value=f"__**Deprecated Roles:**__", inline=False)
            for topic in deprecated_roles:
                embed.add_field(name=topic, value=("\n".join(deprecated_roles[topic]) or "None"), inline=True)

        await ctx.send(embed=embed)


    @cog_ext.cog_subcommand(
        base="roles",
        base_description="Various commands concerning Destiny 2 achievement discord roles",
        name="get",
        description="Assigns you all the roles you've earned",
        options=[
            options_user(flavor_text="Requires elevated permissions")
        ]
    )
    async def _roles_get(self, ctx: SlashContext, **kwargs):
        # check perm for mention, otherwise abort
        user = await get_user_obj_admin(ctx, kwargs)
        if not user:
            return

        # get destiny user info
        _, destinyID, system = await get_destinyID_and_system(ctx, user)
        if not destinyID:
            return

        # might take a sec
        await ctx.defer()

        # update user DB
        await updateDB(destinyID)

        # get new roles
        roles_at_start = [role.name for role in user.roles]
        (roleList, removeRoles) = await get_player_roles(ctx.guild, destinyID, roles_at_start)

        # assign roles
        await ctx.author.add_roles(*roleList, reason="Achievement Role Update")

        # remove roles
        await ctx.author.remove_roles(*removeRoles, reason="Achievement Role Update")

        # refreshing user obj to display the new roles
        updated_roles_member = await user.guild.fetch_member(user.id)

        # compare them with old roles for a better result msg
        old_roles = {}
        roles_now = [role.name for role in updated_roles_member.roles]
        new_roles = {}
        for topic, topicroles in requirementHashes.items():
            topic = topic.replace("Y1", "Year One")
            topic = topic.replace("Y2", "Year Two")
            topic = topic.replace("Y3", "Year Three")
            topic = topic.replace("Y4", "Year Four")

            topic = topic.replace("Addition", "Miscellaneous")

            for role in topicroles.keys():
                if role in roles_at_start:
                    try:
                        old_roles[topic].append(role)
                    except KeyError:
                        old_roles[topic] = [role]
                elif (role not in roles_at_start) and (role in roles_now):
                    try:
                        new_roles[topic].append(role)
                    except KeyError:
                        new_roles[topic] = [role]

        # if user has no roles show
        if not roleList:
            await ctx.send(embed=embed_message(
                'Info',
                f'You don\'t seem to have any roles.\nIf you believe this is an Error, refer to one of the <@&{dev_role_id}>\nOtherwise check <#686568386590802000> to see what you could acquire'
            ))
            return

        # construct reply msg
        embed = embed_message(
            f"{user.display_name}'s new Roles",
            f'__Previous Roles:__'
        )
        if not old_roles:
            embed.add_field(name=f"You didn't have any roles before", value="⁣", inline=True)

        for topic in old_roles:
            roles = []
            for role in topic:
                roles.append(role)
            embed.add_field(name=topic, value="\n".join(old_roles[topic]), inline=True)

        embed.add_field(name="⁣", value=f"__New Roles:__", inline=False)
        if not new_roles:
            embed.add_field(name="No new roles have been achieved", value="⁣", inline=True)

        for topic in new_roles:
            roles = []
            for role in topic:
                roles.append(role)
            embed.add_field(name=topic, value="\n".join(new_roles[topic]), inline=True)

        await ctx.send(embed=embed)


    @cog_ext.cog_subcommand(
        base="roles",
        base_description="Various commands concerning Destiny 2 achievement discord roles",
        name="requirements",
        description="Shows you what you need to do to get the specified role",
        options=[
            create_option(
                name="role",
                description="The name of the role you want to look up",
                option_type=8,
                required=True
            ),
            options_user()
        ]
    )
    async def _roles_requirements(self, ctx: SlashContext, **kwargs):
        user = await get_user_obj(ctx, kwargs)
        role = kwargs["role"]

        # might take a sec
        await ctx.defer()

        # Get user details
        _, destinyID, system = await get_destinyID_and_system(ctx, user)

        # update user DB
        await updateDB(destinyID)
        reqs = await has_role(destinyID, role, return_as_bool=False)

        if not reqs:
            await ctx.send(hidden=True, embed=embed_message(
                f"Error",
                f"This role can't be achieved through Destiny 2 \nPlease try again with a different role"
            ))

        else:
            # construct reply msg
            embed = embed_message(
                f"{user.display_name}'s '{role.name}' Eligibility"
            )

            for req in reqs[1]:
                embed.add_field(name=req, value=reqs[1][req], inline=True)

            await ctx.send(embed=embed)


    def missingRoles(self, user):
        roles = {}
        deprecated_roles = {}

        # get list of roles available
        for category, x in requirementHashes.items():
            for role, req in x.items():
                # depending on if its deprecated or not, add to respective dict
                if "deprecated" not in req:
                    try:
                        roles[category].append(role)
                    except KeyError:
                        roles[category] = [role]
                else:
                    try:
                        deprecated_roles[category].append(role)
                    except KeyError:
                        deprecated_roles[category] = [role]

        # remove the roles from dict(roles) that are already earned
        user_roles = [role.name for role in user.roles]
        for role in user_roles:
            for category in roles:
                try:
                    roles[category].remove(role)
                    break
                except ValueError:
                    pass
            for category in deprecated_roles:
                try:
                    deprecated_roles[category].remove(role)
                    break
                except ValueError:
                    pass

        # remove those roles, where a superior role exists
        for category, x in requirementHashes.items():
            for role, roledata in x.items():
                if 'replaced_by' in roledata.keys():
                    for superior in roledata['replaced_by']:
                        if superior in user_roles:
                            for category in roles:
                                try:
                                    roles[category].remove(role)
                                    break
                                except ValueError:
                                    pass
                            for category in deprecated_roles:
                                try:
                                    deprecated_roles[category].remove(role)
                                    break
                                except ValueError:
                                    pass

        # remove the empty categories
        for role, roledata in roles.copy().items():
            if not roledata:
                roles.pop(role)
        for role, roledata in deprecated_roles.copy().items():
            if not roledata:
                deprecated_roles.pop(role)

        return roles, deprecated_roles






def setup(client):
    client.add_cog(RoleCommands(client))


