from functions.formating import embed_message
from functions.database import insertBountyUser, getBountyUserList, getLevel, addLevel, setLevel, lookupDestinyID, lookupServerID
from functions.bounties.boutiesBountyRequirements import bounties, competition_bounties, possibleWeaponsKinetic, possibleWeaponsEnergy, possibleWeaponsPower
from functions.bounties.bountiesBackend import saveAsGlobalVar, getGlobalVar, addPoints, formatLeaderboardMessage, returnLeaderboard, getCompetitionBountiesLeaderboards, changeCompetitionBountiesLeaderboards, experiencePvp, experiencePve, experienceRaids, threadingCompetitionBounties, threadingBounties
from functions.bounties.bountiesTournament import tournamentRegistrationMessage
from functions.dataLoading import returnManifestInfo
from static.dict import activityRaidHash, speedrunActivitiesRaids, weaponTypeKinetic, weaponTypeEnergy, weaponTypePower

import os
import pickle
import discord
import random
import json
import asyncio
import datetime
import concurrent.futures



# randomly generate bounties. One per topic for both of the lists
async def generateBounties(client):
    # award points for the competition bounties
    await awardCompetitionBountiesPoints(client)

    # clean the tourn channel registration message if exist
    file = getGlobalVar()
    for guild in client.guilds:
        if guild.id == file["guild_id"]:
            try:
                tourn_channel = discord.utils.get(guild.channels, id=file["tournament_channel"])
                tourn_msg = await tourn_channel.fetch_message(file["tournament_channel_message_id"])
                await tourn_msg.delete()
            except:
                pass

    # looping though the bounties
    file = {}
    file["bounties"] = {}
    for topic in bounties.keys():
        file["bounties"][topic] = {}
        for experience in bounties[topic].keys():
            key, value = bountiesFormatting(bounties[topic][experience])

            file["bounties"][topic][experience] = {}
            file["bounties"][topic][experience][key] = value

    # looping though the competition bounties
    file["competition_bounties"] = {}
    for topic in competition_bounties.keys():
        key, value = bountiesFormatting(competition_bounties[topic])

        file["competition_bounties"][topic] = {}
        file["competition_bounties"][topic][key] = value

        # if "tournament" is in there, put the tourn message up
        if "tournament" in value["requirements"]:
            await tournamentRegistrationMessage(client)

    # add current time to list
    file["time"] = "2020-08-05 19:41:13.688291" # todo change this back. only for testing
    #file["time"] = str(datetime.datetime.now())

    # overwrite the old bounties
    with open('functions/bounties/currentBounties.pickle', "wb") as f:
        pickle.dump(file, f)

    print("Generated new bounties:")
    print(json.dumps(file, indent=4))

    # update the display
    task = displayBounties(client)
    asyncio.run_coroutine_threadsafe(task, client.loop)

    # delete old bounty completion tracking pickle
    if os.path.exists('functions/bounties/playerBountyStatus.pickle'):
        os.remove('functions/bounties/playerBountyStatus.pickle')


# do the random selection and the extraText formating
def bountiesFormatting(json):
    key, value = random.choice(list(json.items()))

    # if "randomActivity" is present, get a random activity from the list and delete "randomActivity" so it doesn't take up space anymore
    if "randomActivity" in value:
        value["allowedActivities"] = [random.choice(value.pop("randomActivity"))[0]]
        value["requirements"].pop(value["requirements"].index("randomActivity"))
        value["requirements"].append("allowedActivities")

    # if "customLoadout" is present, get a random loadout from the list
    if "customLoadout" in value["requirements"]:
        weaponKinetic = random.choice(possibleWeaponsKinetic)
        weaponEnergy = random.choice(possibleWeaponsEnergy)
        weaponPower = random.choice(possibleWeaponsPower)

        value["customLoadout"] = {
            weaponTypeKinetic: weaponKinetic,
            weaponTypeEnergy: weaponEnergy,
            weaponTypePower: weaponPower
        }

    # if "extraText" is present, process that
    if "extraText" in value:
        if "allowedActivities" in value["requirements"]:
            activity_name = returnManifestInfo("DestinyActivityDefinition", value["allowedActivities"][0])["Response"]["displayProperties"]["name"]
            key = key.replace("?", activity_name)

        if "customLoadout" in value["requirements"]:
            key = key + value["extraText"]

            key = key.replace("?", f"__{weaponKinetic}__")
            key = key.replace("%", f"__{weaponEnergy}__")
            key = key.replace("&", f"__{weaponPower}__")

        if "speedrun" in value["requirements"]:
            if "allowedTypes" in value["requirements"]:
                if activityRaidHash == value["allowedTypes"]:
                    key = key + f"\n⁣"
                    for activities in speedrunActivitiesRaids:
                        activity_name = returnManifestInfo("DestinyActivityDefinition", activities[0])["Response"]["displayProperties"]["name"]
                        key = key + f"\n{activity_name}: __{speedrunActivitiesRaids[activities] / 60}min__"

    return key, value


# awards points to whoever has the most points. Can be multiple people if tied
async def awardCompetitionBountiesPoints(client):
    # load current bounties
    with open('functions/bounties/currentBounties.pickle', "rb") as f:
        bounties = pickle.load(f)["competition_bounties"]

    # load leaderboards
    leaderboards = getCompetitionBountiesLeaderboards()

    # loop through topic, then though users
    for topic in leaderboards:
        last = None
        for discordID in leaderboards[topic]:
            # also award the points should multiple people have the same score
            if last != leaderboards[topic][discordID]:
                break

            # award the points in the respective categories
            name = list(bounties[topic].keys())[0]
            addPoints(discordID, bounties[topic], bounties[topic][name], f"points_competition_{topic.lower()}")

    # update display
    await displayLeaderboard(client)

    # delete now old leaderboards
    if os.path.exists('functions/bounties/competitionBountiesLeaderboards.pickle'):
        os.remove('functions/bounties/competitionBountiesLeaderboards.pickle')


# print the bounties in their respective channels
async def displayBounties(client):
    # load bounties
    with open('functions/bounties/currentBounties.pickle', "rb") as f:
        json = pickle.load(f)

    # get channel and guild id
    file = getGlobalVar()

    # get the users that signed up for notifications
    text = ["⁣"]    # so that it still works even with nobody signed up
    for discordID in getBountyUserList():
        if getLevel("notifications", discordID) == 1:
            text.append(f"<@{discordID}>")

    for guild in client.guilds:
        if guild.id == file["guild_id"]:
            # clean channels and call the actual print function
            if "bounties_channel" in file:
                bounties_channel = discord.utils.get(guild.channels, id=file["bounties_channel"])
                await bounties_channel.purge(limit=100)
                for topic in json["bounties"].keys():
                    embed = embed_message(
                        topic
                    )
                    for experience in json["bounties"][topic].keys():
                        name, req = list(json["bounties"][topic][experience].items())[0]

                        if isinstance(req['points'], list):
                            if "lowman" in req["requirements"]:
                                points = []
                                for x, y in zip(req["lowman"], req["points"]):
                                    points.append(f"{y}** ({x} Player)** ")
                                points = "**/ **".join(points)
                        else:
                            points = req['points']

                        embed.add_field(name=f"{experience}:", value=f"Points: **{points}** - {name}\n⁣", inline=False)
                    await bounties_channel.send(embed=embed)

                # ping users
                msg = await bounties_channel.send(" ".join(text))
                await msg.delete()

                print("Updated bounty display")

            if "competition_bounties_channel" in file:
                await displayCompetitionBounties(client, guild)

                # ping users
                msg = await discord.utils.get(guild.channels, id=file["competition_bounties_channel"]).send(" ".join(text))
                await msg.delete()

            print("Done updating displays")


async def displayCompetitionBounties(client, guild, message=None):
    # load channel ids
    file = getGlobalVar()

    # load bounties
    with open('functions/bounties/currentBounties.pickle', "rb") as f:
        json = pickle.load(f)

    # load leaderboards
    leaderboards = getCompetitionBountiesLeaderboards()

    # get channel id and clear channel
    competition_bounties_channel = discord.utils.get(guild.channels, id=file["competition_bounties_channel"])
    if not message:
        await competition_bounties_channel.purge(limit=100)

    for topic in json["competition_bounties"].keys():
        name, req = list(json["competition_bounties"][topic].items())[0]

        points = req['points']
        embed = embed_message(
            topic,
            f"Points: **{points}** - {name}\n⁣"
        )

        # read the current leaderboard and display the top x = 10 players
        ranking = []
        try:
            i = 1
            for discordID, value in leaderboards[topic].items():
                ranking.append(str(i) + ") **" + client.get_user(discordID).display_name + "** _(Score: " + str(value) + ")_")
                # break after x entries
                i += 1
                if i > 10:
                    break
        except KeyError:
            pass

        embed.add_field(name=f"Current Leaderboard:", value=f"\n".join(ranking) if ranking else "Nobody has completed this yet", inline=False)

        # edit msg if given one, otherwise create a new one and save the id
        if message:
            # gets the msg object related to the current topic in the competition_bounties_channel
            message = await discord.utils.get(guild.channels, id=file["competition_bounties_channel"]).fetch_message(file[f"competition_bounties_channel_{topic.lower()}_message_id"])
            await message.edit(embed=embed)
        else:
            msg = await competition_bounties_channel.send(embed=embed)
            saveAsGlobalVar(f"competition_bounties_channel_{topic.lower()}_message_id", msg.id)

    print("Updated competition bounty display")


# checks if any player has completed a bounty
async def bountyCompletion(client):
    # current_time = datetime.datetime.now() # todo change that
    current_time = "2020-08-05 19:41:13.688291"

    # load bounties
    with open('functions/bounties/currentBounties.pickle', "rb") as f:
        bounties = pickle.load(f)
    cutoff = datetime.datetime.strptime(bounties["time"], "%Y-%m-%d %H:%M:%S.%f")

    # load channel ids
    file = getGlobalVar()
    for guild in client.guilds:
        if guild.id == file["guild_id"]:
            break


    # loop though all registered users
    with concurrent.futures.ThreadPoolExecutor(os.cpu_count() * 5) as pool:
        futurelist = [pool.submit(threadingBounties, bounties["bounties"], cutoff, user)
                      for user in getBountyUserList()]

        for future in concurrent.futures.as_completed(futurelist):
            future.result()

    # loop though all registered users
    with concurrent.futures.ThreadPoolExecutor(os.cpu_count() * 5) as pool:
        futurelist = [pool.submit(threadingCompetitionBounties, bounties["competition_bounties"], cutoff, user)
                      for user in getBountyUserList()]

        for future in concurrent.futures.as_completed(futurelist):
            future.result()


    print("Done checking all the users")

    # display the new leaderboards
    await displayCompetitionBounties(client, guild, message=True)

    # update the big leaderboard
    await displayLeaderboard(client)

    # overwrite the old time, so that one activity doesn't get checked over and over again
    # bounties["time"] = str(current_time) #todo add that back
    with open('functions/bounties/currentBounties.pickle', "wb") as f:
        pickle.dump(bounties, f)


# updates the leaderboard display
async def displayLeaderboard(client, use_old_message=True):
    # function to condense leaderboards
    def condense(lead_big, lead_new):
        for id, value in lead_new.items():
            if value is not None and value != 0:
                if id in lead_big:
                    lead_big.update({id: (0 if lead_big[id] is None else lead_big[id]) + value})
                else:
                    lead_big.update({id: value})

    # get current leaderboards and condense them into one
    leaderboard = {}
    condense(leaderboard, returnLeaderboard("points_bounties_raids"))
    condense(leaderboard, returnLeaderboard("points_bounties_pve"))
    condense(leaderboard, returnLeaderboard("points_bounties_pvp"))
    condense(leaderboard, returnLeaderboard("points_competition_raids"))
    condense(leaderboard, returnLeaderboard("points_competition_pve"))
    condense(leaderboard, returnLeaderboard("points_competition_pvp"))

    # format that
    ranking = await formatLeaderboardMessage(client, leaderboard, limit=50)

    # load ids
    file = getGlobalVar()

    # try to get the leaderboard message id, else make a new message
    message_id = None
    try:
        message_id = file["leaderboard_channel_message_id"]
    except:
        pass

    for guild in client.guilds:
        if guild.id == file["guild_id"]:

            # get the channel id
            competition_bounties_channel = discord.utils.get(guild.channels, id=file["leaderboard_channel"])

            embed = embed_message(
                "Leaderboard",
                (f"\n".join(ranking)) if ranking else "Nobody has any points yet",
                footer="This leaderboard will update every ~30 minutes"
            )

            if message_id and use_old_message:
                # get the leaderboard msg object
                message = await discord.utils.get(
                        guild.channels,
                        id=file["leaderboard_channel"]
                    ).fetch_message(file["leaderboard_channel_message_id"])

                await message.edit(embed=embed)
            else:
                await competition_bounties_channel.purge(limit=100)
                msg = await competition_bounties_channel.send(embed=embed)
                saveAsGlobalVar("leaderboard_channel_message_id", msg.id)

    print("Updated Leaderboard")


# writes the message the user will see and react to and saves the id in the pickle
async def bountiesChannelMessage(client):
    file = getGlobalVar()

    for guild in client.guilds:
        if guild.id == file["guild_id"]:

            # the other games role channel message
            if "other_game_roles_channel" in file:
                if "other_game_roles_channel_message_id" not in file:
                    channel = discord.utils.get(guild.channels, id=file["other_game_roles_channel"])
                    await channel.purge(limit=100)

                    # send register msg and save the id
                    msg = await channel.send(embed=embed_message(
                        f'Other Game Roles',
                        f'React to add / remove other game roles'
                    ))

                    among_us = client.get_emoji(751020830376591420)
                    barotrauma = client.get_emoji(751022749773856929)
                    gta = client.get_emoji(751020831382962247)
                    valorant = client.get_emoji(751020830414209064)

                    await msg.add_reaction(among_us)
                    await msg.add_reaction(barotrauma)
                    await msg.add_reaction(gta)
                    await msg.add_reaction(valorant)

                    saveAsGlobalVar("other_game_roles_channel_message_id", msg.id)

            # put message in #register channel if there is none
            if "register_channel" in file:
                if "register_channel_message_id" not in file:
                    channel = discord.utils.get(guild.channels, id=file["register_channel"])
                    await channel.purge(limit=100)

                    # send welcome and info message
                    await channel.send(
f"""Welcome the the **Bounty Goblins**!
⁣
After you register to this truly **remarkable** program, you will be assigned an experience level and given a bunch of bounties you can complete at your leisure.
⁣
**Normal bounties** can be completed once and award you the shown points.
**Competitive bounties** are meant to be a competition between all participants and reward a lot of points, but only one player can win. If there are any ties, both parties will of course get the points.
⁣
Your experience level determines which normal bounties you can complete. That way we can have easier bounties for new players compared to veterans. 
```
+-----------------------------------------------------------+
|            Requirements for Experienced Players           |
+--------------------+---------------------+----------------+
|        Raids       |         PvE         |       PvP      |
+--------------------+---------------------+----------------+
|   35 total clears  | 500h total Playtime | K/D above 1.11 |
| Every raid cleared |                     |                |
+--------------------+---------------------+----------------+```
"""
                    )
                    await channel.send(
f"""There are a bunch of commands which will give you more thorough information than visible in the channels:
⁣
Commands:
`!leaderboard <category>` - Prints various leaderboards.
`!experienceLevel` - Updates and DMs you your experience levels. 
`!bounties` - DMs you an overview of you current bounties and their status.
⁣
The bounties change every monday at midnight and will get displayed in their respective channels. You can also sign up to get notified when that happened.
⁣
And lastly, if you have any general suggestions or ideas for new bounties, contact <@!238388130581839872>
⁣
⁣
"""
                    )

                    # send register msg and save the id
                    msg = await channel.send(embed=embed_message(
                        f'Registration',
                        f'If you want to register to the **Bounty Goblins**, react with <:register:751774620696313966> \n\n If you want to receive a notification whenever new bounties are available, react with <a:notifications:751771924866269214>'
                    ))
                    register = client.get_emoji(751774620696313966)
                    await msg.add_reaction(register)
                    notification = client.get_emoji(751771924866269214)
                    await msg.add_reaction(notification)
                    saveAsGlobalVar("register_channel_message_id", msg.id)


async def registrationMessageReactions(client, user, emoji, register_channel, register_channel_message_id):
    message = await register_channel.fetch_message(register_channel_message_id)

    register = client.get_emoji(751774620696313966)
    notification = client.get_emoji(751771924866269214)

    if emoji.id == register.id:
        await message.remove_reaction(register, user)

        # check if user is !registered in clan
        if lookupDestinyID(user.id) is None:
            embed = embed_message(
                "Registration",
                "Please register with `!register` first (not via DMs)"
            )
            await user.send(embed=embed)
            return

        # register him
        if user.id not in getBountyUserList():
            insertBountyUser(user.id)
            setLevel(1, "active", user.id)
            await updateAllExperience(client, user.id, new_register=True)
        elif getLevel("active", user.id) != 1:
            setLevel(1, "active", user.id)
            await updateAllExperience(client, user.id, new_register=True)

        # unregister him
        else:
            setLevel(0, "active", user.id)
            setLevel(0, "notifications", user.id)
            embed = embed_message(
                "See you",
                "You are no longer signed up with the **Bounty Goblins**"
                )
            await user.send(embed=embed)

    elif emoji.id == notification.id:
        await message.remove_reaction(notification, user)
        # you can only sign up if registered
        if user.id in getBountyUserList():
            if getLevel("active", user.id) == 1:
                status = getLevel("notifications", user.id)
                setLevel(0 if status == 1 else 1, "notifications", user.id)

                text = "now " if status == 0 else "no longer "
                embed = embed_message(
                    "Notifications",
                    f"You are {text}receiving notifications when new bounties are available!"
                )
                await user.send(embed=embed)

    print(f"Handled {user.display_name}'s request")


# loop though all users and refresh their experience level. Get's called once a week on sunday at midnight
async def updateExperienceLevels(client):
    for user in getBountyUserList():
        await updateAllExperience(client, user)
    print("Done updating experience")


# updates / sets all experience levels for the user
async def updateAllExperience(client, discordID, new_register=False):
    # get user info
    destinyID = lookupDestinyID(discordID)
    user = client.get_user(discordID)

    # get levels at the start, update levels and get the new ones
    pre_pve = getLevel("exp_pve", user.id)
    pre_pvp = getLevel("exp_pvp", user.id)
    pre_raids = getLevel("exp_raids", user.id)
    experiencePve(destinyID)
    experiencePvp(destinyID)
    experienceRaids(destinyID)
    post_pve = getLevel("exp_pve", user.id)
    post_pvp = getLevel("exp_pvp", user.id)
    post_raids = getLevel("exp_raids", user.id)

    embed = None
    # message the user if they newly registered
    if new_register:
        embed = embed_message(
            "Your Experience Levels",
            f"Thanks for registering with the **Bounty Goblins**. \n Depending on your experience levels, you will only get credit for completing the respective bounties in the respective categories. Also, you can only complete bounties after you signed up, whatever you did before does not count.\n\n Your experience levels are:"
        )

    # message the user if levels have changed
    elif not (pre_pve == post_pve and pre_pvp == post_pvp and pre_raids and post_raids):
        embed = embed_message(
            "Your Experience Levels",
            f"Some of your experience levels have recently changed. \n As a reminder, depending on your experience levels, you will only get credit for completing the respective bounties in the respective categories. \n\n Your experience levels are:"
        )

    try:
        embed.add_field(name="Raids Experience", value="Experienced Player" if post_raids == 1 else "New Player",
                        inline=True)
        embed.add_field(name="Pve Experience", value="Experienced Player" if post_pve == 1 else "New Player",
                        inline=True)
        embed.add_field(name="PvP Experience", value="Experienced Player" if post_pvp == 1 else "New Player",
                        inline=True)
    except AttributeError:  # meaning not new and nothing changed
        pass

    if embed:
        await user.send(embed=embed)

