import asyncio
import os
import random

import aiohttp
import gtts
from naff import ActionRow, Button, ButtonStyles, Member, OptionTypes, slash_command, slash_option
from naff.api.voice.audio import AudioVolume

from ElevatorBot.commandHelpers.permissionTemplates import restrict_default_permission
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.networking.misc.giveaway import BackendGiveaway
from ElevatorBot.static.jokes import jokes
from Shared.functions.readSettingsFile import get_setting

# =============
# Descend Only!
# =============


class Joke(BaseModule):
    @slash_command(
        name="joke",
        description="Tells you a very funny joke",
        dm_permission=False,
        scopes=get_setting("COMMAND_GUILD_SCOPE"),
    )
    async def giveaway(self, ctx: ElevatorInteractionContext):
        voice_state = ctx.author.voice
        run = False
        bot_voice_state = None

        # user not in voice
        if not voice_state:
            embed = embed_message("Error", "You are not in a voice channel, how am I supposed to tell you a joke???")

        else:
            bot_voice_state = ctx.bot.get_bot_voice_state(guild_id=voice_state.guild.id)

            # bot not in voice
            if bot_voice_state and bot_voice_state.connected:
                embed = embed_message("Error", "I'm busy telling a joke, try again in a bit")

            else:
                embed = embed_message(
                    "This joke is gonna blow your mind, you wait for it!",
                )
                run = True

                # connect to the authors voice channel
                bot_voice_state = await voice_state.channel.connect()

        await ctx.send(embed=embed)
        if run and bot_voice_state:
            joke = random.choice(jokes)
            joke_audio = await asyncio.to_thread(lambda: gtts.gTTS(joke))

            filename = "joke.mp3"
            joke_audio.save(filename)
            to_play = AudioVolume(filename)

            # play the audio
            await bot_voice_state.wait_for_stopped()
            await bot_voice_state.play(to_play)

            # delete and disconnect
            await bot_voice_state.disconnect()
            os.remove(filename)


def setup(client):
    Joke(client)
