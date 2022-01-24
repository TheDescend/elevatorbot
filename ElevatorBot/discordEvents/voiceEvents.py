import asyncio

from dis_snek.api.events import VoiceStateUpdate

from ElevatorBot.backendNetworking.destiny.lfgSystem import DestinyLfgSystem
from ElevatorBot.core.misc.persistentMessages import PersistentMessages
from ElevatorBot.static.descendOnlyIds import descend_channels

greek_names = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta", "Iota", "Kappa"]


async def on_voice_state_update(event: VoiceStateUpdate):
    """Triggers when a members voice state changes"""

    # freshly join a channel
    if event.before.channel is None:
        await joined_channel(event)

    # fully leave a channel
    elif event.after.channel is None:
        await left_channel(event)

    # switch channel
    elif event.before.channel != event.after.channel:
        await left_channel(event)
        await joined_channel(event)


async def left_channel(event: VoiceStateUpdate):
    """Gets triggered when a member leaves a channel"""

    # get the lfg voice category
    persistent_messages = PersistentMessages(ctx=None, guild=event.before.guild, message_name="lfg_voice_category")
    result = await persistent_messages.get()
    lfg_voice_category_channel = await event.bot.get_channel(result.channel_id)

    # check if the channel was a lfg channel (correct category)
    if event.before.channel.category == lfg_voice_category_channel:
        # check if channel is now empty
        if len(event.before.channel.members) == 1:
            # get the guilds lfg events
            lfg_backend = DestinyLfgSystem(ctx=None, discord_guild=event.before.guild)
            result = await lfg_backend.get_all()

            # check that more than 10 min have passed since the start (not in the DB anymore)
            for lfg_event in result.events:
                if lfg_event.voice_channel_id == event.before.channel.id:
                    # delete if found
                    await event.before.channel.delete(reason="LFG event over")
                    break

    # auto channel deletion
    else:
        # only do this for descend
        if event.before and event.before.guild == descend_channels.guild:
            # only delete if they were the last in there
            if len(event.before.channel.members) == 1:
                split_name = event.before.channel.name.split("|")
                if len(split_name) > 1:
                    base_name = split_name[0]
                    greek_name = split_name[1].strip()
                    if greek_name in greek_names:
                        async with asyncio.Lock():
                            # get all channels from the category and change them
                            i = 0
                            for voice_channel in event.before.channel.category.voice_channels:
                                if base_name in voice_channel.name:
                                    vc_greek_name = voice_channel.name.split("|")[1].strip()

                                    if voice_channel == event.before.channel:
                                        await event.before.channel.delete()
                                        continue

                                    new_name = voice_channel.name.replace(vc_greek_name, greek_names[i])
                                    if voice_channel.name != new_name:
                                        await voice_channel.edit(name=new_name)

                                    i += 1


async def joined_channel(event: VoiceStateUpdate):
    """Gets triggered when a member joins a channel"""

    # only do this for descend
    if event.after and event.after.guild == descend_channels.guild:
        if len(event.after.channel.members) == 1:
            split_name = event.after.channel.name.split("|")
            if len(split_name) > 1:
                greek_name = split_name[1].strip()
                if greek_name in greek_names:
                    async with asyncio.Lock():
                        # calculate the next name
                        try:
                            next_greek_name = greek_names[greek_names.index(greek_name) + 1]
                        except IndexError:
                            return
                        new_channel_name = event.after.channel.name.replace(greek_name, next_greek_name)

                        # look for the new name
                        found = False
                        for voice_channel in event.after.channel.category.voice_channels:
                            if voice_channel.name == new_channel_name:
                                found = True

                        # make sure we are only creating a channel if one with the next letter does not exist
                        if not found:
                            # clone the channel with the new name
                            await event.after.channel.clone(name=new_channel_name)
