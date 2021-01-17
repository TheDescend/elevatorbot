import discord
import datetime

from functions.bounties.bountiesFunctions import getGlobalVar, saveAsGlobalVar
from functions.database import getPersistentMessage, updatePersistentMessage, insertPersistentMessage, \
    getallSteamJoinIDs
from functions.formating import embed_message
# writes the message the user will see and react to and saves the id in the pickle
from static.globals import yes_emoji_id, destiny_emoji_id, among_us_emoji_id, barotrauma_emoji_id, gta_emoji_id, \
    valorant_emoji_id, lol_emoji_id, steam_join_codes_channel_id, admin_workboard_channel_id


# todo change this to the new format
async def persistentChannelMessages(client):
    file = getGlobalVar()

    for guild in client.guilds:
        if guild.id == file["guild_id"]:
            # the read rules feature
            if "read_rules_channel" in file:
                if "read_rules_channel_message_id" not in file:
                    channel = discord.utils.get(guild.channels, id=file["read_rules_channel"])

                    msg = await channel.send(embed=embed_message(
                        "Access The Server",
                        "If you have read the information above and **Agree** to the rules, please react accordingly"
                    ))
                    join = client.get_emoji(yes_emoji_id)
                    await msg.add_reaction(join)

                    saveAsGlobalVar("read_rules_channel_message_id", msg.id)

            # the clan join request feature
            if "clan_join_request_channel" in file:
                if "clan_join_request_channel_message_id" not in file:
                    channel = discord.utils.get(guild.channels, id=file["clan_join_request_channel"])

                    # send register msg and save the id
                    msg = await channel.send(embed=embed_message(
                        f'Clan Application',
                        f'React if you want to join the clan'
                    ))

                    join = client.get_emoji(destiny_emoji_id)
                    await msg.add_reaction(join)

                    saveAsGlobalVar("clan_join_request_channel_message_id", msg.id)

            # the other games role channel message
            if "other_game_roles_channel" in file:
                if "other_game_roles_channel_message_id" not in file:
                    channel = discord.utils.get(guild.channels, id=file["other_game_roles_channel"])

                    # send register msg and save the id
                    msg = await channel.send(embed=embed_message(
                        f'Other Game Roles',
                        f'React to add / remove other game roles'
                    ))

                    among_us = client.get_emoji(among_us_emoji_id)
                    barotrauma = client.get_emoji(barotrauma_emoji_id)
                    gta = client.get_emoji(gta_emoji_id)
                    valorant = client.get_emoji(valorant_emoji_id)
                    lol = client.get_emoji(lol_emoji_id)

                    await msg.add_reaction(among_us)
                    await msg.add_reaction(barotrauma)
                    await msg.add_reaction(gta)
                    await msg.add_reaction(valorant)
                    await msg.add_reaction(lol)

                    saveAsGlobalVar("other_game_roles_channel_message_id", msg.id)

            # put message in #register channel if there is none
            if "register_channel" in file:
                if "register_channel_message_id" not in file:
                    channel = discord.utils.get(guild.channels, id=file["register_channel"])

                    # send welcome and info message
                    await channel.send(
f"""Welcome the the **Bounty Goblins**!
⁣
After you register to this truly **remarkable** program, you will be assigned an experience level and given a bunch of bounties you can complete at your leisure.
⁣
**Normal bounties** can be completed once and award you the shown points.
**Competitive bounties** are meant to be a competition between all participants and reward a lot of points, but only one player can win. If there are any ties, both parties will of course get the points.
⁣
Your experience level determines which normal bounties you can complete. That way we can have easier bounties for new players compared to veterans. 
```
+-----------------------------------------------------------+
|            Requirements for Experienced Players           |
+--------------------+---------------------+----------------+
|        Raids       |         PvE         |       PvP      |
+--------------------+---------------------+----------------+
|   35 total clears  | 500h total Playtime | K/D above 1.11 |
| Every raid cleared |                     |                |
+--------------------+---------------------+----------------+```
"""
                    )
                    await channel.send(
f"""There are a bunch of commands which will give you more thorough information than visible in the channels:
⁣
__Commands:__
`!leaderboard <category>` - Prints various leaderboards.
`!experienceLevel` - Updates and DMs you your experience levels. 
`!bounties` - DMs you an overview of you current bounties and their status.
⁣
The bounties change every monday at midnight and will get displayed in their respective channels. You can also sign up to get notified when that happened.
⁣
And lastly, if you have any general suggestions or ideas for new bounties, contact <@!238388130581839872>
⁣
⁣
"""
                    )

                    # send register msg and save the id
                    msg = await channel.send(embed=embed_message(
                        f'Registration',
                        f'If you want to register to the **Bounty Goblins**, react with <:desc_bungie:754928322403631216>  \n\n If you want to receive a notification whenever new bounties are available, react with <:elevator_ping:754946724237148220>'
                    ))
                    register = client.get_emoji(754928322403631216)
                    await msg.add_reaction(register)
                    notification = client.get_emoji(754946724237148220)
                    await msg.add_reaction(notification)
                    saveAsGlobalVar("register_channel_message_id", msg.id)



async def steamJoinCodeMessage(client, guild):
    # get all IDs
    data = dict(getallSteamJoinIDs())
    data = {k: v for k, v in sorted(data.items(), key=lambda item: item[1], reverse=False)}

    # put in two lists for the embed
    name = []
    code = []
    for i, c in data.items():
        # get display_name. If that doesnt work user isnt in guild, thus ignore him
        try:
            n = guild.get_member(i).display_name
        except AttributeError:
            continue

        name.append(n)
        code.append(str(c))

    # create new message
    embed = embed_message(
        "Steam Join Codes",
        "Here you can find a updated list of Steam Join Codes. \nUse `!setID` to set appear here and `!getid <user>` to find a code without looking here"
    )

    # add name field
    embed.add_field(name="User", value="\n".join(name), inline=True)

    # add code field
    embed.add_field(name="Code", value="\n".join(code), inline=True)

    # get msg object.
    res = getPersistentMessage("steamJoinCodes", guild.id)
    if res:
        channel = client.get_channel(res[0])
        message = await channel.fetch_message(res[1])
        await message.edit(embed=embed)

    # Skip if no message exist and begin making one
    else:
        channel = client.get_channel(steam_join_codes_channel_id)
        message = await channel.send(embed=embed)
        insertPersistentMessage("steamJoinCodes", guild.id, channel.id, message.id, [])


async def botStatus(client, field_name: str, time: datetime.datetime):
    """
    takes the field (name) and the timestamp of last update

    Current fields in use:
        "Database Update"
        "Member Role Update"
        "Achievement Role Update"
        "Bounties - Experience Update"
        "Bounties - Generation"
        "Bounties - Completion Update"
    """

    # get msg. guild id is one, since there is only gonna be one msg
    res = getPersistentMessage("botStatus", 1)

    embed = embed_message(
        "Status: Last valid..."
    )

    if res:
        channel = client.get_channel(res[0])
        if not channel:
            return
        message = await channel.fetch_message(res[1])
        embeds = message.embeds[0]
        fields = embeds.fields

        found = False
        for field in fields:
            embed.add_field(name=field.name, value=str(time) if field.name == field_name else field.value, inline=True)
            if field.name == field_name:
                found = True

        if not found:
            embed.add_field(name=field_name, value=str(time), inline=True)

        await message.edit(embed=embed)


    else:
        channel = client.get_channel(admin_workboard_channel_id)
        if not channel:
            return

        embed.add_field(name=field_name, value=str(time), inline=True)

        message = await channel.send(embed=embed)

        insertPersistentMessage("botStatus", 1, channel.id, message.id, [])

