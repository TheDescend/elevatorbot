import asyncio

import discord
from discord_slash import ComponentContext, ButtonStyle
from discord_slash.utils import manage_components

from database.database import lookupDestinyID, lookupSystem
from functions.formating import embed_message
from functions.miscFunctions import checkIfUserIsRegistered
from networking.network import get_json_from_url, post_json_to_url
from static.config import CLANID, BOTDEVCHANNELID, BUNGIE_OAUTH
from static.globals import thumps_up_emoji_id, thumps_down_emoji_id


async def on_clan_join_request(
    ctx: ComponentContext
):
    await ctx.defer(hidden=True)

    newtonslab = ctx.guild.get_channel(BOTDEVCHANNELID)
    destinyID = await lookupDestinyID(ctx.author.id)

    # abort if user already is in clan
    for member in (await get_json_from_url(f"https://www.bungie.net/Platform/GroupV2/{CLANID}/Members/")).content["Response"]["results"]:
        memberID = int(member["destinyUserInfo"]["membershipId"])
        if memberID == destinyID:
            print(f"{ctx.author.display_name} tried to join the clan while being in it")
            await ctx.send(
                hidden=True, embed=embed_message(
                    "Clan Application",
                    "You are already in the clan"
                )
            )
            return

    # abort if user is @not_registered
    if not await checkIfUserIsRegistered(ctx.author):
        await ctx.send(
            hidden=True, embed=embed_message(
                "Clan Application",
                "Please `/registerdesc` and then try again"
            )
        )
        return

    # abort if member hasnt accepted the rules
    if ctx.author.pending:
        await ctx.send(
            hidden=True, embed=embed_message(
                "Clan Application",
                "Please accept the rules and then try again"
            )
        )
        return

    # abort if user doesn't fulfill requirements
    req = await checkRequirements(ctx.author.id)
    if req:
        embed = embed_message(
            "Clan Application",
            "Sorry, you don't fulfill the needed requirements"
        )
        for name, value in req.items():
            embed.add_field(name=name, value=value, inline=True)

        await ctx.send(hidden=True, embed=embed)
        return

    # send user a clan invite (using kigstn's id / token since he is an admin and not the owner for some safety)
    membershipType = await lookupSystem(destinyID)
    postURL = f'https://www.bungie.net/Platform/GroupV2/{CLANID}/Members/IndividualInvite/{membershipType}/{destinyID}/'
    data = {
        "message": "Welcome"
    }
    ret = await post_json_to_url(postURL, data, 219517105249189888)  # Halis ID

    # inform user if invite was send / sth went wrong
    if ret.success:
        text = "Sent you a clan application"
        embed = embed_message(
            "Clan Update",
            f"{ctx.author.display_name} with discordID <{ctx.author.id}> and destinyID <{destinyID}> has been sent a clan invite"
        )
        await newtonslab.send(embed=embed)
    else:
        if ret.error == "ClanTargetDisallowsInvites":
            text = "You are currently disallowing clan invites from other people. \nTo change this, go to your account settings on `bungie.net` and then try again"
        else:
            text = ret.error

    embed = embed_message(
        "Clan Application",
        text
    )
    await ctx.send(hidden=True, embed=embed)


# if a user leaves discord, he will be removed from the clan as well if admins react to the msg in the bot dev channel
async def removeFromClanAfterLeftDiscord(
    client,
    member
):
    # wait 10 mins bc bungie takes forever in updating the clan roster
    await asyncio.sleep(10 * 60)

    # check if user was in clan
    destinyID = await lookupDestinyID(member.id)
    found = False
    for clan_member in (await get_json_from_url(f"https://www.bungie.net/Platform/GroupV2/{CLANID}/Members/")).content["Response"]["results"]:
        clan_memberID = int(clan_member["destinyUserInfo"]["membershipId"])
        if clan_memberID == destinyID:
            found = True
            break

    if not found:
        print(f"{member.display_name} has left discord, but wasn't in the clan")
        return

    # promts in newtonslab, if yes is pressed he is removed
    newtonslab = client.get_channel(BOTDEVCHANNELID)
    yes = client.get_emoji(thumps_up_emoji_id)
    no = client.get_emoji(thumps_down_emoji_id)

    embed = embed_message(
        "Clan Update",
        f"{member.display_name} with discordID <{member.id}> and destinyID <{destinyID}> has left the Discord but is still in the clan. \nKick him?"
    )
    message = await newtonslab.send(embed=embed)
    await message.add_reaction(yes)
    await message.add_reaction(no)


    # check that the reaction user was not a bot, used "yes" or "no" reaction and reacted to the correct message
    def check(
        reaction_reaction,
        reaction_user
    ):
        return (not reaction_user.bot) and (reaction_reaction.emoji == yes or reaction_reaction.emoji == no) and (reaction_reaction.message.id == message.id)


    reaction, _ = await client.wait_for('reaction_add', check=check)

    # if yes is pressed he is removed (using kigstn's id / token since he is an admin and not the owner for some safety)
    if reaction.emoji == yes:
        membershipType = await lookupSystem(destinyID)
        postURL = f'https://www.bungie.net/Platform/GroupV2/{CLANID}/Members/{membershipType}/{destinyID}/Kick/'
        data = {}
        # Kigstns discord ID
        ret = await post_json_to_url(postURL, data, 238388130581839872)

        if ret.success:
            text = "Successfully removed!"
        else:
            text = ret.error
    else:
        text = "Aborted"

    await newtonslab.send(text)


# returns a dict with the requirements which are not fulfilled, otherwise return None
async def checkRequirements(
    discordID
) -> dict:
    return {}


async def elevatorRegistration(
    user: discord.Member
):
    URL = f"https://www.bungie.net/en/oauth/authorize?client_id={BUNGIE_OAUTH}&response_type=code&state={str(user.id) + ':' + str(user.guild.id)}"

    components = [
        manage_components.create_actionrow(
            manage_components.create_button(
                style=ButtonStyle.URL,
                label=f"Registration Link",
                url=URL
            ),
        ),
    ]

    await user.send(
        components=components, embed=embed_message(
            f'Registration',
            f'Use the button below to register with me',
            "Please be aware that I will need a while to process your data after you register for the first time, so I might react very slow to your first commands."
        )
    )
