from commands.base_command  import BaseCommand
from functions.bounties.bountiesFunctions import displayBounties, displayCompetitionBounties, bountyCompletion, displayLeaderboard, updateAllExperience, generateBounties, saveAsGlobalVar, deleteFromGlobalVar, bountiesChannelMessage
from functions.bounties.bountiesBackend import returnLeaderboard, formatLeaderboardMessage, playerHasDoneBounty
from functions.dataLoading import getPGCR
from functions.database import getBountyUserList, setLevel, getLevel
from functions.formating import embed_message

import discord
import asyncio
import pickle
import os
import requests
import json


# --------------------------------------------------------------------------------------------
# normal user commands
class bounties(BaseCommand):
    def __init__(self):
        description = f"DM's you an overview of you current bounties and their status"
        params = []
        super().__init__(description, params)

    async def handle(self, params, message, client):
        with open('functions/bounties/currentBounties.pickle', "rb") as f:
            json = pickle.load(f)

        experience_level_pve = getLevel("exp_pve", message.author.id)
        experience_level_pvp = getLevel("exp_pvp", message.author.id)
        experience_level_raids = getLevel("exp_raids", message.author.id)

        for topic in json["bounties"].keys():
            embed = embed_message(
                topic
            )
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

                name, req = list(json["bounties"][topic][experience].items())[0]

                embed.add_field(name="✅ Done" if playerHasDoneBounty(message.author.id, name) else "Available", value=f"~~Points: **{req['points']}** - {name}~~\n⁣" if playerHasDoneBounty(message.author.id, name) else f"Points: **{req['points']}** - {name}\n⁣", inline=False)
            await message.author.send(embed=embed)


class leaderboard(BaseCommand):
    def __init__(self):
        description = f"Shows the full leaderboard for the given category"
        params = []
        super().__init__(description, params)

    async def handle(self, params, message, client):
        topics = {
            "all": ["points_bounties_raids", "points_competition_raids", "points_bounties_pve", "points_competition_pve", "points_bounties_pvp", "points_competition_pvp"],
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

        # check if message too long
        if len(params) != 1:
            await message.channel.send(embed=embed_message(
                'Error',
                f'Incorrect formatting, correct usage is: \n\u200B\n `!leaderboard <category>` \n\u200B\n Currently supported are: \n\u200B\n`{", ".join(topics)}`'
            ))
            return

        # check if topic is correct
        elif params[0].lower() not in topics:
            await message.channel.send(embed=embed_message(
                'Error',
                f'Unrecognised category, currently supported are: \n\u200B\n`{"`, `".join(topics)}`'
            ))
            return

        # function to condense leaderboards
        def condense(lead_big, lead_new):
            for id, value in lead_new.items():
                if value is not None and value != 0:
                    if id in lead_big:
                        lead_big.update({id: (0 if lead_big[id] is None else value) + value})
                    else:
                        lead_big.update({id: value})

        # get, condense and format leaderboard
        leaderboard = {}
        for topic in topics[params[0].lower()]:
            condense(leaderboard, returnLeaderboard(topic))
        ranking = await formatLeaderboardMessage(client, leaderboard, user_id=message.author.id)

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
        params = []
        super().__init__(description, params)

    async def handle(self, params, message, client):
        await updateAllExperience(client, message.author.id, new_register=True)


# --------------------------------------------------------------------------------------------
# admin commands
class updateCompletions(BaseCommand):
    def __init__(self):
        description = f"[Admin] Updates bounty completion status"
        params = []
        super().__init__(description, params)

    async def handle(self, params, message, client):
        # check if user has permission to use this command
        admin = discord.utils.get(message.guild.roles, name='Admin')
        dev = discord.utils.get(message.guild.roles, name='Developer')
        if admin not in message.author.roles and dev not in message.author.roles:
            await message.channel.send(embed=embed_message(
                'Error',
                'You are not allowed to do that'
            ))
            return

        await bountyCompletion(client)


class resetLeaderboards(BaseCommand):
    def __init__(self):
        description = f'[Admin] Generate new bounties'
        params = []
        super().__init__(description, params)

    async def handle(self, params, message, client):
        # check if user has permission to use this command
        admin = discord.utils.get(message.guild.roles, name='Admin')
        dev = discord.utils.get(message.guild.roles, name='Developer')
        if admin not in message.author.roles and dev not in message.author.roles:
            await message.channel.send(embed=embed_message(
                'Error',
                'You are not allowed to do that'
            ))
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
        params = []
        super().__init__(description, params)

    async def handle(self, params, message, client):
        # check if user has permission to use this command
        admin = discord.utils.get(message.guild.roles, name='Admin')
        dev = discord.utils.get(message.guild.roles, name='Developer')
        if admin not in message.author.roles and dev not in message.author.roles:
            await message.channel.send(embed=embed_message(
                'Error',
                'You are not allowed to do that'
            ))
            return

        await generateBounties(client)


# --------------------------------------------------------------------------------------------
# channel registration
class bountiesMakeChannelRegister(BaseCommand):
    def __init__(self):
        description = f'[dev] Admin / Dev only'
        params = []
        super().__init__(description, params)

    async def handle(self, params, message, client):
        # check if user has permission to use this command
        admin = discord.utils.get(message.guild.roles, name='Admin')
        dev = discord.utils.get(message.guild.roles, name='Developer')
        if admin not in message.author.roles and dev not in message.author.roles:
            await message.channel.send(embed=embed_message(
                'Error',
                'You are not allowed to do that'
            ))
            return

        deleteFromGlobalVar("register_channel_message_id")
        saveAsGlobalVar("register_channel", message.channel.id, message.guild.id)
        await bountiesChannelMessage(client)


class bountiesMakeChannelLeaderboard(BaseCommand):
    def __init__(self):
        description = f'[dev] Admin / Dev only'
        params = []
        super().__init__(description, params)

    async def handle(self, params, message, client):
        # check if user has permission to use this command
        admin = discord.utils.get(message.guild.roles, name='Admin')
        dev = discord.utils.get(message.guild.roles, name='Developer')
        if admin not in message.author.roles and dev not in message.author.roles:
            await message.channel.send(embed=embed_message(
                'Error',
                'You are not allowed to do that'
            ))
            return

        # todo
        saveAsGlobalVar("leaderboard_channel", message.channel.id, message.guild.id)
        await displayLeaderboard(client, False)


class bountiesMakeChannelBounties(BaseCommand):
    def __init__(self):
        description = f'[dev] Admin / Dev only'
        params = []
        super().__init__(description, params)

    async def handle(self, params, message, client):
        # check if user has permission to use this command
        admin = discord.utils.get(message.guild.roles, name='Admin')
        dev = discord.utils.get(message.guild.roles, name='Developer')
        if admin not in message.author.roles and dev not in message.author.roles:
            await message.channel.send(embed=embed_message(
                'Error',
                'You are not allowed to do that'
            ))
            return

        saveAsGlobalVar("bounties_channel", message.channel.id, message.guild.id)
        await displayBounties(client)


class bountiesMakeChannelCompetitionBounties(BaseCommand):
    def __init__(self):
        description = f'[dev] Admin / Dev only'
        params = []
        super().__init__(description, params)

    async def handle(self, params, message, client):
        # check if user has permission to use this command
        admin = discord.utils.get(message.guild.roles, name='Admin')
        dev = discord.utils.get(message.guild.roles, name='Developer')
        if admin not in message.author.roles and dev not in message.author.roles:
            await message.channel.send(embed=embed_message(
                'Error',
                'You are not allowed to do that'
            ))
            return

        saveAsGlobalVar("competition_bounties_channel", message.channel.id, message.guild.id)
        await displayBounties(client)


# --------------------------------------------------------------------------------------------
# dev commands
class getBounties(BaseCommand):
    def __init__(self):
        description = f"[dev] Overwrites bounties"
        params = []
        super().__init__(description, params)

    async def handle(self, params, message, client):
        # check if user has permission to use this command
        admin = discord.utils.get(message.guild.roles, name='Admin')
        dev = discord.utils.get(message.guild.roles, name='Developer')
        if admin not in message.author.roles and dev not in message.author.roles:
            await message.channel.send(embed=embed_message(
                'Error',
                'You are not allowed to do that'
            ))
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
        params = []
        super().__init__(description, params)

    async def handle(self, params, message, client):
        # check if user has permission to use this command
        admin = discord.utils.get(message.guild.roles, name='Admin')
        dev = discord.utils.get(message.guild.roles, name='Developer')
        if admin not in message.author.roles and dev not in message.author.roles:
            await message.channel.send(embed=embed_message(
                'Error',
                'You are not allowed to do that'
            ))
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
        file = requests.get(attachment_url).text

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

        with open('functions/bounties/channelIDs.pickle', "rb") as f:
            file = pickle.load(f)
        for guild in client.guilds:
            if guild.id == file["guild_id"]:
                await displayBounties(client)
                await displayCompetitionBounties(client, guild)
