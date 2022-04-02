import asyncio
import os

import aiohttp
import gtts
from dis_snek import ActiveVoiceState, Message
from dis_snek.api.voice.audio import AudioVolume


async def play_joke(bot_voice_state: ActiveVoiceState, message: Message | None = None):
    """Connect to voice and tell a joke"""

    # get the joke
    async with aiohttp.ClientSession() as session:
        async with session.get("https://v2.jokeapi.dev/joke/Miscellaneous,Dark,Pun?type=single") as resp:
            try:
                joke_json = await resp.json()
                joke = joke_json["joke"]

                joke_audio = await asyncio.to_thread(lambda: gtts.gTTS(joke))

            except:
                if message:
                    await message.reply("Sorry, failed getting a joke")

            else:
                filename = "joke.mp3"
                joke_audio.save(filename)
                to_play = AudioVolume(filename)

                # play the audio
                await bot_voice_state.wait_for_stopped()
                await bot_voice_state.play(to_play)

                # delete and disconnect
                await bot_voice_state.disconnect()
                os.remove(filename)
