import discord
import datetime

from functions.clanJoinRequests import clanJoinRequestMessageReactions
from functions.database import getPersistentMessage, insertPersistentMessage, \
    getallSteamJoinIDs, updatePersistentMessage, getAllPersistentMessages
from functions.formating import embed_message
from static.globals import among_us_emoji_id, barotrauma_emoji_id, gta_emoji_id, valorant_emoji_id, lol_emoji_id, \
    eft_emoji_id, among_us_role_id, barotrauma_role_id, gta_role_id, valorant_role_id, lol_role_id, eft_role_id, \
    other_game_roles


async def get_persistent_message(client, message_name, guild_id):
    """
    Gets the persisten message for the specified name and guild and channel. If it doesnt exist, it will return False
    Returns message obj or False
    """

    res = await getPersistentMessage(message_name, guild_id)

    # check if msg exist
    if not res:
        return False

    # otherwise return message
    channel = client.get_channel(res[0])
    return await channel.fetch_message(res[1])


async def make_persistent_message(client, message_name, guild_id, channel_id, reaction_id_list=None, message_text=None, message_embed=None):
    """
    Creates a new persistent message entry in the DB or changes the old one
    Returns message obj
    """

    if reaction_id_list is None:
        reaction_id_list = []
    assert (not message_text and not message_embed, "Need to input either text or embed")

    # make new message
    channel = client.get_channel(channel_id)
    message = await channel.send(message_name)

    # react if wanted
    for emoji_id in reaction_id_list:
        emoji = client.get_emoji(emoji_id)
        await message.add_reaction(emoji)

    # save msg in DB
    # check if msg exists
    res = await getPersistentMessage(message_name, guild_id)

    # update
    if res:
        # delete old msg
        channel = client.get_channel(res[0])
        old_message = await channel.fetch_message(res[1])
        await old_message.delete()

        await updatePersistentMessage(message_name, guild_id, channel_id, message.id, reaction_id_list)

    # insert
    else:
        await insertPersistentMessage(message_name, guild_id, channel_id, message.id, reaction_id_list)

    return message


async def check_reaction_for_persistent_message(client, payload):
    # get all persistent messages
    persistent_messages = await getAllPersistentMessages()

    # loop through the msgs and check if reaction was on in
    for persistent_message in persistent_messages:
        persistent_message_id = persistent_message[3]

        # if it was, handle it
        if payload.message_id == persistent_message_id:
            await handle_persistent_message_reaction(client, payload, persistent_message)


async def handle_persistent_message_reaction(client, payload, persistent_message):
    message_name = persistent_message[0]
    guild_id = persistent_message[1]
    channel_id = persistent_message[2]
    message_id = persistent_message[3]
    reactions_id_list = persistent_message[4]

    # check if the reactions are ok, else remove them
    if payload.emoji.id not in reactions_id_list:
        channel = client.get_channel(channel_id)
        message = await channel.fetch_message(message_id)
        await message.remove_reaction(payload.emoji, payload.member)
        return

    # handling depends on the type of message, so if statement incoming
    if message_name == "otherGameRoles":
        await otherGameRolesMessageReactions(payload.member, payload.emoji, channel_id, message_id)

    elif message_name == "clanJoinRequest":
        await clanJoinRequestMessageReactions(client, payload.member, payload.emoji, channel_id, message_id)


async def steamJoinCodeMessage(client, guild):
    # get all IDs
    data = await getallSteamJoinIDs()

    # convert discordIDs to names
    clean_data = {}
    for k, v in data.items():
        # get display_name. If that doesnt work user isnt in guild, thus ignore him
        try:
            clean_data[guild.get_member(k).display_name] = v
        except AttributeError:
            continue

    # sort and put in two lists
    sorted_data = {k: str(v) for k, v in sorted(clean_data.items(), key=lambda item: item[0], reverse=False)}

    # put in two lists for the embed
    name = list(sorted_data.keys())
    code = list(sorted_data.values())

    # create new message
    embed = embed_message(
        "Steam Join Codes",
        "Here you can find a updated list of Steam Join Codes. \nUse `!setID <id>` to set appear here and `!getid <user>` to find a code without looking here"
    )

    # add name field
    embed.add_field(name="User", value="\n".join(name), inline=True)

    # add code field
    embed.add_field(name="Code", value="\n".join(code), inline=True)

    # get msg object
    message = await get_persistent_message(client, "steamJoinCodes", guild.id)

    # edit msg
    await message.edit(embed=embed)


async def botStatus(client, field_name: str, time: datetime.datetime):
    """
    takes the field (name) and the timestamp of last update

    Current fields in use:
        "Database Update"
        "Manifest Update"
        "Token Refresh"
        "Member Role Update"
        "Achievement Role Update"
        "Bounties - Experience Update"
        "Bounties - Generation"
        "Bounties - Completion Update"
        "Steam Player Update"
        "Vendor Armor Roll Lookup"
    """

    # get msg. guild id is one, since there is only gonna be one msg
    message = await get_persistent_message(client, "botStatus", 1)

    embed = embed_message(
        "Status: Last valid..."
    )

    embeds = message.embeds[0]
    fields = embeds.fields

    found = False
    for field in fields:
        embed.add_field(name=field.name, value=f"""{time.strftime("%d/%m/%Y, %H:%M")} UTC""" if field.name == field_name else field.value, inline=True)
        if field.name == field_name:
            found = True

    if not found:
        embed.add_field(name=field_name, value=str(time), inline=True)

    await message.edit(embed=embed)


async def otherGameRolesMessageReactions(user, emoji, channel_id, channel_message_id):
    async def handle_reaction(m, u, r, e_id, r_id):
        if r_id not in r:
            await u.add_roles(discord.utils.get(m.guild.roles, id=r_id), reason="Other Game Roles")
        else:
            await u.remove_roles(discord.utils.get(m.guild.roles, id=r_id), reason="Other Game Roles")
        await m.remove_reaction(e_id, u)

    message = await channel_id.fetch_message(channel_message_id)

    # get current roles
    roles = [role.id for role in user.roles]

    # remove reaction and apply role
    for emoji_id, role_id in other_game_roles:
        if emoji.id == emoji_id:
            await handle_reaction(message, user, roles, emoji_id, role_id)
