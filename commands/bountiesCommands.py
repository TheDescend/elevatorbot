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

from functions.bounties.bountiesTournament import tournamentRegistrationMessage, tournamentChannelMessage, \
    startTournamentEvents
from functions.dataLoading import getPGCR
from functions.database import getBountyUserList, setLevel, getLevel, lookupDestinyID
from functions.formating import embed_message
from functions.persistentMessages import persistentChannelMessages
from functions.miscFunctions import hasAdminOrDevPermissions, hasMentionPermission


# todo rewrite
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

# todo rewrite
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
