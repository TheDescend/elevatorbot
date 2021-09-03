import asyncio
import datetime
from typing import Optional

import discord

from ElevatorBot.database.database import lookupDiscordID
from ElevatorBot.events.backgroundTasks import UpdateActivityDB
from ElevatorBot.events.baseEvent import BaseEvent
from ElevatorBot.core.destinyPlayer import DestinyPlayer
from ElevatorBot.core.formating import split_into_chucks_of_max_2000_characters
from ElevatorBot.core.persistentMessages import bot_status
from ElevatorBot.core.roleLookup import (
    assignRolesToUser,
    removeRolesFromUser,
    get_player_roles,
)
from ElevatorBot.networking.bungieAuth import handle_and_return_token
from ElevatorBot.networking.network import get_json_from_url
from ElevatorBot.static.config import CLANID, BOTDEVCHANNELID
from ElevatorBot.static.globals import *


# todo call this one elevator, and the sleep. Backend calls elevator webhook when done
class AutomaticRoleAssignment(BaseEvent):
    """Will automatically _update the roles"""

    def __init__(self):
        # Set the interval for this event
        dow_day_of_week = "*"
        dow_hour = 1
        dow_minute = 0
        super().__init__(
            scheduler_type="cron",
            dow_day_of_week=dow_day_of_week,
            dow_hour=dow_hour,
            dow_minute=dow_minute,
        )

    async def run(self, client):
        async def update_user(discord_member: discord.Member) -> Optional[str]:
            if discord_member.bot:
                return None

            destiny_player = await DestinyPlayer.from_discord_id(discord_member.id)
            if not destiny_player:
                return

            # gets the roles of the specific player and assigns/removes them
            roles_to_add, roles_to_remove, _, _ = await get_player_roles(discord_member, destiny_player)

            # assign roles
            await discord_member.add_roles(*roles_to_add, reason="Achievement Role Earned")

            # _delete roles
            await discord_member.remove_roles(*roles_to_remove, reason="Achievement Role Not Deserved")

            # convert to str
            new_roles = [role.name for role in roles_to_add]
            remove_roles = [role.name for role in roles_to_remove]

            if new_roles or remove_roles:
                return f'Updated player {discord_member.mention} by adding `{", ".join(new_roles or ["nothing"])}` and removing `{", ".join(remove_roles or ["nothing"])}`\n'
            else:
                return None

        print("Running the automatic role assignment...")

        # acquires the newtonslab channel from the descend server and notifies about starting
        newtonslab = client.get_channel(BOTDEVCHANNELID)
        guild = newtonslab.guild

        async with newtonslab.typing():
            update = UpdateActivityDB()
            await update.run(client)

        joblist = []
        for member in guild.members:
            # only allow people who accepted the rules
            if not member.pending:
                joblist.append(update_user(member))

        results = await asyncio.gather(*joblist)
        news = []
        for result in results:
            if result:
                news.append(result)

        if news:
            for chunk in split_into_chucks_of_max_2000_characters(text_list=news):
                await newtonslab.send(chunk)

        # _update the status
        await bot_status(
            client,
            "Achievement Role Update",
            datetime.datetime.now(tz=datetime.timezone.utc),
        )


class AutoRegisteredRole(BaseEvent):
    """Will automatically _update the registration and clan roles"""

    def __init__(self):
        interval_minutes = 30  # Set the interval for this event
        super().__init__(scheduler_type="interval", interval_minutes=interval_minutes)

    async def run(self, client):
        # get all clan members discordID
        memberlist = []
        for member in (await get_json_from_url(f"https://www.bungie.net/Platform/GroupV2/{CLANID}/Members/")).content[
            "Response"
        ]["results"]:
            destinyID = int(member["destinyUserInfo"]["membershipId"])
            discordID = await lookupDiscordID(destinyID)
            if discordID is not None:
                memberlist.append(discordID)

        if not len(memberlist) > 5:
            # error.log
            print("something broke at AutoRegisteredRole, clansize <= 5")
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
                if (await handle_and_return_token(member.id)).token:
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

        # _update the status
        await bot_status(
            client,
            "Member Role Update",
            datetime.datetime.now(tz=datetime.timezone.utc),
        )
