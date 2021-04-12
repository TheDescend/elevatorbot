# import datetime
# import io
# import os
# import pickle
# import random
#
# import aiohttp
# import discord
# from PIL import Image, ImageDraw, ImageFont
#
# from functions.bounties.bountiesBackend import saveAsGlobalVar, getGlobalVar, addPoints, formatLeaderboardMessage, \
#     returnLeaderboard, getCompetitionBountiesLeaderboards, changeCompetitionBountiesLeaderboards, experiencePvp, \
#     experiencePve, experienceRaids, threadingCompetitionBounties, threadingBounties
# from functions.bounties.boutiesBountyRequirements import possibleWeaponsKinetic, possibleWeaponsEnergy, possibleWeaponsPower
# from functions.dataLoading import returnManifestInfo, getPlayersPastActivities
# from functions.database import lookupDestinyID
# from functions.formating import embed_message
# from functions.miscFunctions import checkIfUserIsRegistered
# from static.dict import activityRaidHash, speedrunActivitiesRaids, weaponTypeKinetic, weaponTypeEnergy, weaponTypePower
#
#
# # randomly generate bounties. One per topic for both of the lists
#
#
# # do the random selection and the extraText formating
# async def bountiesFormatting(client, topic, json, amount_of_bounties=1):
#     ret = {}
#
#     # generate the specified amount of bounties
#     for _ in range(amount_of_bounties):
#         key, value = random.choice(list(json.items()))
#
#         # pop that, so it can't get chosen randomly twice
#         json.pop(key)
#
#         # if "randomActivity" is present, get a random activity from the list and delete "randomActivity" so it doesn't take up space anymore
#         if "randomActivity" in value:
#             value["allowedActivities"] = random.choice(value.pop("randomActivity"))
#             value["requirements"].pop(value["requirements"].index("randomActivity"))
#             value["requirements"].append("allowedActivities")
#
#         # if "customLoadout" is present, get a random loadout from the list
#         if "customLoadout" in value["requirements"]:
#             weaponKinetic = random.choice(possibleWeaponsKinetic)
#             weaponEnergy = random.choice(possibleWeaponsEnergy)
#             weaponPower = random.choice(possibleWeaponsPower)
#
#             value["customLoadout"] = {
#                 weaponTypeKinetic: weaponKinetic,
#                 weaponTypeEnergy: weaponEnergy,
#                 weaponTypePower: weaponPower
#             }
#
#         # if "extraText" is present, process that
#         if "extraText" in value:
#             if "allowedActivities" in value["requirements"]:
#                 ret_dummy = await returnManifestInfo("DestinyActivityDefinition", value["allowedActivities"][0])
#                 activity_name = ret_dummy["Response"]["displayProperties"]["name"]
#
#                 # removing extra characters
#                 activity_name = activity_name.replace(": Level 55", "")
#                 activity_name = activity_name.replace(": Normal", "")
#
#                 key = key.replace("?", activity_name)
#
#             if "customLoadout" in value["requirements"]:
#                 value["extraText"] = value["extraText"].replace("?", f"{weaponKinetic}")
#                 value["extraText"] = value["extraText"].replace("%", f"{weaponEnergy}")
#                 value["extraText"] = value["extraText"].replace("&", f"{weaponPower}")
#
#             if "speedrun" in value["requirements"]:
#                 if "allowedTypes" in value["requirements"]:
#                     if activityRaidHash == value["allowedTypes"]:
#                         for activities in speedrunActivitiesRaids:
#                             ret_dummy = await returnManifestInfo("DestinyActivityDefinition", activities[0])
#                             activity_name = ret_dummy["Response"]["displayProperties"]["name"]
#
#                             # removing extra characters
#                             activity_name = activity_name.replace(": Level 55", "")
#                             activity_name = activity_name.replace(": Normal", "")
#
#                             value["extraText"] += f"{activity_name}: {round(speedrunActivitiesRaids[activities] / 60, 2)}min (2x WR)\n"
#
#         # put the text on and image and save the url
#         key, value = await makeAndUploadBountyImage(client, topic, key, value)
#
#         # update return dict
#         ret.update({key: value})
#
#     return ret
#
#
# # puts the text on the image and then uploads it and saves the url
# async def makeAndUploadBountyImage(client, topic, key, value):
#     # edit the name to not be too long
#     l = 25
#     name = key
#     small_font = False
#     if len(key) > 2*l:
#         l = 29
#         small_font = True
#     if len(key) > l:
#         splits = key.split(" ")
#         name = []
#         name_holder = ""
#         while splits:
#             while len(name_holder + f" {splits[0]}") <= l:
#                 name_holder += f" {splits.pop(0)}"
#                 if not splits:
#                     break
#             name.append(name_holder)
#             name_holder = ""
#
#     # set description for later use
#     desc = value["extraText"] if "extraText" in value else ""
#
#     # set points for later use
#     points = value['points']
#     if isinstance(value['points'], list):
#         if "lowman" in value["requirements"]:
#             points = []
#             for x, y in zip(value["lowman"], value["points"]):
#                 points.append(f"{y} ({x} Man) ")
#             points = "/ ".join(points)
#
#     # get image editing tools
#     image = Image.open(f"functions/bounties/template/{topic}.png")
#     draw = ImageDraw.Draw(image)
#     font_name = ImageFont.truetype("functions/bounties/template/font/NHaasGroteskTXPro-75Bd.otf", 60 if small_font else 64)
#     font_desc = ImageFont.truetype("functions/bounties/template/font/NHaasGroteskTXPro-55Rg.otf", 50)
#     font_points = ImageFont.truetype("functions/bounties/template/font/NHaasGroteskTXPro-65Md.otf", 46)
#
#     # edit the image
#     draw.text((230, 20 if isinstance(name, list) else 50), "\n".join(name) if isinstance(name, list) else name, font=font_name, fill=(255, 255, 255))
#     draw.text((240, 220), desc, font=font_desc, fill=(128, 128, 128))
#     draw.text((300, 496), f"Points: {points}", font=font_points, fill=(91, 166, 107))
#
#     # upload the image
#     imagespamchannel = client.get_channel(761278600103723018)
#     with io.BytesIO() as image_binary:
#         image.save(image_binary, 'PNG')
#         image_binary.seek(0)
#         msg = await imagespamchannel.send(file=discord.File(fp=image_binary, filename='image.png'))
#
#     # save the image url
#     value['url'] = msg.attachments[0].url
#
#     return key, value
#
#
# # awards points to whoever has the most points. Can be multiple people if tied
# async def awardCompetitionBountiesPoints(client):
#     # load current bounties
#     if os.path.exists('functions/bounties/currentBounties.pickle'):
#         with open('functions/bounties/currentBounties.pickle', "rb+") as f:
#             bountydict = pickle.load(f)
#             if "competition_bounties" in bountydict.keys():
#                 bounties = bountydict["competition_bounties"]
#
#         # load leaderboards
#         leaderboards = getCompetitionBountiesLeaderboards()
#
#         # loop through topic, then though users
#         for topic in leaderboards:
#             last_score = None
#             for discordID in leaderboards[topic]:
#                 # also award the points should multiple people have the same score
#                 if (last_score != leaderboards[topic][discordID]) and last_score is not None:
#                     break
#
#                 # award the points in the respective categories
#                 last_score = leaderboards[topic][discordID]
#                 name = list(bounties[topic].keys())[0]
#                 addPoints(discordID, bounties[topic][name], name, f"points_competition_{topic.lower()}")
#
#         # update display
#         await displayLeaderboard(client)
#
#         # delete now old leaderboards
#         if os.path.exists('functions/bounties/competitionBountiesLeaderboards.pickle'):
#             os.remove('functions/bounties/competitionBountiesLeaderboards.pickle')
#
#
# # print the bounties in their respective channels
# async def displayBounties(client):
#     # load bounties
#     with open('functions/bounties/currentBounties.pickle', "rb") as f:
#         json = pickle.load(f)
#
#     # get channel and guild id
#     file = getGlobalVar()
#
#     # get the users that signed up for notifications
#     text = ["⁣"]    # so that it still works even with nobody signed up
#     for discordID in getBountyUserList():
#         if getLevel("notifications", discordID) == 1:
#             text.append(f"<@{discordID}>")
#
#     for guild in client.guilds:
#         if guild.id == file["guild_id"]:
#             # open http session for images later
#             async with aiohttp.ClientSession() as session:
#                 # clean channels and call the actual print function
#                 if "bounties_channel" in file:
#                     bounties_channel = discord.utils.get(guild.channels, id=file["bounties_channel"])
#                     await bounties_channel.purge(limit=100)
#                     await bounties_channel.send(f"**Tip:** You earn 10% more points if you complete bounties with other people in this discord!")
#
#                     # loop though topics
#                     for topic in json["bounties"].keys():
#                         await bounties_channel.send(f"⁣\n⁣\n__**{topic}**__")
#
#                         # loop though experience
#                         for experience in json["bounties"][topic].keys():
#                             await bounties_channel.send(f"**{experience}**")
#
#                             # loop though bounties
#                             for name in json["bounties"][topic][experience]:
#                                 url = json["bounties"][topic][experience][name]["url"]
#
#                                 async with session.get(url) as resp:
#                                     if resp.status == 200:
#                                         data = io.BytesIO(await resp.read())
#                                         await bounties_channel.send(file=discord.File(data, f'Bounties-{topic}-{experience}-{name}.png'))
#
#                     # ping users
#                     msg = await bounties_channel.send(" ".join(text))
#                     await msg.delete()
#
#                     print("Updated bounty display")
#
#             if "competition_bounties_channel" in file:
#                 await displayCompetitionBounties(client, guild)
#
#                 # ping users
#                 msg = await discord.utils.get(guild.channels, id=file["competition_bounties_channel"]).send(" ".join(text))
#                 await msg.delete()
#
#             print("Done updating displays")
#
#
# async def displayCompetitionBounties(client, guild, message=None):
#     # load channel ids
#     file = getGlobalVar()
#
#     # load bounties
#     with open('functions/bounties/currentBounties.pickle', "rb") as f:
#         json = pickle.load(f)
#
#     # load leaderboards
#     leaderboards = getCompetitionBountiesLeaderboards()
#
#     # get channel id and clear channel
#     competition_bounties_channel = discord.utils.get(guild.channels, id=file["competition_bounties_channel"])
#     if not message:
#         await competition_bounties_channel.purge(limit=100)
#
#     # open http session for images later
#     async with aiohttp.ClientSession() as session:
#         # loop though topics
#         for topic in json["competition_bounties"].keys():
#             name, req = list(json["competition_bounties"][topic].items())[0]
#             url = req["url"]
#
#             if not message:
#                 await competition_bounties_channel.send(f"__**{topic}**__")
#
#                 async with session.get(url) as resp:
#                     if resp.status == 200:
#                         data = io.BytesIO(await resp.read())
#                         await competition_bounties_channel.send(file=discord.File(data, f'CBounties-{topic}-{name}.png'))
#
#             # read the current leaderboard and display the top x = 10 players
#             ranking = []
#             try:
#                 i = 1
#                 for discordID, value in leaderboards[topic].items():
#                     leaderboarduser = client.get_user(discordID)
#                     if leaderboarduser:
#                         ranking.append(str(i) + ") **" + leaderboarduser.display_name + "** _(Score: " + str(value) + ")_")
#                         # break after x entries
#                         i += 1
#                         if i > 10:
#                             break
#                     else:
#                         print(f'User with ID {discordID} in competition bounties, but not found')
#             except KeyError:
#                 pass
#
#             embed = embed_message(
#                 "Current Leaderboard",
#                 f"\n".join(ranking) if ranking else "Nobody has completed this yet"
#             )
#
#             # edit msg if given one, otherwise create a new one and save the id
#             if message:
#                 # gets the msg object related to the current topic in the competition_bounties_channel
#                 if channel := discord.utils.get(guild.channels, id=file["competition_bounties_channel"]):
#                     message = await channel.fetch_message(file[f"competition_bounties_channel_{topic.lower()}_message_id"])
#                     await message.edit(embed=embed)
#             else:
#                 msg = await competition_bounties_channel.send(embed=embed)
#                 saveAsGlobalVar(f"competition_bounties_channel_{topic.lower()}_message_id", msg.id)
#
#             # send spacer message
#             if not message:
#                 await competition_bounties_channel.send(f"⁣\n⁣\n")
#
#     #print("Updated competition bounty display")
#
#
# # checks if any player has completed a bounty
# async def bountyCompletion(client):
#     current_time = datetime.datetime.now()
#
#     # load bounties
#     with open('functions/bounties/currentBounties.pickle', "rb") as f:
#         bounties = pickle.load(f)
#     cutoff = datetime.datetime.strptime(bounties["time"], "%Y-%m-%dT%H:%M:%SZ")
#
#     # load channel ids
#     file = getGlobalVar()
#     for guild in client.guilds:
#         if guild.id == file["guild_id"]:
#             break
#
#     # create leaderboard dict for competitive bounties
#     leaderboard = {}
#     sort_by = {}
#     for topic in bounties["competition_bounties"]:
#         leaderboard[topic] = {}
#         sort_by[topic] = True
#
#     # loop though all registered users
#     for discordID in getBountyUserList():
#         # get user info
#         destinyID = lookupDestinyID(discordID)
#         experience_level_pve = getLevel("exp_pve", discordID)
#         experience_level_pvp = getLevel("exp_pvp", discordID)
#         experience_level_raids = getLevel("exp_raids", discordID)
#
#         # loop though activities
#         async for activity in getPlayersPastActivities(destinyID, mode=0):
#             # only look at activities younger than the cutoff date
#             if datetime.datetime.strptime(activity["period"], "%Y-%m-%dT%H:%M:%SZ") < cutoff:
#                 break
#
#             # checking normal bounties
#             await threadingBounties(activity, bounties["bounties"], destinyID, discordID, experience_level_pve, experience_level_pvp, experience_level_raids)
#
#             # checking competitive bounties
#             await threadingCompetitionBounties(activity, bounties["competition_bounties"], destinyID, discordID, leaderboard, sort_by)
#
#     #print("Done checking all the users")
#
#     # update the leaderboard file
#     for topic in leaderboard:
#         changeCompetitionBountiesLeaderboards(topic, leaderboard[topic], sort_by[topic])
#
#     # display the new leaderboards
#     await displayCompetitionBounties(client, guild, message=True)
#
#     # update the big leaderboard
#     await displayLeaderboard(client)
#
#     # overwrite the old time, so that one activity doesn't get checked over and over again
#     bounties["time"] = str(current_time)
#     with open('functions/bounties/currentBounties.pickle', "wb") as f:
#         pickle.dump(bounties, f)
#
#
# # updates the leaderboard display
# async def displayLeaderboard(client, use_old_message=True):
#     # function to condense leaderboards
#     def condense(lead_big, lead_new):
#         for id, value in lead_new.items():
#             if value is not None and value != 0:
#                 if id in lead_big:
#                     lead_big.update({id: (0 if lead_big[id] is None else lead_big[id]) + value})
#                 else:
#                     lead_big.update({id: value})
#
#     # get current leaderboards and condense them into one
#     leaderboard = {}
#     condense(leaderboard, returnLeaderboard("points_bounties_raids"))
#     condense(leaderboard, returnLeaderboard("points_bounties_pve"))
#     condense(leaderboard, returnLeaderboard("points_bounties_pvp"))
#     condense(leaderboard, returnLeaderboard("points_competition_raids"))
#     condense(leaderboard, returnLeaderboard("points_competition_pve"))
#     condense(leaderboard, returnLeaderboard("points_competition_pvp"))
#
#     # format that
#     ranking = await formatLeaderboardMessage(client, leaderboard, limit=50)
#
#     # load ids
#     file = getGlobalVar()
#
#     # try to get the leaderboard message id, else make a new message
#     message_id = None
#     try:
#         message_id = file["leaderboard_channel_message_id"]
#     except:
#         pass
#
#     for guild in client.guilds:
#         if guild.id == file["guild_id"]:
#
#             # get the channel id
#             competition_bounties_channel = discord.utils.get(guild.channels, id=file["leaderboard_channel"])
#
#             embed = embed_message(
#                 "Leaderboard",
#                 (f"\n".join(ranking)) if ranking else "Nobody has any points yet",
#                 footer="This leaderboard will update every ~30 minutes"
#             )
#
#             if message_id and use_old_message and (channel := discord.utils.get(
#                         guild.channels,
#                         id=file["leaderboard_channel"]
#                         )):
#                 # get the leaderboard msg object
#                 message = await channel.fetch_message(file["leaderboard_channel_message_id"])
#
#                 await message.edit(embed=embed)
#             else:
#                 await competition_bounties_channel.purge(limit=100)
#                 msg = await competition_bounties_channel.send(embed=embed)
#                 saveAsGlobalVar("leaderboard_channel_message_id", msg.id)
#
#     #print("Updated Leaderboard")
#
#
# async def registrationMessageReactions(client, user, emoji, register_channel, register_channel_message_id):
#     message = await register_channel.fetch_message(register_channel_message_id)
#
#     register = client.get_emoji(754928322403631216)
#     notification = client.get_emoji(754946724237148220)
#
#     if emoji.id == register.id:
#         await message.remove_reaction(register, user)
#
#         # check if user is @registered
#         if not await checkIfUserIsRegistered(user):
#             return
#
#         # register him
#         if user.id not in getBountyUserList():
#             insertBountyUser(user.id)
#             setLevel(1, "active", user.id)
#             await updateAllExperience(client, user.id, new_register=True)
#         elif getLevel("active", user.id) != 1:
#             setLevel(1, "active", user.id)
#             await updateAllExperience(client, user.id, new_register=True)
#
#         # unregister him
#         else:
#             setLevel(0, "active", user.id)
#             setLevel(0, "notifications", user.id)
#             embed = embed_message(
#                 "See you",
#                 "You are no longer signed up with the **Bounty Goblins**"
#                 )
#             await user.send(embed=embed)
#
#     elif emoji.id == notification.id:
#         await message.remove_reaction(notification, user)
#         # you can only sign up if registered
#         if user.id in getBountyUserList():
#             if getLevel("active", user.id) == 1:
#                 status = getLevel("notifications", user.id)
#                 setLevel(0 if status == 1 else 1, "notifications", user.id)
#
#                 text = "now " if status == 0 else "no longer "
#                 embed = embed_message(
#                     "Notifications",
#                     f"You are {text}receiving notifications when new bounties are available!"
#                 )
#                 await user.send(embed=embed)
#
#     print(f"Handled {user.display_name}'s request")
#
#
# # loop though all users and refresh their experience level. Get's called once a week on sunday at midnight
#
#
# # updates / sets all experience levels for the user
# async def updateAllExperience(client, discordID, new_register=False):
#     # get user info
#     destinyID = lookupDestinyID(discordID)
#     user = client.get_user(discordID)
#
#     # get levels at the start, update levels and get the new ones
#     pre_pve = getLevel("exp_pve", user.id)
#     pre_pvp = getLevel("exp_pvp", user.id)
#     pre_raids = getLevel("exp_raids", user.id)
#     await experiencePve(destinyID)
#     await experiencePvp(destinyID)
#     await experienceRaids(destinyID)
#     post_pve = getLevel("exp_pve", user.id)
#     post_pvp = getLevel("exp_pvp", user.id)
#     post_raids = getLevel("exp_raids", user.id)
#
#     embed = None
#     # message the user if they newly registered
#     if new_register:
#         embed = embed_message(
#             "Your Experience Levels",
#             f"Thanks for registering with the **Bounty Goblins**. \n Depending on your experience levels, you will only get credit for completing the respective bounties in the respective categories. Also, you can only complete bounties after you signed up, whatever you did before does not count.\n\n Your experience levels are:"
#         )
#
#     # message the user if levels have changed
#     elif not (pre_pve == post_pve and pre_pvp == post_pvp and pre_raids and post_raids):
#         embed = embed_message(
#             "Your Experience Levels",
#             f"Some of your experience levels have recently changed. \n As a reminder, depending on your experience levels, you will only get credit for completing the respective bounties in the respective categories. \n\n Your experience levels are:"
#         )
#
#     try:
#         embed.add_field(name="Raids Experience", value="Experienced Player" if post_raids == 1 else "New Player",
#                         inline=True)
#         embed.add_field(name="Pve Experience", value="Experienced Player" if post_pve == 1 else "New Player",
#                         inline=True)
#         embed.add_field(name="PvP Experience", value="Experienced Player" if post_pvp == 1 else "New Player",
#                         inline=True)
#     except AttributeError:  # meaning not new and nothing changed
#         pass
#
#     if embed:
#         await user.send(embed=embed)
#
