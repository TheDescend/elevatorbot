from functions.formating import embed_message
from functions.bounties.bountiesFunctions import getGlobalVar, saveAsGlobalVar

import discord


# writes the message the user will see and react to and saves the id in the pickle
async def persistentChannelMessages(client):
    file = getGlobalVar()

    for guild in client.guilds:
        if guild.id == file["guild_id"]:
            # the clan join request feature
            if "clan_join_request_channel" in file:
                if "clan_join_request_channel_message_id" not in file:
                    channel = discord.utils.get(guild.channels, id=file["clan_join_request_channel"])
                    await channel.purge(limit=100)

                    await channel.send(
f"""**Welcome to Descend!**

We are an EU based community of veteran players who have created their own community for chill PVE and PVP activities while still focusing on raids and other endgame activities.

If you want to join the clan, react to the message below and if you fulfill the requirements, you will instantly receive an invite to join the clan.


__Requirements:__
- Join the Discord <> Wow, you already did that :)
- Register with `!registerdesc` in <#670401854496309268>
⁣
"""
                    )

                    # send register msg and save the id
                    msg = await channel.send(embed=embed_message(
                        f'Clan Application',
                        f'React if you want to join the clan'
                    ))

                    join = client.get_emoji(754928322403631216)
                    await msg.add_reaction(join)

                    saveAsGlobalVar("clan_join_request_channel_message_id", msg.id)

            # the other games role channel message
            if "other_game_roles_channel" in file:
                if "other_game_roles_channel_message_id" not in file:
                    channel = discord.utils.get(guild.channels, id=file["other_game_roles_channel"])
                    await channel.purge(limit=100)

                    # send register msg and save the id
                    msg = await channel.send(embed=embed_message(
                        f'Other Game Roles',
                        f'React to add / remove other game roles'
                    ))

                    among_us = client.get_emoji(751020830376591420)
                    barotrauma = client.get_emoji(756077724870901830)
                    gta = client.get_emoji(751020831382962247)
                    valorant = client.get_emoji(751020830414209064)
                    lol = client.get_emoji(756076309527920661)

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
                    await channel.purge(limit=100)

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