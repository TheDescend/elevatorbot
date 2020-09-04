from commands.base_command  import BaseCommand
from functions.bounties.bountiesFunctions import generateBounties, saveAsGlobalVar, deleteFromGlobalVar, bountiesChannelMessage, displayBounties
from functions.bounties.bountiesBackend import experiencePvp
from functions.database import getAllDiscordMemberDestinyIDs
from functions.formating import embed_message

import discord
import asyncio


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

        deleteFromGlobalVar("leaderboard_channel_message_id")
        saveAsGlobalVar("leaderboard_channel", message.channel.id, message.guild.id)
        await bountiesChannelMessage(client)


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
