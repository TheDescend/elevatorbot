from functions.network import getJSONfromURL
from functions.database import lookupDestinyID, lookupDiscordID, getBountyUserList, getLevel, addLevel, setLevel
from functions.dataLoading import getPlayersPastPVE, getStats, getProfile
from static.dict import metricRaidCompletion, metricAvailableRaidCompletion
from functions.formating    import embed_message

import datetime
import json
import pickle
import os


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

    return {discordID: highest_score}


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


# saves the current competition bounties leaderboards. gets reset in awardCompetitionBountiesPoints()
def changeCompetitionBountiesLeaderboards(leaderboard_name, leaderboard_data):  # leaderboard_date = {discordID: score}
    if not os.path.exists('functions/bounties/competitionBountiesLeaderboards.pickle'):
        file = {}
    else:
        with open('functions/bounties/competitionBountiesLeaderboards.pickle', "rb") as f:
            file = pickle.load(f)

    # create entry or get it if exists
    if leaderboard_name not in file.keys():
        file[leaderboard_name] = {}

    # update the players score and sort it again
    file[leaderboard_name].update(leaderboard_data)
    file[leaderboard_name] = {k: v for k, v in sorted(file[leaderboard_name].items(), key=lambda item: item[1], reverse=True)}

    # overwrite the file
    with open('functions/bounties/competitionBountiesLeaderboards.pickle', "wb") as f:
        pickle.dump(file, f)


# gets the current competition bounties leaderboards. gets reset (file gets deleted) in awardCompetitionBountiesPoints()
# leaderboards = {topic(fe. "Raids"): {id1: score, id2:score,...}, topic2: {...
def getCompetitionBountiesLeaderboards():
    # skip this is the file doesn't exist
    if not os.path.exists('functions/bounties/competitionBountiesLeaderboards.pickle'):
        return {}

    # load the file
    with open('functions/bounties/competitionBountiesLeaderboards.pickle', "rb") as f:
        return pickle.load(f)


# sets the exp level for "pve" - currently kd above 1.11
def experiencePvp(destinyID):
    limit = 1.11    # since that includes hali :)

    ret = getStats(destinyID)
    if ret:
        kd = ret["mergedAllCharacters"]["results"]["allPvP"]["allTime"]["killsDeathsRatio"]["basic"]["value"]

        exp = 1 if kd >= limit else 0
        setLevel(exp, "exp_pvp", lookupDiscordID(destinyID))

        return True
    return False


# sets the exp level for "pve" - currently time played above 500h
def experiencePve(destinyID):
    limit = 500     # hours

    ret = getStats(destinyID)
    if ret:
        time_played = ret["mergedAllCharacters"]["results"]["allPvE"]["allTime"]["secondsPlayed"]["basic"]["value"]

        exp = 1 if time_played >= (limit * 60 * 60) else 0
        setLevel(exp, "exp_pve", lookupDiscordID(destinyID))

        return True
    return False


# sets the exp level for "raids" - currently 35 raids and every raid cleared
def experienceRaids(destinyID):
    limit_raids = 35            # total raids
    limit_doneEach = 1          # does every raid need to be cleared

    ret = getProfile(destinyID, 1100)
    if ret:
        # check total raid completions
        completions = 0
        for raid in metricRaidCompletion:
            completions += ret["metrics"]["data"]["metrics"][str(raid)]["objectiveProgress"]["progress"]

        # check if every raid got cleared. Only looks at currently available raids
        clears = True
        for raid in metricAvailableRaidCompletion:
            if limit_doneEach > ret["metrics"]["data"]["metrics"][str(raid)]["objectiveProgress"]["progress"]:
                clears = False
                break

        exp = 1 if (completions >= limit_raids) and clears else 0
        setLevel(exp, "exp_raids", lookupDiscordID(destinyID))

        return True
    return False


# returns the sorted leaderboard for the specific topic. Returns dict = {id: score, ...}
def returnLeaderboard(topic):
    leaderboard = {}

    # loop through users and get their individual score
    for discordID in getBountyUserList():
        leaderboard.update({discordID: getLevel(topic, discordID)})

    # return sorted
    return {k: v for k, v in sorted(leaderboard.items(), key=lambda item: item[1], reverse=True)}


# formats and sorts the entries. Input is dict = {id: score, id2: score2,...} output is list = [fancy sentence for id1, ...]
async def formatLeaderboardMessage(client, leaderboard, user_id=None):
    # how long the leaderboard will be
    limit = 10

    # sort that shit
    leaderboard = {k: v for k, v in sorted(leaderboard.items(), key=lambda item: item[1], reverse=True)}

    # format that shit
    ranking = []
    found = True if user_id is None else False
    i = 1
    for id, points in leaderboard.items():
        if i > limit and found:
            break

        elif i > limit and not found:
            # adding only this user
            if id == user_id:
                ranking.append("...")
                ranking.append(str(i) + ") **" + client.get_user(id).display_name + "** _(Points: " + str(points) + ")_")
                break

        else:
            # if user id is given, do some fancy formating
            if id == user_id:
                found = True
                ranking.append(str(i) + ") **[ " + client.get_user(id).display_name + " ]** _(Points: " + str(points) + ")_")
            else:
                ranking.append(str(i) + ") **" + client.get_user(id).display_name + "** _(Points: " + str(points) + ")_")

        i += 1

    return ranking