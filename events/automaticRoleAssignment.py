import datetime
from itertools import compress

import discord

from events.backgroundTasks import updateActivityDB
from events.base_event import BaseEvent
from database.database import lookupDiscordID, lookupDestinyID
from functions.network import getJSONfromURL, handleAndReturnToken
from functions.persistentMessages import botStatus
from functions.roleLookup import assignRolesToUser, removeRolesFromUser, getPlayerRoles
from static.config import CLANID, BOTDEVCHANNELID
from static.globals import *


class AutomaticRoleAssignment(BaseEvent):
    """Will automatically update the roles"""
    def __init__(self):
        # Set the interval for this event
        dow_day_of_week = "*"
        dow_hour = 0
        dow_minute = 0
        super().__init__(scheduler_type="cron", dow_day_of_week=dow_day_of_week, dow_hour=dow_hour, dow_minute=dow_minute)

    async def run(self, client):
        async def updateUser(discordUser):
            if discordUser.bot:
                return None, None, None

            destinyID = await lookupDestinyID(discordUser.id)
            if not destinyID:
                return None, None, None

            # gets the roles of the specific player and assigns/removes them
            newRoles, removeRoles = await getPlayerRoles(destinyID, [role.name for role in discordUser.roles]) #the list of roles may be used to not check existing roles

            return discordUser, newRoles, removeRoles

        print('Running the automatic role assignment...')

        # acquires the newtonslab channel from the descend server and notifies about starting
        newtonslab = client.get_channel(BOTDEVCHANNELID)
        guild = newtonslab.guild

        async with newtonslab.typing():
            update = updateActivityDB()
            await update.run(client)

        news = []
        async for member in guild.fetch_members():
            # only allow people who accepted the rules
            if not member.pending:
                news.append(await updateUser(member))

        newstext = ''
        for discordUser, newRoles, removeRoles in news:
            if not discordUser:
                continue
            is_assigned = await assignRolesToUser(newRoles, discordUser, guild)
            await removeRolesFromUser(removeRoles, discordUser, guild)
            existingRoles = [er.name for er in discordUser.roles]
            addBools = [nr not in existingRoles for nr in newRoles]
            removeBools = [rr in existingRoles for rr in removeRoles]

            addrls = list(compress(newRoles, addBools))
            removerls = list(compress(removeRoles, removeBools))

            if addrls or removerls:
                if is_assigned:
                    newstext += f'Updated player {discordUser.mention} by adding `{", ".join(addrls or ["nothing"])}` and removing `{", ".join(removerls or ["nothing"])}`\n'

        if newstext:
            await newtonslab.send(newstext)

        # update the status
        await botStatus(client, "Achievement Role Update", datetime.datetime.now(tz=datetime.timezone.utc))


class AutoRegisteredRole(BaseEvent):
    """Will automatically update the registration and clan roles"""
    def __init__(self):
        interval_minutes = 30  # Set the interval for this event
        super().__init__(scheduler_type="interval", interval_minutes=interval_minutes)

    async def run(self, client):
        # get all clan members discordID
        memberlist = []
        for member in (await getJSONfromURL(f"https://www.bungie.net/Platform/GroupV2/{CLANID}/Members/"))["Response"]["results"]:
            destinyID = int(member["destinyUserInfo"]["membershipId"])
            discordID = await lookupDiscordID(destinyID)
            if discordID is not None:
                memberlist.append(discordID)

        if not len(memberlist) > 5:
            #error.log
            print('something broke at AutoRegisteredRole, clansize <= 5')
            return

        for guild in client.guilds:
            newtonsLab = discord.utils.get(guild.channels, id=BOTDEVCHANNELID)

            clan_role = discord.utils.get(guild.roles, id=clan_role_id)
            member_role = discord.utils.get(guild.roles, id=member_role_id)

            for member in guild.members:
                # only allow people who accepted the rules
                if member.pending:
                    continue
                # dont do that for bots
                if member.bot:
                    continue

                # add "Registered" if they have a token but not the role
                if (await handleAndReturnToken(member.id))["result"]:
                    if discord.utils.get(guild.roles, id=not_registered_role_id) in member.roles:
                        await removeRolesFromUser([not_registered_role_id], member, guild)
                    await assignRolesToUser([registered_role_id], member, guild)
                # add "Not Registered" if they have no token but the role (after unregister)
                else:
                    if discord.utils.get(guild.roles, id=registered_role_id) in member.roles:
                        await removeRolesFromUser([registered_role_id], member, guild)
                    await assignRolesToUser([not_registered_role_id], member, guild)

                # add clan role if user is in clan, has token, is member and doesn't have clan role
                if clan_role not in member.roles:
                    if (member_role in member.roles) and (member.id in memberlist):
                        await assignRolesToUser([clan_role_id], member, guild)
                        if newtonsLab:
                            await newtonsLab.send(f"Added Descend role to {member.mention}")

                # Remove clan role it if no longer in clan or not member or no token
                if clan_role in member.roles:
                    if (member_role not in member.roles) or (member.id not in memberlist):
                        await removeRolesFromUser([clan_role_id], member, guild)
                        if newtonsLab:
                            await newtonsLab.send(f"Removed Descend role from {member.mention}")


        # update the status
        await botStatus(client, "Member Role Update", datetime.datetime.now(tz=datetime.timezone.utc))
