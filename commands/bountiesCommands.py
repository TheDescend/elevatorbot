import asyncio
import io
import logging
import os
import pickle

import aiohttp
import discord

from commands.base_command import BaseCommand
from functions.bounties.bountiesBackend import getGlobalVar, saveAsGlobalVar, deleteFromGlobalVar, returnScore, \
    fulfillRequirements, returnLeaderboard, formatLeaderboardMessage, playerHasDoneBounty
from functions.bounties.bountiesFunctions import displayBounties, displayCompetitionBounties, bountyCompletion, \
    displayLeaderboard, updateAllExperience
from events.bountiesEvents import GenerateBounties
from functions.bounties.bountiesTournament import tournamentRegistrationMessage, tournamentChannelMessage, \
    startTournamentEvents
from functions.dataLoading import getPGCR
from functions.database import getBountyUserList, setLevel, getLevel, lookupDestinyID
from functions.formating import embed_message
from functions.persistentMessages import persistentChannelMessages
from functions.miscFunctions import hasAdminOrDevPermissions, hasMentionPermission


# --------------------------------------------------------------------------------------------
# normal user commands
class bounties(BaseCommand):
    def __init__(self):
        description = f"DM's you an overview of you current bounties and their status"
        topic = "Bounties"
        params = []
        super().__init__(description, params, topic)

    async def handle(self, params, message, mentioned_user, client):
        # check perm for other user mention, otherwise abort
        if not (await hasMentionPermission(message, mentioned_user)):
            return

        with open('functions/bounties/currentBounties.pickle', "rb") as f:
            json = pickle.load(f)

        experience_level_pve = getLevel("exp_pve", message.author.id)
        experience_level_pvp = getLevel("exp_pvp", message.author.id)
        experience_level_raids = getLevel("exp_raids", message.author.id)

        await message.author.send("This are the bounties you can still complete")

        # open http session for images later
        async with aiohttp.ClientSession() as session:
            for topic in json["bounties"].keys():
                await message.author.send(f"⁣\n⁣\n__**{topic}**__")

                for experience in json["bounties"][topic].keys():

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

                    for name in json["bounties"][topic][experience]:
                        if not playerHasDoneBounty(message.author.id, name):
                            url = json["bounties"][topic][experience][name]["url"]

                            async with session.get(url) as resp:
                                if resp.status == 200:
                                    data = io.BytesIO(await resp.read())
                                    await message.author.send(file=discord.File(data, f'Bounties-{topic}-{experience}-{name}.png'))


class leaderboard(BaseCommand):
    topics = {
        "all": ["points_bounties_raids", "points_competition_raids", "points_bounties_pve", "points_competition_pve",
                "points_bounties_pvp", "points_competition_pvp"],
        "raids": ["points_bounties_raids", "points_competition_raids"],
        "pve": ["points_bounties_pve", "points_competition_pve"],
        "pvp": ["points_bounties_pvp", "points_competition_pvp"],
        "bountiesraids": ["points_bounties_raids"],
        "bountiespve": ["points_bounties_pve"],
        "bountiespvp": ["points_bounties_pvp"],
        "competitiveraids": ["points_competition_raids"],
        "competitivepve": ["points_competition_pve"],
        "competitivepvp": ["points_competition_pvp"],
    }

    def __init__(self):
        description = f"Shows the full leaderboard for the given category"
        topic = "Bounties"
        params = [f"topic {'|'.join(list(self.topics.keys()))}"]
        super().__init__(description, params, topic)

    async def handle(self, params, message, mentioned_user, client):
        # check if topic is correct
        if params[0].lower() not in self.topics:
            await message.channel.send(embed=embed_message(
                'Error',
                f'Unrecognised category, currently supported are: \n\u200B\n`{"|".join(list(self.topics.keys()))}`'
            ))
            return

        # function to condense leaderboards
        def condense(lead_big, lead_new):
            for id, value in lead_new.items():
                if value is not None and value != 0:
                    if id in lead_big:
                        lead_big.update({id: (0 if lead_big[id] is None else lead_big[id]) + value})
                    else:
                        lead_big.update({id: value})

        # get, condense and format leaderboard
        leaderboard = {}
        for topic in self.topics[params[0].lower()]:
            condense(leaderboard, returnLeaderboard(topic))
        ranking = await formatLeaderboardMessage(client, leaderboard, user_id=mentioned_user.id)

        fancy_dict = {
            "all": "All Categories",
            "raids": "Raids",
            "pve": "PvE",
            "pvp": "PvP",
            "bountiesraids": "Normal Bounties - Raids",
            "bountiespve": "Normal Bounties - PvE",
            "bountiespvp": "Normal Bounties - PvP",
            "competitiveraids": "Competitive Bounties - Raids",
            "competitivepve": "Competitive Bounties - PvE",
            "competitivepvp": "Competitive Bounties - PvP",
        }

        await message.channel.send(embed=embed_message(
            f'Leaderboard: {fancy_dict[params[0].lower()]}',
            (f"\n".join(ranking)) if ranking else "Nobody has any points yet"
        ))
        return


class experienceLevel(BaseCommand):
    def __init__(self):
        description = f"DM's you your experience level for the Bounty Goblins"
        topic = "Bounties"
        params = []
        super().__init__(description, params, topic)

    async def handle(self, params, message, mentioned_user, client):
        # check perm for other user mention, otherwise abort
        if not (await hasMentionPermission(message, mentioned_user)):
            return

        await updateAllExperience(client, mentioned_user.id, new_register=True)


# --------------------------------------------------------------------------------------------
# admin commands
class startTournament(BaseCommand):
    def __init__(self):
        description = f"[Admin] Starts the tournament"
        topic = "Bounties"
        params = []
        super().__init__(description, params, topic)

    async def handle(self, params, message, mentioned_user, client):
        # check if user has permission to use this command
        if not await hasAdminOrDevPermissions(message):
            return

        await startTournamentEvents(client)

        # update leaderboard
        await displayLeaderboard(client)

        # delete old messages and print the default one back
        await asyncio.sleep(60 * 60)  # wait one hour before deleting annoucements and stuff
        await tournamentChannelMessage(client)


class generateTournament(BaseCommand):
    def __init__(self):
        description = f"[Admin] Generate an out of the order tournament"
        topic = "Bounties"
        params = []
        super().__init__(description, params, topic)

    async def handle(self, params, message, mentioned_user, client):
        # check if user has permission to use this command
        if not await hasAdminOrDevPermissions(message):
            return

        await tournamentRegistrationMessage(client)


class updateCompletions(BaseCommand):
    def __init__(self):
        description = f"[Admin] Updates bounty completion status"
        topic = "Bounties"
        params = []
        super().__init__(description, params, topic)

    async def handle(self, params, message, mentioned_user, client):
        # check if user has permission to use this command
        if not await hasAdminOrDevPermissions(message):
            return

        await bountyCompletion(client)


class resetLeaderboards(BaseCommand):
    def __init__(self):
        description = f'[Admin] Generate new bounties'
        topic = "Bounties"
        params = []
        super().__init__(description, params, topic)

    async def handle(self, params, message, mentioned_user, client):
        # check if user has permission to use this command
        if not await hasAdminOrDevPermissions(message):
            return

        msg = await message.channel.send("Are you sure you want to reset the entire leaderboards? That can't be undone. Type `yes` to continue or anything else to abort")

        # check the channel, user and content of the answer to double check
        def check(m):
            return m.author == message.author and m.channel == message.channel
        try:
            msg2 = await client.wait_for('message', timeout=60, check=check)
        except asyncio.TimeoutError:
            msg3 = await message.channel.send("Aborted")
        else:
            if msg2.content == "yes":
                # delete leaderboards
                for discordID in getBountyUserList(all=True):
                    setLevel(0, "points_bounties_pve", discordID)
                    setLevel(0, "points_bounties_pvp", discordID)
                    setLevel(0, "points_bounties_raids", discordID)
                    setLevel(0, "points_competition_pve", discordID)
                    setLevel(0, "points_competition_pvp", discordID)
                    setLevel(0, "points_competition_raids", discordID)

                msg4 = await message.channel.send("Leaderboards were reset")
                logging.info("Reset all leaderboards")
            else:
                msg3 = await message.channel.send("Aborted")

        await asyncio.sleep(30)
        await message.delete()
        await msg.delete()
        try:
            await msg2.delete()
        except:
            pass
        try:
            await msg3.delete()
        except:
            pass
        try:
            await msg4.delete()
        except:
            pass


class generateNewBounties(BaseCommand):
    def __init__(self):
        description = f'[Admin] Generate new bounties'
        topic = "Bounties"
        params = []
        super().__init__(description, params, topic)

    async def handle(self, params, message, mentioned_user, client):
        # check if user has permission to use this command
        if not await hasAdminOrDevPermissions(message):
            return

        gen = GenerateBounties()
        await gen.run(client)


# --------------------------------------------------------------------------------------------
# channel registration
class bountiesMakeChannelRegister(BaseCommand):
    def __init__(self):
        description = f'[dev] Admin / Dev only'
        topic = "Bounties"
        params = []
        super().__init__(description, params, topic)

    async def handle(self, params, message, mentioned_user, client):
        # check if user has permission to use this command
        if not await hasAdminOrDevPermissions(message):
            return

        deleteFromGlobalVar("register_channel_message_id")
        saveAsGlobalVar("register_channel", message.channel.id, message.guild.id)
        await persistentChannelMessages(client)


class bountiesMakeChannelTournment(BaseCommand):
    def __init__(self):
        description = f'[dev] Admin / Dev only'
        topic = "Bounties"
        params = []
        super().__init__(description, params, topic)

    async def handle(self, params, message, mentioned_user, client):
        # check if user has permission to use this command
        if not await hasAdminOrDevPermissions(message):
            return

        saveAsGlobalVar("tournament_channel", message.channel.id, message.guild.id)
        await tournamentChannelMessage(client)


class bountiesMakeChannelLeaderboard(BaseCommand):
    def __init__(self):
        description = f'[dev] Admin / Dev only'
        topic = "Bounties"
        params = []
        super().__init__(description, params, topic)

    async def handle(self, params, message, mentioned_user, client):
        # check if user has permission to use this command
        if not await hasAdminOrDevPermissions(message):
            return

        saveAsGlobalVar("leaderboard_channel", message.channel.id, message.guild.id)
        await displayLeaderboard(client, False)


class bountiesMakeChannelBounties(BaseCommand):
    def __init__(self):
        description = f'[dev] Admin / Dev only'
        topic = "Bounties"
        params = []
        super().__init__(description, params, topic)

    async def handle(self, params, message, mentioned_user, client):
        # check if user has permission to use this command
        if not await hasAdminOrDevPermissions(message):
            return

        saveAsGlobalVar("bounties_channel", message.channel.id, message.guild.id)
        await displayBounties(client)


class bountiesMakeChannelCompetitionBounties(BaseCommand):
    def __init__(self):
        description = f'[dev] Admin / Dev only'
        topic = "Bounties"
        params = []
        super().__init__(description, params, topic)

    async def handle(self, params, message, mentioned_user, client):
        # check if user has permission to use this command
        if not await hasAdminOrDevPermissions(message):
            return

        saveAsGlobalVar("competition_bounties_channel", message.channel.id, message.guild.id)
        await displayBounties(client)


# --------------------------------------------------------------------------------------------
# dev commands
class getBounties(BaseCommand):
    def __init__(self):
        description = f"[dev] Overwrites bounties"
        topic = "Bounties"
        params = []
        super().__init__(description, params, topic)

    async def handle(self, params, message, mentioned_user, client):
        # check if user has permission to use this command
        if not await hasAdminOrDevPermissions(message):
            return

        with open('functions/bounties/currentBounties.pickle', "rb") as f:
            bounties = pickle.load(f)

        with open('functions/bounties/temp.txt', "w") as f:
            f.write(str(bounties))

        await message.channel.send(file=discord.File('functions/bounties/temp.txt'))

        os.remove('functions/bounties/temp.txt')

class overwriteBounties(BaseCommand):
    def __init__(self):
        description = f"[dev] Overwrites bounties"
        topic = "Bounties"
        params = []
        super().__init__(description, params, topic)

    async def handle(self, params, message, mentioned_user, client):
        # check if user has permission to use this command
        if not await hasAdminOrDevPermissions(message):
            return

        await message.channel.send("Please upload the new json as a file (pasting will automatically do that since its big)")

        def check(m):
            return m.author == message.author and m.channel == message.channel
        try:
            msg = await client.wait_for('message', timeout=120, check=check)
        except asyncio.TimeoutError:
            await message.channel.send("You took too long")
            return

        attachment_url = msg.attachments[0].url
        async with aiohttp.ClientSession() as session:
            async with session.get(url=attachment_url) as r:
                file = await r.json()

        try:
            file = eval(file)
        except:
            await message.channel.send("Incorrect Formating")
            return

        # overwrite the old bounties
        with open('functions/bounties/currentBounties.pickle', "wb") as f:
            pickle.dump(file, f)
        # delete old bounty completion tracking pickle
        if os.path.exists('functions/bounties/playerBountyStatus.pickle'):
            os.remove('functions/bounties/playerBountyStatus.pickle')

        print("Bounties manually overridden to:")
        print(file)

        file = getGlobalVar()

        for guild in client.guilds:
            if guild.id == file["guild_id"]:
                await displayBounties(client)
                await displayCompetitionBounties(client, guild)


class testCompetitive(BaseCommand):
    def __init__(self):
        description = f"[dev] testCompetitive"
        topic = "Bounties"
        params = []
        super().__init__(description, params, topic)

    async def handle(self, params, message, mentioned_user, client):
        # check if user has permission to use this command
        if not await hasAdminOrDevPermissions(message):
            return

        """ Insert (fe.):
                {
                    "requirements": ["allowedTypes", "win", "totalKills"],
                    "allowedTypes": [2043403989],
                    "totalKills": 30,
                    "points": 1
                }
        """
        try:
            instance_id = str(params.pop(params.index(params[0])))
            activity = {
                "activityDetails": {
                    "directorActivityHash": await getPGCR(instance_id)["Response"]["activityDetails"]["directorActivityHash"],
                    "instanceId": instance_id
                }
            }

            req = " ".join(params)
            req.replace("\\n", "")
            req = " ".join(req.split())
            req = eval(req)
        except:
            await message.channel.send("Incorrect Formating")
            return

        score, _ = await returnScore(req, activity, lookupDestinyID(message.author.id))
        await message.channel.send(f"Score : {score}")


class testBounties(BaseCommand):
    def __init__(self):
        description = f"[dev] testCompetitive"
        topic = "Bounties"
        params = []
        super().__init__(description, params, topic)

    async def handle(self, params, message, mentioned_user, client):
        # check if user has permission to use this command
        if not await hasAdminOrDevPermissions(message):
            return

        """ Insert (fe.):
                {
                    "requirements": ["allowedTypes", "win", "totalKills"],
                    "allowedTypes": [2043403989],
                    "totalKills": 30,
                    "points": 1
                }
        """
        try:
            instance_id = str(params.pop(params.index(params[0])))
            activity = {
                "activityDetails": {
                    "directorActivityHash": await getPGCR(instance_id)["Response"]["activityDetails"]["directorActivityHash"],
                    "instanceId": instance_id
                }
            }

            req = " ".join(params)
            req.replace("\\n", "")
            req = " ".join(req.split())
            req = eval(req)
        except:
            await message.channel.send("Incorrect Formating")
            return

        done, index_multiple_points = await fulfillRequirements(req, activity, lookupDestinyID(message.author.id))
        await message.channel.send(f"Done: {done}")
        if index_multiple_points is not None:
            await message.channel.send(f"index_multiple_points: {index_multiple_points}")

