from dis_snek.models import InteractionContext, Member, OptionTypes, slash_command, slash_option

from ElevatorBot.backendNetworking.destiny.account import DestinyAccount
from ElevatorBot.backendNetworking.destiny.clan import DestinyClan
from ElevatorBot.backendNetworking.destiny.profile import DestinyProfile
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formatting import embed_message


class UserInfo(BaseScale):
    """
    Gets collected info for the specified user. Exactly one option needs to be filled out
    """

    # todo perms
    @slash_command(name="user_info", description="Gets collected info for the specified user")
    @slash_option(name="discord_user", description="Look up a discord user", required=False, opt_type=OptionTypes.USER)
    @slash_option(name="destiny_id", description="Look up a destinyID", required=False, opt_type=OptionTypes.STRING)
    @slash_option(
        name="fuzzy_name", description="If you know how the user is called", required=False, opt_type=OptionTypes.STRING
    )
    async def user_info(
        self, ctx: InteractionContext, discord_user: Member = None, destiny_id: str = None, fuzzy_name: str = None
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
                ephemeral=True,
                embeds=embed_message("Error", "Exactly one of the arguments must be used"),
            )
            return

        destiny_profile = DestinyProfile(ctx=ctx, discord_member=discord_user, discord_guild=ctx.guild)

        if destiny_id:
            destiny_id = int(destiny_id)

        title = "Available Info"
        profiles = []

        # if destiny info is given
        if destiny_id:
            try:
                destiny_id = int(destiny_id)
            except ValueError:
                await ctx.send(
                    ephemeral=True,
                    embeds=embed_message("Error", "The argument `destiny_id` must be a number"),
                )
                return

            profile = await destiny_profile.from_destiny_id(destiny_id=destiny_id)
            profiles.append(profile)

        # if discord info is given
        elif discord_user:
            profile = await destiny_profile.from_discord_member()
            profiles.append(profile)

        # if fuzzy name is given
        else:
            clan = DestinyClan(ctx=ctx, discord_guild=ctx.guild)
            clan_members = await clan.search_for_clan_members(search_phrase=fuzzy_name)

            # did we find sb?
            if not clan_members.members:
                await ctx.send(embeds=embed_message("Error", f"No matches found for `{fuzzy_name}`"))
                return

            # loop through the results
            for potential_match in clan_members.members:
                profile = await destiny_profile.from_destiny_id(destiny_id=potential_match.destiny_id)

                profiles.append(profile)

        # make return embed
        embed = embed_message(
            title,
            "Could not find a clear result, here are the matches" if len(profiles) > 1 else None,
        )

        # fill that
        for i, profile in enumerate(profiles):
            discord_member = await ctx.guild.get_member(profile.discord_id)
            if not discord_member:
                await ctx.send(
                    embeds=embed_message(
                        "Error", f"The discord ID `{profile.discord_id}` is not in this discord server"
                    )
                )
                return

            account = DestinyAccount(
                ctx=ctx,
                discord_member=discord_member,
                discord_guild=ctx.guild,
            )
            destiny_name = await account.get_destiny_name()
            embed.add_field(
                name=f"Option {i + 1}",
                value=f"Discord - {discord_member.mention} \nDestinyID: `{profile.destiny_id}` \nSystem - `{profile.system}` \nDestiny Name - `{destiny_name.name}`",
                inline=False,
            )

        await ctx.send(embeds=embed)


def setup(client):
    UserInfo(client)
