import discord
from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option

from ElevatorBot.commandHelpers.permissionTemplates import permissions_admin
from ElevatorBot.core.destiny.account import DestinyAccount
from ElevatorBot.core.destiny.clan import DestinyClan
from ElevatorBot.core.destiny.profile import DestinyProfile
from ElevatorBot.misc.formating import embed_message


class UserInfo(Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="userinfo",
        description="Gets collected info for the specified user",
        options=[
            create_option(
                name="discord_user",
                description="Look up a discord user",
                option_type=6,
                required=False,
            ),
            create_option(
                name="destiny_id",
                description="Look up a destinyID",
                option_type=3,
                required=False,
            ),
            create_option(
                name="fuzzy_name",
                description="If you know how the user is called",
                option_type=3,
                required=False,
            ),
        ],
        default_permission=False,
        permissions=permissions_admin,
    )
    async def _user_info(
        self,
        ctx: SlashContext,
        discord_user: discord.Member = None,
        destiny_id: str = None,
        fuzzy_name: str = None,
    ):
        """Gets collected info for the specified user"""

        # make sure exactly one arg was chosen
        if (
            (not (discord_user or destiny_id or fuzzy_name))
            or (discord_user and destiny_id)
            or (discord_user and fuzzy_name)
            or (destiny_id and fuzzy_name)
            or (destiny_id and discord_user and fuzzy_name)
        ):
            await ctx.send(
                hidden=True,
                embed=embed_message("Error", "Exactly one of the arguments must be used"),
            )
            return
        await ctx.defer()
        destiny_profile = DestinyProfile(client=ctx.bot, discord_member=discord_user, discord_guild=ctx.guild)

        title = f"Available Info"
        profiles = []

        # if destiny info is given
        if destiny_id:
            try:
                destiny_id = int(destiny_id)
            except ValueError:
                await ctx.send(
                    hidden=True,
                    embed=embed_message("Error", "The argument `destiny_id` must be a number"),
                )
                return

            profile = await destiny_profile.from_destiny_id(destiny_id=destiny_id)
            if not profile:
                await profile.send_error_message(ctx)
                return

            profiles.append(profile)

        # if discord info is given
        elif discord_user:
            profile = await destiny_profile.from_discord_member()
            if not profile:
                await profile.send_error_message(ctx)
                return

            profiles.append(profile)

        # if fuzzy name is given
        else:
            # todo get clan id from discord guild
            clan = DestinyClan(client=ctx.bot, discord_member=discord_user, discord_guild=ctx.guild)
            clan_members = await clan.search_for_clan_members(search_phrase=fuzzy_name)

            # handle errors
            if not clan_members:
                await clan_members.send_error_message(ctx)
                return

            # did we find sb?
            if not clan_members.result["members"]:
                await ctx.send(embed=embed_message("Error", "No matches found for `{fuzzy_name}`"))
                return

            # loop through the results
            for potential_match in clan_members.result["members"]:
                profile = await destiny_profile.from_destiny_id(destiny_id=potential_match.destiny_id)

                # handle errors
                if not profile:
                    await profile.send_error_message(ctx)
                    return

                profiles.append(profile)

        # make return embed
        embed = embed_message(
            title,
            "Could not find a clear result, here are the matches" if len(profiles) > 1 else None,
        )

        # fill that
        i = 0
        for profile in profiles:
            i += 1

            account = DestinyAccount(
                client=ctx.bot,
                discord_member=profile.discord_member,
                discord_guild=ctx.guild,
            )
            destiny_name = await account.get_destiny_name()

            # error out if need be
            if not destiny_name:
                await destiny_name.send_error_message(ctx)
                return

            embed.add_field(
                name=f"Option {i}",
                value=f"Discord - {profile.discord_member.mention} \nDestinyID: `{profile.destiny_id}` \nSystem - `{profile.system}` \nDestiny Name - `{destiny_name.result['name']}`",
                inline=False,
            )

        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(UserInfo(client))
