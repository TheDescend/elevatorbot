from commands.base_command  import BaseCommand
from functions.bounties.bountiesFunctions import displayLeaderboard, updateAllExperience, generateBounties, saveAsGlobalVar, deleteFromGlobalVar, bountiesChannelMessage, displayBounties
from functions.bounties.bountiesBackend import returnLeaderboard, formatLeaderboardMessage
from functions.database import getAllDiscordMemberDestinyIDs
from functions.formating import embed_message

import discord
import asyncio


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
                if value is not None:
                    if id in lead_big:
                        lead_big.update({id: (0 if lead_big[id] is None else value) + value})
                    else:
                        lead_big.update({id: value})

        # get, condense and format leaderboard
        leaderboard = {}
        for topic in topics[params[0].lower()]:
            condense(leaderboard, returnLeaderboard(topic))
        ranking = await formatLeaderboardMessage(client, leaderboard, message.author.id)

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
                # todo delete leaderboard
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

        generateBounties(client)


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


# class bountiesMakeChannelTournament(BaseCommand):
#     def __init__(self):
#         description = f'[dev] Admin / Dev only'
#         params = []
#         super().__init__(description, params)
#
#     async def handle(self, params, message, client):
#         saveAsGlobalVar("tournament_channel", message.channel.id, message.guild.id)
#         await message.channel.send("Done!")
