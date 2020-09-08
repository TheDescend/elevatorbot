from commands.base_command  import BaseCommand
from functions.bounties.bountiesBackend import saveAsGlobalVar, deleteFromGlobalVar
from functions.bounties.bountiesFunctions import bountiesChannelMessage

import os
import pickle
import discord

gta_id = 709120893728718910
barotrauma_id = 738438622553964636
valorant_id = 709378171832893572
amongUs_id = 750409552075423753

class makeChannelOtherGameRoles(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "[dev] make channel for getting other game roles. will delete all msg in channel if used"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        # add channel id to pickle where bounty channel ids are also saved
        deleteFromGlobalVar("other_game_roles_channel_message_id")
        saveAsGlobalVar("other_game_roles_channel", message.channel.id, message.guild.id)
        await bountiesChannelMessage(client)


# writes the message the user will see and react to and saves the id in the pickle

# assign the roles. get's called from bloodbot.py
async def otherGameRolesMessageReactions(client, user, emoji, register_channel, channel_message_id):
    message = await register_channel.fetch_message(channel_message_id)

    # emoji ids
    among_us = client.get_emoji(751020830376591420)
    barotrauma = client.get_emoji(751022749773856929)
    gta = client.get_emoji(751020831382962247)
    valorant = client.get_emoji(751020830414209064)

    # role ids
    amongUs_id = 750409552075423753
    barotrauma_id = 738438622553964636
    gta_id = 709120893728718910
    valorant_id = 709378171832893572

    # get current roles
    roles = [role.id for role in user.roles]

    # remove reaction and apply role
    if emoji == among_us:
        if amongUs_id not in roles:
            await user.add_roles(discord.utils.get(message.guild.roles, id=amongUs_id))
        else:
            await user.remove_roles(discord.utils.get(message.guild.roles, id=amongUs_id))
        await message.remove_reaction(among_us, user)

    elif emoji.name == barotrauma:
        if barotrauma_id not in roles:
            await user.add_roles(discord.utils.get(message.guild.roles, id=barotrauma_id))
        else:
            await user.remove_roles(discord.utils.get(message.guild.roles, id=barotrauma_id))
        await message.remove_reaction(barotrauma, user)

    elif emoji.name == gta:
        if gta_id not in roles:
            await user.add_roles(discord.utils.get(message.guild.roles, id=gta_id))
        else:
            await user.remove_roles(discord.utils.get(message.guild.roles, id=gta_id))
        await message.remove_reaction(gta, user)

    elif emoji.name == valorant:
        if valorant_id not in roles:
            await user.add_roles(discord.utils.get(message.guild.roles, id=valorant_id))
        else:
            await user.remove_roles(discord.utils.get(message.guild.roles, id=valorant_id))
        await message.remove_reaction(valorant, user)