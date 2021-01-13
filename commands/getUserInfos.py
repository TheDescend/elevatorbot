import discord
from discord.ext import commands

from commands.base_command import BaseCommand
from functions.dataLoading import getProfile
from functions.database import lookupDestinyID, lookupDiscordID, lookupSystem, getToken
from functions.formating import embed_message
from functions.miscFunctions import hasAdminOrDevPermissions
from functions.network import getJSONfromURL
from static.dict import clanids


class getDiscordDate(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Check your join-datetime of the discord server"
        params = []
        topic = "Registration"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        await message.channel.send(f'{mentioned_user.mention} joined at {mentioned_user.joined_at.strftime("%d.%m.%Y, %H:%M")}')


class getUserInfo(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[dev] check a user's infos"
        params = []
        topic = "Registration"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        # check if user has permission to use this command
        if not await hasAdminOrDevPermissions(message):
            return

        discordID = mentioned_user.id
        destinyID = lookupDestinyID(discordID)

        await message.channel.send(embed=embed_message(
            f'DB infos for {mentioned_user.name}',
            f"""DiscordID - `{discordID}` \nDestinyID: `{destinyID}` \nSystem - `{lookupSystem(destinyID)}` \nSteamName - `{(await getProfile(destinyID, 100))["profile"]["data"]["userInfo"]["displayName"]}` \nHasToken - `{bool(getToken(discordID))}`"""
        ))


class getDiscordFuzzy(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[dev] check a user's discordID by destinyID"
        params = ['partial name']
        topic = "Registration"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
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
            for guy in resp['results']:
                i += 1
                steam_name = guy['destinyUserInfo']['LastSeenDisplayName']
                bungie_name = guy['bungieNetUserInfo']['displayName']
                destinyID = guy['destinyUserInfo']['membershipId']
                discordID = lookupDiscordID(destinyID)
                embed.add_field(name=f"Option {i}", value=f"Discord - <@{discordID}>\nSteamName - {steam_name}\nBungieName - {bungie_name}", inline=False)

        await message.channel.send(embed=embed)
