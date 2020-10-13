from functions.formating import embed_message
from functions.miscFunctions import checkIfUserIsRegistered
from functions.network import getJSONfromURL, postJSONtoBungie
from functions.database import lookupDestinyID, getToken
from functions. dataLoading import getMembershipType
from static.config import CLANID, BOTDEVCHANNELID

import asyncio


async def clanJoinRequestMessageReactions(client, user, emoji, channel, channel_message_id):
    message = await channel.fetch_message(channel_message_id)
    join = client.get_emoji(754928322403631216)
    destinyID = lookupDestinyID(user.id)

    # if the reaction is the correct one
    if emoji.id == join.id:
        # remove reaction
        await message.remove_reaction(join, user)

        # abort if user already is in clan
        for member in (await getJSONfromURL(f"https://www.bungie.net/Platform/GroupV2/{CLANID}/Members/"))["Response"]["results"]:
            memberID = int(member["destinyUserInfo"]["membershipId"])
            if memberID == destinyID:
                print(f"{member.display_name} tried to join the clan while being in it")
                return

        # # abort if user is @not_registered
        # if not await checkIfUserIsRegistered(user):
        #     return

        # abort if user doesn't fulfill requirements
        req = await checkRequirements(user.id)
        if req:
            embed = embed_message(
                "Clan Application",
                "Sorry, you don't fulfill the needed requirements"
            )
            for name, value in req.items():
                embed.add_field(name=name, value=value, inline=True)

            await user.send(embed=embed)
            return

        # send user a clan invite (using kigstn's id / token since he is an admin and not the owner for some safety)
        membershipType = await getMembershipType(destinyID)
        postURL = f'https://www.bungie.net/Platform/GroupV2/{CLANID}/Members/IndividualInvite/{membershipType}/{destinyID}/'
        data = {
            "message": "Welcome"
        }
        ret = await postJSONtoBungie(postURL, data, 238388130581839872)

        # inform user if invite was send / sth went wrong
        if ret["error"] is None:
            text = "Send you a clan application"
            newtonslab = client.get_channel(BOTDEVCHANNELID)
            embed = embed_message(
                "Clan Update",
                f"{user.display_name} with discordID <{user.id}> and destinyID <{destinyID}> has been send a clan invite"
            )
            await newtonslab.send(embed=embed)
        else:
            text = ret["error"]

        embed = embed_message(
            "Clan Application",
            text
        )
        await user.send(embed=embed)


# if a user leaves discord, he will be removed from the clan as well if admins react to the msg in the bot dev channel
async def removeFromClanAfterLeftDiscord(client, member):
    # remove this  once everyone is happy with this
    return

    # wait 10 mins bc bungie takes forever in updating the clan roster
    await asyncio.sleep(10 * 60)

    # check if user was in clan
    destinyID = lookupDestinyID(member.id)
    found = False
    for clan_member in (await getJSONfromURL(f"https://www.bungie.net/Platform/GroupV2/{CLANID}/Members/"))["Response"]["results"]:
        clan_memberID = int(clan_member["destinyUserInfo"]["membershipId"])
        if clan_memberID == destinyID:
            found = True
            break

    if not found:
        print(f"{member.display_name} has left discord, but wasn't in the clan")
        return

    # promts in newtonslab, if yes is pressed he is removed
    newtonslab = client.get_channel(BOTDEVCHANNELID)
    yes = client.get_emoji(754946723612196975)
    no = client.get_emoji(754946723503276124)

    embed = embed_message(
        "Clan Update",
        f"{member.display_name} with discordID <{member.id}> and destinyID <{destinyID}> has left the Discord but is still in the clan. \nKick him?"
    )
    message = await newtonslab.send(embed=embed)
    await message.add_reaction(yes)
    await message.add_reaction(no)

    # check that the reaction user was not a bot, used "yes" or "no" reaction and reacted to the correct message
    def check(reaction_reaction, reaction_user):
        return (not reaction_user.bot) and (reaction_reaction.emoji == yes or reaction_reaction.emoji == no) and (reaction_reaction.message.id == message.id)
    reaction, _ = await client.wait_for('reaction_add', check=check)

    # if yes is pressed he is removed (using kigstn's id / token since he is an admin and not the owner for some safety)
    if reaction.emoji == yes:
        membershipType = await getMembershipType(destinyID)
        postURL = f'https://www.bungie.net/Platform/GroupV2/{CLANID}/Members/{membershipType}/{destinyID}/Kick/'
        data = {}

        ret = await postJSONtoBungie(postURL, data, 238388130581839872)

        if ret["error"] is None:
            text = "Successfully removed!"
        else:
            text = ret["error"]
    else:
        text = "Aborted"

    await newtonslab.send(text)


# returns a dict with the requirements which are not fulfilled, otherwise return None
async def checkRequirements(discordID):

    return None

