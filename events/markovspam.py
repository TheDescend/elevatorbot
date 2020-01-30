from events.base_event      import BaseEvent

from markovGenerator        import getMarkovSentence
import datetime

class Markovspam(BaseEvent):

    def __init__(self):
        interval_minutes = 0.4  # Set the interval for this event 1440 = 12h
        super().__init__(interval_minutes)

    # Override the run() method
    # It will be called once every {interval_minutes} minutes
    stopmsg = False
    async def run(self, client):
        markchannel = client.get_channel(672541982157045791)
        now = datetime.datetime.now()
        stopmsg = False
        async for msg in markchannel.history(limit=20):
            if msg.author.id != 386490723223994371:
                async with markchannel.typing():
                    await markchannel.send(getMarkovSentence())
                    stopmsg = False
                    return
                
        if not stopmsg:
            await markchannel.send('type something to reactivate the bot')
            stopmsg = True
                
        