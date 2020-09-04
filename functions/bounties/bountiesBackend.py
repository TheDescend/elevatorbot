from functions.network import getJSONfromURL
from functions.database import getBountyUserList, lookupDestinyID, getLevel, addLevel
from functions.dataLoading import getPlayersPastPVE
from functions.formating    import embed_message
from functions.bounties.bountiesFunctions import displayCompetitionBounties

import datetime
import json
import pickle
import os
import discord
import concurrent.futures

# return winner of the last game in the pvp history, if just those two players where in it
def returnCustomGameWinner(destinyID1, charIDs1, membershipType1, destinyID2):
    for char in charIDs1:
        staturl = f"https://www.bungie.net/Platform/Destiny2/{membershipType1}/Account/{destinyID1}/Character/{char}/Stats/Activities/?mode=0&count=1&page=0"
        rep = getJSONfromURL(staturl)
        if rep and rep['Response']:
            rep = json.loads(json.dumps(rep))
            # if it's not a private game
            if not rep["Response"]["activities"][0]["activityDetails"]["isPrivate"]:
                return False

            # if it's not completed
            if not int(rep["Response"]["activities"][0]["values"]["completed"]["basic"]["value"]) == 1:
                return False

            ID = rep["Response"]["activities"][0]["activityDetails"]["instanceId"]
            staturl = f"https://stats.bungie.net/Platform/Destiny2/Stats/PostGameCarnageReport/{ID}/"
            rep2 = getJSONfromURL(staturl)
            if rep2 and rep2['Response']:
                rep2 = json.loads(json.dumps(rep2))

                # if more / less than 2 players
                if len(rep2["Response"]["entries"]) != 2:
                    return False

                found1, found2 = False
                for player in rep2["Response"]["entries"]:
                    if int(player["player"]["destinyUserInfo"]["membershipId"]) == int(destinyID1):
                        found1 = True
                    elif int(player["player"]["destinyUserInfo"]["membershipId"]) == int(destinyID2):
                        found2 = True

                # players need to be the once specified
                if found1 and found2:
                    if rep["Response"]["activities"][0]["values"]["standing"]["basic"]["displayValue"] == "Victory":
                        return destinyID1
                    else:
                        return destinyID2
    return False


# checks if any player has completed a bounty
async def bountyCompletion(client):
    # load bounties
    with open('functions/bounties/currentBounties.pickle', "rb") as f:
        bounties = pickle.load(f)
    cutoff = datetime.datetime.strptime(bounties["time"], "%Y-%m-%d %H:%M:%S.%f")

    # load channel ids
    with open('functions/bounties/channelIDs.pickle', "rb") as f:
        file = pickle.load(f)
        for guild in client.guilds:
            if guild.id == file["guild_id"]:
                break

    # loop though all registered users
    with concurrent.futures.ThreadPoolExecutor(os.cpu_count() * 5) as pool:
        futurelist = [pool.submit(threadingBounties, bounties["bounties"], cutoff, user) for user in getBountyUserList()]

        for future in concurrent.futures.as_completed(futurelist):
            try:
                result = future.result()
            except Exception as exc:
                print(f'generated an exception: {exc}')


    # loop though all the competition bounties
    for topic in bounties["competition_bounties"]:
        for bounty in bounties["competition_bounties"][topic]:

            # gets the msg object related to the current topic in the competition_bounties_channel
            message = await discord.utils.get(client.guild.channels, id=file["competition_bounties_channel"]).fetch_message(file[f"competition_bounties_channel_{topic.lower()}_message_id"])

            # create leaderboard dict
            leaderboard = {}

            # loop though all registered users
            with concurrent.futures.ThreadPoolExecutor(os.cpu_count() * 5) as pool:
                futurelist = [pool.submit(threadingCompetitionBounties, bounties["competition_bounties"][topic][bounty], cutoff, user.id)
                              for user in getBountyUserList()]

                for future in concurrent.futures.as_completed(futurelist):
                    try:
                        result = future.result()
                        leaderboard.update(result)
                    except Exception as exc:
                        print(f'generated an exception: {exc}')

            # sort leaderboard
            leaderboard = {k: v for k, v in sorted(leaderboard.items(), key=lambda item: item[1], reverse=True)}

            # update bounty leaderboard
            ranking = []
            i = 1
            for key, value in leaderboard.items():
                ranking.append(str(i) + ") **" + client.get_user(key).display_name + "** _(Score: " + str(value) + ")_")

                # break after 10 entries
                i += 1
                if i > 10:
                    break

            await displayCompetitionBounties(guild, file, ranking, message)


def threadingBounties(bounties, cutoff, user):
    destinyID = lookupDestinyID(user.id)
    experience_level_pve = getLevel("exp_pve", user.id)
    experience_level_pvp = getLevel("exp_pvp", user.id)
    experience_level_raids = getLevel("exp_raids", user.id)

    # loop through all the bounties
    for topic in bounties:
        for experience in bounties[topic]:

            # only go further if experience levels match
            if topic == "Raids":
                if not ((experience_level_raids == 0 and experience == "New Players") or (
                        experience_level_raids == 1 and experience == "Experienced Players")):
                    continue
            elif topic == "PvE":
                if not ((experience_level_pve == 0 and experience == "New Players") or (
                        experience_level_pve == 1 and experience == "Experienced Players")):
                    continue
            elif topic == "PvP":
                if not ((experience_level_pvp == 0 and experience == "New Players") or (
                        experience_level_pvp == 1 and experience == "Experienced Players")):
                    continue

            for bounty in bounties[topic][experience]:

                # check if user has done bounty this week already
                if playerHasDoneBounty(bounty):
                    break

                requirements = bounties[topic][experience][bounty]

                for activity in getPlayersPastPVE(destinyID, mode=0):
                    activity = json.loads(json.dumps(activity))

                    # only look at activities younger than the cutoff date
                    if datetime.datetime.strptime(activity["period"], "%Y-%m-%dT%H:%M:%SZ") > cutoff:

                        # if true, a bounty is done
                        if fulfillRequirements(requirements, activity, destinyID):
                            addLevel(requirements["points"], f"points_bounties_{topic.lower()}",user.id)


def threadingCompetitionBounties(bounty, cutoff, discordID):
    destinyID = lookupDestinyID(discordID)

    highest_score = 0
    for activity in getPlayersPastPVE(destinyID, mode=0):
        activity = json.loads(json.dumps(activity))

        # only look at activities younger than the cutoff date
        if datetime.datetime.strptime(activity["period"], "%Y-%m-%dT%H:%M:%SZ") > cutoff:

            # add to high score if new high score, otherwise skip
            ret = returnScore(bounty, activity)
            if ret > highest_score:
                highest_score = ret

    return {discordID, highest_score}




def fulfillRequirements(requirements, activity, destinyID):
    for req in requirements["requirements"]:
        # todo
        #if req == ....
        pass

    return True

def returnScore(requirements, activity):
    # todo
    return 10


# return true if name is in the pickle, otherwise false and add name to pickle
def playerHasDoneBounty(discordID, name):
    if not os.path.exists('functions/bounties/playerBountyStatus.pickle'):
        file = {}
    else:
        with open('functions/bounties/playerBountyStatus.pickle', "rb") as f:
            file = pickle.load(f)

    try:
        if name in file[discordID]:
            return True
        else:
            file[discordID].append(name)
    except KeyError:
        file[discordID] = [name]

    with open('functions/bounties/playerBountyStatus.pickle', "wb") as f:
        pickle.dump(file, f)

    return False


