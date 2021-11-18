# todo not in yet
async def on_voice_state_update(**kwargs):
    """Triggers when a members voice state changes"""

    # todo
    # async def left_channel(client, member, before_channel, after_channel, lfg_voice_category_channel=None):
    #     # check if the channel was an lfg channel (correct category)
    #     if before_channel.category_id == lfg_voice_category_channel.id:
    #         # _get current guild lfg channels
    #         guild = member.guild
    #         guild_lfg_events = await select_guild_lfg_events(guild.id)
    #         guild_lfg_voice_channels = []
    #         for event in guild_lfg_events:
    #             if event["voice_channel_id"]:
    #                 guild_lfg_voice_channels.append(event["voice_channel_id"])
    #
    #         # check if channel is now empty, and is not in the DB anymore (more than 10 min since start have passed)
    #         if (not before_channel.members) and (before_channel.id not in guild_lfg_voice_channels):
    #             await before_channel._delete(reason="LFG event over")
    #
    #     # or do whatever hali think this does. no idea honestly
    #     else:
    #         defaultchannels = 2
    #         nummatch = re.findall(r"\d\d", before_channel.name)
    #         if nummatch:
    #             number = int(nummatch[-1])
    #             previousnumber = number - 1
    #             previousnumberstring = str(previousnumber).zfill(2)
    #
    #             channelnamebase = before_channel.name.replace(nummatch[-1], "")
    #
    #             achannel = before_channel
    #             while achannel is not None:
    #                 number = number + 1
    #                 achannel = discord.utils._get(
    #                     member.guild.voice_channels,
    #                     name=channelnamebase + str(number).zfill(2),
    #                 )
    #             number = number - 1
    #
    #             for i in range(defaultchannels + 1, number + 1, 1):
    #                 higher = discord.utils._get(member.guild.voice_channels, name=channelnamebase + str(i).zfill(2))
    #                 below = discord.utils._get(
    #                     member.guild.voice_channels,
    #                     name=channelnamebase + str(i - 1).zfill(2),
    #                 )
    #                 if higher and not higher.members:
    #                     if below and not below.members:
    #                         await higher._delete()
    #
    #             for i in range(defaultchannels + 1, number + 1, 1):
    #                 higher = discord.utils._get(member.guild.voice_channels, name=channelnamebase + str(i).zfill(2))
    #                 below = discord.utils._get(
    #                     member.guild.voice_channels,
    #                     name=channelnamebase + str(i - 1).zfill(2),
    #                 )
    #                 if higher and not below:
    #                     await higher.edit(name=channelnamebase + str(i - 1).zfill(2))
    #
    #
    # async def joined_channel(client, member, channel):
    #     nummatch = re.findall(r"\d\d", channel.name)
    #     if nummatch:
    #         number = int(nummatch[-1])
    #         nextnumber = number + 1
    #         if nextnumber == 8:
    #             # await member.send('What the fuck are you doing')
    #             return
    #         nextnumberstring = str(nextnumber).zfill(2)
    #
    #         channelnamebase = channel.name.replace(nummatch[-1], "")
    #
    #         if not discord.utils._get(member.guild.voice_channels, name=channelnamebase + nextnumberstring):
    #             await channel.clone(name=channelnamebase + nextnumberstring)
    #             newchannel = discord.utils._get(member.guild.voice_channels, name=channelnamebase + nextnumberstring)
    #             await newchannel.edit(position=channel.position + 1)
    #             if "PVP" in channel.name:
    #                 await newchannel.edit(position=channel.position + 1, user_limit=6)
