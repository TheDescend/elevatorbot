from events.base_event          import BaseEvent

from functions.markovGenerator  import getMarkovSentence
from datetime                   import datetime

class Markovspam(BaseEvent):

    def __init__(self):
        interval_minutes = 0.4  # Set the interval for this event 1440 = 12h
        super().__init__(interval_minutes)

    # Override the run() method
    # It will be called once every {interval_minutes} minutes
    stopmsg = False
    async def run(self, client):
        try:
            markchannel = client.get_channel(672541982157045791)

            now = datetime.now()
            async for msg in markchannel.history(limit=45):
                if msg.author.id != 386490723223994371:
                    async with markchannel.typing():
                        await markchannel.send(getMarkovSentence())
                        return

            async for msg in markchannel.history(limit=1):
                    if not msg.content == '**type something to reactivate the bot**':
                        await markchannel.send('**type something to reactivate the bot**')

        # don't spam errors if run on a a different discord
        except:
            return
        