import asyncio
import datetime
import itertools
import re

import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord_slash import SlashContext

from database.database import select_guild_lfg_events
from functions.formating import embed_message
from networking.bungieAuth import handle_and_return_token
from static.config import COMMAND_PREFIX
from static.dict import expansion_dates, season_dates
from static.globals import admin_role_id, dev_role_id, mod_role_id


scheduler = None


async def checkIfUserIsRegistered(
    user
):
    if (await handle_and_return_token(user.id)).token:
        return True
    else:
        print(f"{user.display_name} is not registered")
        embed = embed_message(
            "Error",
            "Please register with `/registerdesc` first (not via DMs)"
        )
        await user.send(embed=embed)
        return False


async def update_status(
    client
):
    status_messages = [
        "Type '/' to see available commands",
        "Type '/registerdesc' to register your Destiny 2 account",
        "DM me to contact staff",
        "↓ Psst! Did you know this person stinks",
        "I head @Tom wants to be sherpa'd through GoS to finally get Divinity, but is too afraid to ask",
        "This message has been removed due to a request from @Feedy",
        "We all know who the best bot is",
        "Hint: Checkmarks are lame",
        "Hmm, maybe an actual versioning system would be about time",
        "Can I get vaccinated too? Technically I'm still a baby",
        "Chillin' in my Hot Tub right now 🍑💦",
        "I can win the hard mode TicTacToe, can you?",
        "Presenting: Extra context! Right click a message or a user to be amazed",
        "I am fluent in over six million forms of communication",
        "dis-snek > d.py",
        "Yehaw?"
    ]

    status_messages.append(f"I have {len(status_messages)} status messages :)")

    for element in itertools.cycle(status_messages):
        await client.change_presence(activity=discord.Game(name=element))
        await asyncio.sleep(30)


# checks if user is allowed to use the command for other user.
async def hasMentionPermission(
    message,
    user,
    additional_users=None
):
    if additional_users is None:
        additional_users = []

    # if no other user is mentioned its ok anyways
    if user.id not in [message.author.id, *additional_users]:
        if not await hasAdminOrDevPermissions(message):
            await message.channel.send(
                embed=embed_message(
                    'Error',
                    'You are not allowed to use this command for a different user here, please try again`'
                )
            )
            return False
    return True


# checks for admin or  dev permissions
async def hasAdminOrDevPermissions(
    message,
    send_message=True
):
    admin = discord.utils.get(message.guild.roles, id=admin_role_id)
    dev = discord.utils.get(message.guild.roles, id=dev_role_id)
    mod = discord.utils.get(message.guild.roles, id=mod_role_id)

    # also checking for Kigstns id, to make that shit work on my local version of the bot
    if message.author.id == 238388130581839872:
        return True

    if admin not in message.author.roles and dev not in message.author.roles and mod not in message.author.roles:
        if send_message:
            await message.channel.send(
                embed=embed_message(
                    'Error',
                    'You are not allowed to do that'
                )
            )
        return False
    return True


# todo swap old hasAdminOrDevPermissions stuff with this
async def has_elevated_permissions(
    user,
    guild,
    ctx: SlashContext = None
):
    """ checks for admin or dev permissions, otherwise returns False. If ctx is given, return error message """
    admin = discord.utils.get(guild.roles, id=admin_role_id)
    dev = discord.utils.get(guild.roles, id=dev_role_id)
    mod = discord.utils.get(guild.roles, id=mod_role_id)

    # also checking for Kigstns id, to make that shit work on my local version of the bot
    if user.id == 238388130581839872:
        return True

    if admin not in user.roles and dev not in user.roles and mod not in user.roles:
        if ctx:
            await ctx.send(
                hidden=True, embed=embed_message(
                    f"Error",
                    f"You do not have permission do to this"
                )
            )
        return False
    return True


# should be called if incorrect params for command call where used
async def show_help(
    message,
    command,
    params
):
    # work some magic that msg looks nice
    nice_looking_params = []
    for param in params:
        if param.startswith("*"):
            nice_looking_params.append(f"{param[:1]}<{param[1:]}>")
        else:
            nice_looking_params.append(f"<{param}>")

    await message.reply(
        embed=embed_message(
            "Incorrect Parameters",
            f"Correct usage is:\n`{COMMAND_PREFIX}{command} {' '.join(nice_looking_params)} *<user>`",
            "Info: The <user> parameter doesn't work for every command"
        )
    )


async def get_emoji(
    client,
    emoji_id
):
    """ Return an emoji obj """

    return client.get_emoji(emoji_id)


def write_line(
    index,
    member,
    stat_text,
    stat,
    emoji
):
    """ Write a line like charley does"""

    return f"**{index})** {member} \n{emoji} {stat_text}: {stat}"


def check_if_mutually_exclusive(
    possible_args: list,
    kwargs
):
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


def convert_expansion_or_season_dates(
    kwargs
):
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


def get_scheduler():
    """ Returns the apscheduler object """

    global scheduler
    if not scheduler:
        scheduler = AsyncIOScheduler()
        scheduler.start()
    return scheduler


async def left_channel(
    client,
    member,
    before_channel,
    after_channel,
    lfg_voice_category_channel=None
):
    # check if the channel was an lfg channel (correct category)
    if before_channel.category_id == lfg_voice_category_channel.id:
        # get current guild lfg channels
        guild = member.guild
        guild_lfg_events = await select_guild_lfg_events(guild.id)
        guild_lfg_voice_channels = []
        for event in guild_lfg_events:
            if event["voice_channel_id"]:
                guild_lfg_voice_channels.append(event["voice_channel_id"])

        # check if channel is now empty, and is not in the DB anymore (more than 10 min since start have passed)
        if (not before_channel.members) and (before_channel.id not in guild_lfg_voice_channels):
            await before_channel.delete(reason="LFG event over")

    # or do whatever hali think this does. no idea honestly
    else:
        defaultchannels = 2
        nummatch = re.findall(r'\d\d', before_channel.name)
        if nummatch:
            number = int(nummatch[-1])
            previousnumber = number - 1
            previousnumberstring = str(previousnumber).zfill(2)

            channelnamebase = before_channel.name.replace(nummatch[-1], '')

            achannel = before_channel
            while achannel is not None:
                number = number + 1
                achannel = discord.utils.get(member.guild.voice_channels, name=channelnamebase + str(number).zfill(2))
            number = number - 1

            for i in range(defaultchannels + 1, number + 1, 1):
                higher = discord.utils.get(member.guild.voice_channels, name=channelnamebase + str(i).zfill(2))
                below = discord.utils.get(member.guild.voice_channels, name=channelnamebase + str(i - 1).zfill(2))
                if higher and not higher.members:
                    if below and not below.members:
                        await higher.delete()

            for i in range(defaultchannels + 1, number + 1, 1):
                higher = discord.utils.get(member.guild.voice_channels, name=channelnamebase + str(i).zfill(2))
                below = discord.utils.get(member.guild.voice_channels, name=channelnamebase + str(i - 1).zfill(2))
                if higher and not below:
                    await higher.edit(name=channelnamebase + str(i - 1).zfill(2))


async def joined_channel(
    client,
    member,
    channel
):
    nummatch = re.findall(r'\d\d', channel.name)
    if nummatch:
        number = int(nummatch[-1])
        nextnumber = number + 1
        if nextnumber == 8:
            # await member.send('What the fuck are you doing')
            return
        nextnumberstring = str(nextnumber).zfill(2)

        channelnamebase = channel.name.replace(nummatch[-1], '')

        if not discord.utils.get(member.guild.voice_channels, name=channelnamebase + nextnumberstring):
            await channel.clone(name=channelnamebase + nextnumberstring)
            newchannel = discord.utils.get(member.guild.voice_channels, name=channelnamebase + nextnumberstring)
            await newchannel.edit(position=channel.position + 1)
            if 'PVP' in channel.name:
                await newchannel.edit(position=channel.position + 1, user_limit=6)
