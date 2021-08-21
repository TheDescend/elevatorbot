import discord
from discord.ext.commands import Cog
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option

from ElevatorBot.commandHelpers.permissionTemplates import permissions_admin
from ElevatorBot.commandHelpers.responseTemplates import respond_destiny_id_unknown
from ElevatorBot.core.destiny.noOauthNeeded import DestinyNoOauthNeeded
from ElevatorBot.core.destiny.profile import DestinyProfile
from ElevatorBot.misc.formating import embed_message


class UserInfo(Cog):
    def __init__(
        self,
        client
    ):
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
            embed=embed_message(
                "Error",
                "Exactly one of the arguments must be used"
            ),
        )
        return
    await ctx.defer()

    profiles = []

    # if destiny info is given
    if destiny_id:
        try:
            destiny_id = int(destiny_id)
        except ValueError:
            await ctx.send(
                hidden=True,
                embed=embed_message(
                    "Error",
                    "The argument `destiny_id` must be a number")
            )
            return

        profile = await DestinyProfile.from_destiny_id(
            client=ctx.bot,
            discord_guild=ctx.guild,
            destiny_id=destiny_id
        )
        if not profile:
            await profile.send_error_message(ctx)
            return

        profiles.append(profile)

    # if discord info is given
    elif discord_user:
        profile = await DestinyProfile.from_discord_member(
            client=ctx.bot,
            discord_guild=ctx.guild,
            discord_member=discord_user
        )
        if not profile:
            await profile.send_error_message(ctx)
            return

        profiles.append(profile)

    # if fuzzy name is given
    else:
        # todo append that info to profiles
        clansearch = []
        returnjson = await get_json_from_url(
            f"https://www.bungie.net/Platform/GroupV2/{CLANID}/Members?nameSearch={fuzzy_name}"
        )
        clansearch.append(returnjson)

        for result in clansearch:
            resp = result.content["Response"]
            if not resp["results"]:
                await ctx.send(
                    embed=embed_message(
                        f"Error", f"No matches found for `{fuzzy_name}`"
                    )
                )
                return

            i = 0
            for guy in resp["results"]:
                i += 1
                steam_name = guy["destinyUserInfo"]["LastSeenDisplayName"]
                bungie_name = guy["bungieNetUserInfo"]["displayName"]
                destinyID = int(guy["destinyUserInfo"]["membershipId"])
                discordID = await lookupDiscordID(destinyID)

    # make return embed
    title = f"Available Info"
    embed = embed_message(
        title,
        "Could not find a clear result, here are the matches" if len(profiles) > 1 else None
    )

    # fill that
    i = 0
    for profile in profiles:
        i += 1

        destiny_name = await DestinyNoOauthNeeded(
            client=ctx.bot,
            destiny_id=profile.destiny_id,
            system=profile.system
        ).get_destiny_name()

        embed.add_field(
            name=f"Option {i}",
            value=f"Discord - {profile.discord_member.mention} \nDestinyID: `{profile.destiny_id}` \nSystem - `{profile.system}` \nDestiny Name - `{destiny_name}`",
            inline=False,
        )

    await ctx.send(embed=embed)


def setup(
    client
):
    client.add_cog(UserInfo(client))
