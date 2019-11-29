from events.base_event      import BaseEvent

import discord
from io import open
import random

from generateFastAchievementList import createSheet

class ExiledsWeeklySheet(BaseEvent):

    def __init__(self):
        interval_minutes = 604800  # Set the interval for this event - 7 days
        super().__init__(interval_minutes)

    # Override the run() method
    # It will be called once every {interval_minutes} minutes
    async def run(self, client):
        greetings = ['Have a nice week', 'Enjoy the grind!', 'You\'re doing great', 'Thanks for everything', 'The clan appreciates you', 'You can achieve your goals', 'Someone cares', 'Life is like a Jötunn', 'Enjoy the little things']
        print('generating and sending exileds sheet')
        exiled = client.get_user(206878830017773568)
        sheetpath = createSheet()
        if sheetpath is not None:
            f = discord.File(open(sheetpath,'rb'),'AchievementSheet.xlsx')
            await exiled.send(file=f)
            await exiled.send(random.choice(greetings))
        else:
            await exiled.send('something happened to the bot, sorry')
