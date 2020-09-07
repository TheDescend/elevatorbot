from functions.network import getJSONfromURL
from functions.database import lookupDestinyID, lookupDiscordID, getBountyUserList, getLevel, addLevel, setLevel
from functions.dataLoading import getPGCR, getPlayersPastPVE, getStats, getProfile, returnManifestInfo
from functions.network import getJSONfromURL
from static.dict import speedrunActivities, metricRaidCompletion, metricAvailableRaidCompletion
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


def threadingBounties(bounties, cutoff, discordID):
    destinyID = lookupDestinyID(discordID)
    experience_level_pve = getLevel("exp_pve", discordID)
    experience_level_pvp = getLevel("exp_pvp", discordID)
    experience_level_raids = getLevel("exp_raids", discordID)

    # initialise completions list used later to save values to
    completions = {}
    for topic in bounties:
        completions.update({topic: 0})

    # initialise wins list used later to save values to
    wins = {}
    for topic in bounties:
        wins.update({topic: 0})

    # loop though activities
    for activity in getPlayersPastPVE(destinyID, mode=0):
        # only look at activities younger than the cutoff date
        if datetime.datetime.strptime(activity["period"], "%Y-%m-%dT%H:%M:%SZ") < cutoff:
            break

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
                    if playerHasDoneBounty(discordID, bounty):
                        break

                    requirements = bounties[topic][experience][bounty]

                    # if true, a bounty is done
                    done, number_of_completions, number_of_wins = fulfillRequirements(requirements, activity, destinyID, completions[topic], wins[topic])
                    completions[topic] += number_of_completions
                    wins[topic] += number_of_wins
                    if done:
                        playerHasDoneBounty(discordID, bounty, True)
                        addLevel(requirements["points"], f"points_bounties_{topic.lower()}", discordID)
                        print(f"""DestinyID {destinyID} has completed bounty {bounty} with instanceID {activity["activityDetails"]["instanceId"]}""")

    print(f"Bounties for destinyID: {destinyID} done")


def threadingCompetitionBounties(bounties, cutoff, discordID):
    destinyID = lookupDestinyID(discordID)

    # create leaderboard dict
    leaderboard = {}
    sort_by = {}
    for topic in bounties:
        leaderboard[topic] = {}
        sort_by.update({topic: True})

    # loop through activities
    for activity in getPlayersPastPVE(destinyID, mode=0):
        # only look at activities younger than the cutoff date
        if datetime.datetime.strptime(activity["period"], "%Y-%m-%dT%H:%M:%SZ") < cutoff:
            break

        # loop though all the competition bounties
        for topic in bounties:
            sort_by_highest = True
            best_score = 0

            for bounty, req in bounties[topic].items():  # there is only one item in here
                # add to high score if new high score, otherwise skip
                ret, sort_by_highest = returnScore(req, activity, destinyID)

                # next, if 0 got returned
                if ret == 0:
                    continue

                # overwrite value if better
                if sort_by_highest:
                    if ret > best_score:
                        best_score = ret
                else:
                    if (ret < best_score) or (best_score == 0):
                        best_score = ret

                # update leaderboards
                sort_by.update({topic: sort_by_highest})
                leaderboard[topic].update({discordID: best_score})

    # update the leaderboard file
    for topic in leaderboard:
        changeCompetitionBountiesLeaderboards(topic, leaderboard[topic], sort_by[topic])

    print(f"Competitive bounties for destinyID: {destinyID} done")


# return true if name is in the pickle, otherwise false and add name to pickle
def playerHasDoneBounty(discordID, name, done=False):
    if not os.path.exists('functions/bounties/playerBountyStatus.pickle'):
        file = {}
    else:
        with open('functions/bounties/playerBountyStatus.pickle', "rb") as f:
            file = pickle.load(f)

    # read
    if not done:
        try:
            if name in file[discordID]:
                return True
        except KeyError:
            pass


    # write
    else:
        try:
            file[discordID].append(name)
        except KeyError:
            file[discordID] = [name]

        with open('functions/bounties/playerBountyStatus.pickle', "wb") as f:
            pickle.dump(file, f)

    return False


# saves the current competition bounties leaderboards. gets reset in awardCompetitionBountiesPoints()
def changeCompetitionBountiesLeaderboards(leaderboard_name, leaderboard_data, sort_by_highest=True):  # leaderboard_date = {discordID: score}
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
    file[leaderboard_name] = {k: v for k, v in sorted(file[leaderboard_name].items(), key=lambda item: item[1], reverse=sort_by_highest)}

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
async def formatLeaderboardMessage(client, leaderboard, user_id=None, limit=10):
    # limit = how long the leaderboard will be

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


# --------------------------------------------------------------
# checking bounties requirements
def fulfillRequirements(requirements, activity, destinyID, past_completions, past_wins):
    # write the requirement into the this list if it is done. At the end it will get check and if all the requirements are in there, true gets returned
    complete_list = []

    # completions / wins used for completions / wins
    completions = 0
    wins = 0

    hashID = activity["activityDetails"]["directorActivityHash"]
    instance = activity["activityDetails"]["instanceId"]

    pgcr = getPGCR(instance)

    # clean runs
    clean = cleanRuns(pgcr, destinyID)
    if not clean:
        return False, 0, 0


    # loop through other requirements
    for req in requirements["requirements"]:
        if req == "allowedTypes":
            if returnManifestInfo("DestinyActivityDefinition", hashID)["Response"]["activityTypeHash"] in requirements["allowedTypes"]:
                complete_list.append(req)
            else:
                return False, 0, 0


        if req == "allowedActivities":
            found = False
            for activity_list in requirements["allowedActivities"]:
                if instance in activity_list:
                    complete_list.append(req)
                    found = True
                    break

            if not found:
                return False, 0, 0


        if req == "firstClear":
            # get raid metrics for future comparison
            individual_raid_clears = getProfile(destinyID, 1100)
            if individual_raid_clears:
                # loop though allowedActivities
                for activity_list in requirements["firstClear"]:
                    for activity in activity_list:
                        # make sure an allowed activity is selected
                        if activity == hashID:

                            # set return to true if raid wasn't cleared before. So compare to one, since raid is now cleared. This shouldn't be a problem, since this gets check every 30mins, but it could bug out if they the raid 2x within that time
                            if individual_raid_clears["metrics"]["data"]["metrics"][str(hashID)]["objectiveProgress"]["progress"] == 1:
                                complete_list.append(req)
                            else:
                                return False, 0, 0


        if req == "completions":
            # add to completions
            completions += 1

            # check if enough completions
            if (past_completions + completions) == requirements["completions"]:
                complete_list.append(req)


        if req == "customLoadout":
            for player in pgcr["Response"]["entries"]:
                if player["player"]["destinyUserInfo"]["membershipId"] == str(destinyID):

                    # loop through weapons
                    all_weapons_ok = True
                    for weapon in player["extended"]["weapons"]:
                        weapon_info = returnManifestInfo("DestinyInventoryItemDefinition", weapon["referenceId"])
                        weapon_info_slot = weapon_info["Response"]["equippingBlock"]["equipmentSlotTypeHash"]
                        weapon_info_type_name = weapon_info["Response"]["itemTypeDisplayName"]

                        # check if weapon is allowed in slot
                        for slot, allowed_weapon_type in requirements["customLoadout"].items():
                            if not (slot == weapon_info_slot and allowed_weapon_type == weapon_info_type_name):
                                all_weapons_ok = False

                    # return true if all weapons were ok
                    if all_weapons_ok:
                        complete_list.append(req)
                    else:
                        return False, 0, 0


        if req == "contest":
            for player in pgcr["Response"]["entries"]:
                if player["player"]["destinyUserInfo"]["membershipId"] == str(destinyID):
                    # get light level
                    light_player = player["player"]["lightLevel"]

                    # get activity light level
                    light_activity = returnManifestInfo("DestinyActivityDefinition", hashID)["Response"]["activityLightLevel"]

                    if (light_player + requirements["contest"]) <= light_activity:
                        complete_list.append(req)
                    else:
                        return False, 0, 0


        if req == "speedrun":
            for player in pgcr["Response"]["entries"]:
                if player["player"]["destinyUserInfo"]["membershipId"] == str(destinyID):
                    time = player["values"]["activityDurationSeconds"]["basic"]["value"]

                    # do a different calc if "allowedTypes" or "allowedActivities"
                    if "allowedTypes" in requirements["requirements"]:
                        # check if activityDurationSeconds is shorter than allowed
                        if requirements["speedrun"] <= time:
                            complete_list.append(req)
                        else:
                            return False, 0, 0

                    elif "allowedActivities" in requirements["requirements"]:
                        found = False
                        for activities in speedrunActivities:
                            if speedrunActivities["activities"] <= time:
                                complete_list.append(req)
                                found = True
                                break

                        if not found:
                            return False, 0, 0


        if req == "totalKills":
            for player in pgcr["Response"]["entries"]:
                if player["player"]["destinyUserInfo"]["membershipId"] == str(destinyID):
                    if player["values"]["kills"]["basic"]["value"] >= requirements["totalKills"]:
                        complete_list.append(req)
                    else:
                        return False, 0, 0


        if req == "totalDeaths":
            for player in pgcr["Response"]["entries"]:
                if player["player"]["destinyUserInfo"]["membershipId"] == str(destinyID):
                    if player["values"]["deaths"]["basic"]["value"] >= requirements["totalDeaths"]:
                        complete_list.append(req)
                    else:
                        return False, 0, 0


        if req == "kd":
            for player in pgcr["Response"]["entries"]:
                if player["player"]["destinyUserInfo"]["membershipId"] == str(destinyID):
                    if player["values"]["killsDeathsRatio"]["basic"]["value"] >= requirements["kd"]:
                        complete_list.append(req)
                    else:
                        return False, 0, 0


        if req == "win":
            for player in pgcr["Response"]["entries"]:
                if player["player"]["destinyUserInfo"]["membershipId"] == str(destinyID):
                    if player["values"]["standing"]["basic"]["value"] == "Victory":
                        complete_list.append(req)
                    else:
                        return False, 0, 0


        if req == "winStreak":
            wins += 1

            # check if enough completions
            if (past_wins + wins) == requirements["winStreak"]:
                complete_list.append(req)


        if req == "NFscore":
            for player in pgcr["Response"]["entries"]:
                if player["player"]["destinyUserInfo"]["membershipId"] == str(destinyID):
                    if player["values"]["score"]["basic"]["value"] >= requirements["NFscore"]:
                        complete_list.append(req)
                    else:
                        return False, 0, 0

    # only return true if everything else passes
    all_done = True
    for req in requirements["requirements"]:
        if req not in complete_list:
            all_done = False
    return all_done, completions, wins


# checking competition bounties scores
def returnScore(requirements, activity, destinyID):
    score = 0
    sort_by_highest = True

    hashID = activity["activityDetails"]["directorActivityHash"]
    instance = activity["activityDetails"]["instanceId"]

    pgcr = getPGCR(instance)

    # clean runs
    clean = cleanRuns(pgcr, destinyID)
    if not clean:
        return 0, sort_by_highest


    # loop through other requirements
    for req in requirements["requirements"]:
        if req == "allowedTypes":
            if returnManifestInfo("DestinyActivityDefinition", hashID)["Response"]["activityTypeHash"] not in requirements["allowedTypes"]:
                return 0, sort_by_highest


        elif req == "allowedActivities":
            if hashID not in requirements["allowedActivities"]:
                return 0, sort_by_highest


        elif req == "speedrun":
            for player in pgcr["Response"]["entries"]:
                if player["player"]["destinyUserInfo"]["membershipId"] == str(destinyID):

                    # set score
                    sort_by_highest = False
                    score = player["values"]["activityDurationSeconds"]["basic"]["value"] / 60
                    score = round(score, 2)
                    break


        elif req == "lowman":
            for player in pgcr["Response"]["entries"]:
                if player["player"]["destinyUserInfo"]["membershipId"] == str(destinyID):

                    # set score
                    sort_by_highest = False
                    score = int(player["values"]["playerCount"]["basic"]["value"])


        elif req == "noWeapons":
            # return 0 if there are any weapon kills
            for player in pgcr["Response"]["entries"]:
                for weapon in player["extended"]["weapons"]:
                    if weapon["values"]["uniqueWeaponKills"] != 0:
                        return 0, sort_by_highest


        elif req == "totalKills":
            for player in pgcr["Response"]["entries"]:
                if player["player"]["destinyUserInfo"]["membershipId"] == str(destinyID):

                    # set score
                    score = int(player["values"]["kills"]["basic"]["value"])
                    break


        elif req == "kd":
            for player in pgcr["Response"]["entries"]:
                if player["player"]["destinyUserInfo"]["membershipId"] == str(destinyID):

                    # set score
                    score = player["values"]["killsDeathsRatio"]["basic"]["value"]
                    score = round(score, 2)
                    break


        elif req == "NFscore":
            for player in pgcr["Response"]["entries"]:
                if player["player"]["destinyUserInfo"]["membershipId"] == str(destinyID):

                    # set score
                    score = int(player["values"]["score"]["basic"]["value"])
                    break


        elif req == "tournament":
            pass
            # todo

    # only return score if all other things have passed
    return score, sort_by_highest


# checks cp runs, if completed
def cleanRuns(pgcr, destinyID):
    # check for checkpoint runs
    if pgcr["Response"]["startingPhaseIndex"] not in [-1, 0]:
        return False

    # check if activity got completed
    for player in pgcr["Response"]["entries"]:
        if player["player"]["destinyUserInfo"]["membershipId"] == str(destinyID):
            if player["values"]["completed"]["basic"]["value"] != 1:
                return False

    return True










