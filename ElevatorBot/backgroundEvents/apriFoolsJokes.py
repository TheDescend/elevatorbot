import random

from ElevatorBot.backgroundEvents.base import BaseEvent
from ElevatorBot.core.misc.aprilFools import play_joke
from ElevatorBot.discordEvents.base import ElevatorSnake
from ElevatorBot.misc.cache import descend_cache
from ElevatorBot.networking.errors import BackendException
from ElevatorBot.static.descendOnlyIds import descend_channels
from Shared.functions.helperFunctions import get_now_with_tz


class AprilFoolsJokes(BaseEvent):
    def __init__(self):
        interval_minutes = 30
        super().__init__(scheduler_type="interval", interval_minutes=interval_minutes)

    async def run(self, client: ElevatorSnake):
        # check if today is april first
        today = get_now_with_tz()
        if today.day != 1 or today.month != 4:
            return

        # get all members that are currently in voice channels
        voice_states = descend_channels.guild.voice_states

        # choose one at random
        chosen = random.choice(voice_states)

        # connect and play audio
        bot_voice_state = client.get_bot_voice_state(guild_id=descend_channels.guild.id)
        if not bot_voice_state or not bot_voice_state.connected:
            bot_voice_state = await chosen.channel.connect()
            await play_joke(bot_voice_state=bot_voice_state)
