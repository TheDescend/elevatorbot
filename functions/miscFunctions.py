import asyncio
import datetime
import itertools

import discord
from discord_slash import SlashContext

from functions.formating import embed_message
from functions.network import handleAndReturnToken
from static.dict import expansion_dates, season_dates
from static.globals import admin_role_id, dev_role_id, mod_role_id
from static.config import COMMAND_PREFIX

async def checkIfUserIsRegistered(user):
    if (await handleAndReturnToken(user.id))["result"]:
        return True
    else:
        print(f"{user.display_name} is not registered")
        embed = embed_message(
            "Error",
            "Please register with `/registerdesc` first (not via DMs)"
        )
        await user.send(embed=embed)
        return False


async def update_status(client):
    status_messages = [
        "Type '/' to see available commands",
        "Type '/registerdesc' to register your Destiny 2 account",
        "DM me to contact staff",
        "While Neria is no longer new, welcoming someone is polite - just saying ¯\_(ツ)_/¯",
        "↓ Psst! Did you know this person stinks",
        "Slashing through life",
        "Dear god please stop using old commands and use slash commands",
        "This message has been removed due to a request from @Feedy",
        "Go sports!",
        "We all know who the best bot is",
        "Hint: Checkmarks are lame",
        "Now running v2.1 ('world_domination_test.py')",
        "Can I get vaccinated too? Technically I'm still a baby",
        "Chillin' in my Hot Tub right now 🍑💦",
    ]

    print("Launching the Status Changer Loop", flush=True)
    for element in itertools.cycle(status_messages):
        await client.change_presence(activity=discord.Game(name=element))
        await asyncio.sleep(30)


# checks if user is allowed to use the command for other user.
async def hasMentionPermission(message, user, additional_users=None):
    if additional_users is None:
        additional_users = []

    # if no other user is mentioned its ok anyways
    if user.id not in [message.author.id, *additional_users]:
        if not await hasAdminOrDevPermissions(message):
            await message.channel.send(embed=embed_message(
                'Error',
                'You are not allowed to use this command for a different user here, please try again`'
            ))
            return False
    return True


# checks for admin or  dev permissions
async def hasAdminOrDevPermissions(message, send_message=True):
    admin = discord.utils.get(message.guild.roles, id=admin_role_id)
    dev = discord.utils.get(message.guild.roles, id=dev_role_id)
    mod = discord.utils.get(message.guild.roles, id=mod_role_id)

    # also checking for Kigstns id, to make that shit work on my local version of the bot
    if message.author.id == 238388130581839872:
        return True

    if admin not in message.author.roles and dev not in message.author.roles and mod not in message.author.roles:
        if send_message:
            await message.channel.send(embed=embed_message(
                'Error',
                'You are not allowed to do that'
            ))
        return False
    return True


# todo swap old hasAdminOrDevPermissions stuff with this
async def has_elevated_permissions(user, guild, ctx: SlashContext = None):
    """ checks for admin or dev permissions, otherwise returns False. If ctx is given, return error message """
    admin = discord.utils.get(guild.roles, id=admin_role_id)
    dev = discord.utils.get(guild.roles, id=dev_role_id)
    mod = discord.utils.get(guild.roles, id=mod_role_id)

    # also checking for Kigstns id, to make that shit work on my local version of the bot
    if user.id == 238388130581839872:
        return True

    if admin not in user.roles and dev not in user.roles and mod not in user.roles:
        if ctx:
            await ctx.send(hidden=True, embed=embed_message(
                f"Error",
                f"You do not have permission do to this"
            ))
        return False
    return True


# should be called if incorrect params for command call where used
async def show_help(message, command, params):
    # work some magic that msg looks nice
    nice_looking_params = []
    for param in params:
        if param.startswith("*"):
            nice_looking_params.append(f"{param[:1]}<{param[1:]}>")
        else:
            nice_looking_params.append(f"<{param}>")

    await message.reply(embed=embed_message(
        "Incorrect Parameters",
        f"Correct usage is:\n`{COMMAND_PREFIX}{command} {' '.join(nice_looking_params)} *<user>`",
        "Info: The <user> parameter doesn't work for every command"
    ))


async def get_emoji(client, emoji_id):
    """ Return an emoji obj """

    return client.get_emoji(emoji_id)


def write_line(index, member, stat_text, stat, emoji):
    """ Write a line like charley does"""

    return f"**{index})** {member} \n{emoji} {stat_text}: {stat}"


def check_if_mutually_exclusive(possible_args: list, kwargs):
    """"
    Checks if at most one of the allowed arguments has been used.

    Returns False if more than one arg was used
    Returns True if at most one arg was used
    """

    count = 0
    for arg in possible_args:
        if type(arg) == str:
            if arg in kwargs:
                count += 1
        elif type(arg) == list:
            for subarg in arg:
                if subarg in kwargs:
                    count += 1
                    break

    return count <= 1


def convert_expansion_or_season_dates(kwargs):
    """ This takes in kwargs, looks if 'expansion' or 'season' are in them and return None, None if not, or the datetime objects """

    starttime = None
    endtime = None

    # convert expansion dates to datetimes
    if "expansion" in kwargs:
        starttime = datetime.datetime.strptime(kwargs["expansion"].split(",")[0], '%Y-%m-%d')
        try:
            endtime = expansion_dates[(expansion_dates.index(kwargs["expansion"].split(",")) + 1)][0]
            endtime = datetime.datetime.strptime(endtime, '%Y-%m-%d')
        except IndexError:
            endtime = datetime.datetime.now()

    # or convert season dates to datetimes
    elif "season" in kwargs:
        starttime = datetime.datetime.strptime(kwargs["season"].split(",")[0], '%Y-%m-%d')
        try:
            endtime = expansion_dates[(season_dates.index(kwargs["season"].split(",")) + 1)][0]
            endtime = datetime.datetime.strptime(endtime, '%Y-%m-%d')
        except IndexError:
            endtime = datetime.datetime.now()

    return starttime, endtime