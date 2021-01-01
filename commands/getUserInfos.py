import discord
from discord.ext import commands

from commands.base_command import BaseCommand
from functions.database import lookupDestinyID, lookupDiscordID
from functions.formating import embed_message
from functions.network import getJSONfromURL
from static.dict import clanids

class getDestinyID(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[dev] check a user's destinyID"
        params = ['User']
        topic = "Registration"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        try:
            ctx = await client.get_context(message)
            discordUser = await commands.MemberConverter().convert(ctx, params[0])
        except:
            await message.channel.send(f'User not found')
        if not discordUser:
            await message.channel.send(f'Unknown User {discordID}')
        print(f'{discordID} with {lookupDestinyID(discordID)}')
        await message.channel.send(f'{discordUser.name} has destinyID {lookupDestinyID(discordID)}')

class getDiscordDate(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Check your join-datetime of the discord server"
        params = []
        topic = "Registration"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        discordMember = message.author
        await message.channel.send(f'{discordMember.mention} joined at {discordMember.joined_at.strftime("%d.%m.%Y, %H:%M")}')
        


class getDiscordID(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[dev] check a user's discordID by destinyID"
        params = ['User']
        topic = "Registration"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        destinyID = int(params[0])
        print(f'{destinyID} with {lookupDiscordID(destinyID)}')
        await message.channel.send(f'{destinyID} has discordID {lookupDiscordID(destinyID)}')

class getDiscordFuzzy(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[dev] check a user's discordID by destinyID"
        params = ['partial name']
        topic = "Registration"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        partialName = " ".join(params)
        clansearch = []
        for clanid in clanids:
            returnjson = await getJSONfromURL(f"https://www.bungie.net/Platform/GroupV2/{clanid}/Members?nameSearch={partialName}")
            clansearch.append(returnjson)

        embed = embed_message(
            f'Possible matches for {partialName}'
        )

        for result in clansearch:
            resp = result['Response']
            if not resp['results']:
                await message.channel.send(embed=embed_message(
                    f'Possible matches for {partialName}',
                    "No matches found"
                ))
                return

            i = 0
            for user in resp['results']:
                i += 1
                steam_name = user['destinyUserInfo']['LastSeenDisplayName']
                bungie_name = user['bungieNetUserInfo']['displayName']
                destinyID = user['destinyUserInfo']['membershipId']
                discordID = lookupDiscordID(destinyID)
                embed.add_field(name=f"Option {i}", value=f"Discord - <@{discordID}>\nSteamName - {steam_name}\nBungieName - {bungie_name}", inline=False)

        await message.channel.send(embed=embed)
