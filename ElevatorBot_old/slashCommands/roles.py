import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash import SlashContext
from discord_slash.utils.manage_commands import create_option

from ElevatorBot.backendNetworking.destinyPlayer import DestinyPlayer
from ElevatorBot.backendNetworking.formating import embed_message
from ElevatorBot.backendNetworking.roleLookup import get_player_roles
from ElevatorBot.backendNetworking.roleLookup import has_role
from ElevatorBot.backendNetworking.slashCommandFunctions import get_user_obj
from ElevatorBot.backendNetworking.slashCommandFunctions import get_user_obj_admin
from ElevatorBot.static.dict import requirementHashes
from ElevatorBot.static.globals import dev_role_id
from ElevatorBot.static.slashCommandOptions import options_user


class RoleCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    # @cog_ext.cog_subcommand(
    #     base="roles",
    #     base_description="Various commands concerning Destiny 2 achievement discord roles",
    #     name="overview",
    #     description="Shows you what roles you can still achieve in this clan",
    #     options=[options_user()],
    # )
    # async def _roles_overview(self, ctx: SlashContext, **kwargs):
    # user = await get_user_obj(ctx, kwargs)
    #
    # # might take a sec
    # await ctx.defer()
    #
    # # get the users roles
    # active_roles, deprecated_roles = self.missingRoles(user)
    #
    # # do the missing roles display
    # embed = embed_message(f"{user.display_name}'s missing Roles")
    # embed.add_field(name="⁣", value=f"__**Achievable Roles:**__", inline=False)
    #
    # # only do this if there are roles to get
    # if active_roles:
    #     for topic in active_roles:
    #         embed.add_field(
    #             name=topic,
    #             value=("\n".join(active_roles[topic]) or "None"),
    #             inline=True,
    #         )
    # else:
    #     embed.add_field(
    #         name="Wow, you got every single role that is currently achievable. Congrats!",
    #         value="⁣",
    #         inline=False,
    #     )
    #
    # # Do the same for the deprecated roles
    # if deprecated_roles:
    #     embed.add_field(name="⁣", value=f"__**Deprecated Roles:**__", inline=False)
    #     for topic in deprecated_roles:
    #         embed.add_field(
    #             name=topic,
    #             value=("\n".join(deprecated_roles[topic]) or "None"),
    #             inline=True,
    #         )
    #
    # await ctx.send(embed=embed)

    # @cog_ext.cog_subcommand(
    #     base="roles",
    #     base_description="Various commands concerning Destiny 2 achievement discord roles",
    #     name="get",
    #     description="Assigns you all the roles you've earned",
    #     options=[options_user(flavor_text="Requires elevated permissions")],
    # )
    # async def _roles_get(self, ctx: SlashContext, **kwargs):
    # # check perm for mention, otherwise abort
    # user = await get_user_obj_admin(ctx, kwargs)
    # if not user:
    #     return
    #
    # # get destiny user info
    # destiny_player = await DestinyPlayer.from_discord_id(user.id, ctx=ctx)
    # if not destiny_player:
    #     return
    #
    # # might take a sec
    # await ctx.defer()
    #
    # # _update user DB
    # await destiny_player.update_activity_db()
    #
    # # get new roles
    # roles_at_start = [role.name for role in user.roles]
    # (
    #     roles_to_add,
    #     roles_to_remove,
    #     all_roles_earned,
    #     all_roles_not_earned,
    # ) = await get_player_roles(user, destiny_player, roles_at_start)
    #
    # # if user has no roles show
    # if not all_roles_earned:
    #     await ctx.send(
    #         embed=embed_message(
    #             "Info",
    #             f"You don't seem to have any roles.\nIf you believe this is an Error, refer to one of the <@&{dev_role_id}>\nOtherwise check <#686568386590802000> to see what you could acquire",
    #         )
    #     )
    #     return
    #
    # # assign roles
    # await user.add_roles(*roles_to_add, reason="Achievement Role Update")
    #
    # # _delete roles
    # await user.remove_roles(*roles_to_remove, reason="Achievement Role Update")
    #
    # # compare them with old roles for a better result msg
    # old_roles = {}
    # new_roles = {}
    # for topic, topicroles in requirementHashes.items():
    #     topic = topic.replace("Y1", "Year One")
    #     topic = topic.replace("Y2", "Year Two")
    #     topic = topic.replace("Y3", "Year Three")
    #     topic = topic.replace("Y4", "Year Four")
    #
    #     topic = topic.replace("Addition", "Miscellaneous")
    #
    #     for role_name in topicroles.keys():
    #         discord_role = discord.utils.get(ctx.guild.roles, name=role_name)
    #         if discord_role:
    #             if discord_role in roles_to_add:
    #                 try:
    #                     new_roles[topic].append(discord_role.mention)
    #                 except KeyError:
    #                     new_roles[topic] = [discord_role.mention]
    #             else:
    #                 if discord_role in all_roles_earned:
    #                     try:
    #                         old_roles[topic].append(discord_role.mention)
    #                     except KeyError:
    #                         old_roles[topic] = [discord_role.mention]
    #
    # # construct reply msg
    # embed = embed_message(f"{user.display_name}'s new Roles", f"__Previous Roles:__")
    # if not old_roles:
    #     embed.add_field(name=f"You didn't have any roles before", value="⁣", inline=True)
    #
    # for topic in old_roles:
    #     roles = []
    #     for role_name in topic:
    #         roles.append(role_name)
    #     embed.add_field(name=topic, value="\n".join(old_roles[topic]), inline=True)
    #
    # embed.add_field(name="⁣", value=f"__New Roles:__", inline=False)
    # if not new_roles:
    #     embed.add_field(name="No new roles have been achieved", value="⁣", inline=True)
    #
    # for topic in new_roles:
    #     roles = []
    #     for role_name in topic:
    #         roles.append(role_name)
    #     embed.add_field(name=topic, value="\n".join(new_roles[topic]), inline=True)
    #
    # await ctx.send(embed=embed)

    # @cog_ext.cog_subcommand(
    #     base="roles",
    #     base_description="Various commands concerning Destiny 2 achievement discord roles",
    #     name="requirements",
    #     description="Shows you what you need to do to get the specified role",
    #     options=[
    #         create_option(
    #             name="role",
    #             description="The name of the role you want to look up",
    #             option_type=8,
    #             required=True,
    #         ),
    #         options_user(),
    #     ],
    # )
    # async def _roles_requirements(self, ctx: SlashContext, **kwargs):
    # user = await get_user_obj(ctx, kwargs)
    # role = kwargs["role"]
    #
    # # might take a sec
    # await ctx.defer()
    #
    # # Get user details
    # destiny_player = await DestinyPlayer.from_discord_id(user.id, ctx=ctx)
    # if not destiny_player:
    #     return
    #
    # # _update user DB
    # await destiny_player.update_activity_db()
    # reqs = await has_role(destiny_player, role, return_as_bool=False)
    #
    # if not reqs:
    #     await ctx.send(
    #         hidden=True,
    #         embed=embed_message(
    #             f"Error",
    #             f"This role can't be achieved through Destiny 2 \nPlease try again with a different role",
    #         ),
    #     )
    #
    # else:
    #     # construct reply msg
    #     embed = embed_message(f"{user.display_name}'s '{role.name}' Eligibility")
    #
    #     for req in reqs[1]:
    #         embed.add_field(name=req, value=reqs[1][req], inline=True)
    #
    #     await ctx.send(embed=embed)

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

        # _delete the roles from dict(roles) that are already earned
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

        # _delete those roles, where a superior role exists
        for category, x in requirementHashes.items():
            for role, roledata in x.items():
                if "replaced_by" in roledata.keys():
                    for superior in roledata["replaced_by"]:
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

        # _delete the empty categories
        for role, roledata in roles.copy().items():
            if not roledata:
                roles.pop(role)
        for role, roledata in deprecated_roles.copy().items():
            if not roledata:
                deprecated_roles.pop(role)

        return roles, deprecated_roles


def setup(client):
    client.add_cog(RoleCommands(client))
