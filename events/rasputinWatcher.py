from events.base_event              import BaseEvent

from functions.markovGenerator      import getMarkovSentence
from functions.authfunctions        import getRasputinQuestProgress

from datetime                       import datetime
import pandas                           as pd
import os

class rasputinWatcher(BaseEvent):

    def __init__(self):
        interval_minutes = 15  # Set the interval for this event 1440 = 12h
        super().__init__(interval_minutes)

    # Override the run() method
    # It will be called once every {interval_minutes} minutes

    async def run(self, client):
        if not os.path.exists('database/rasputinData.pickle'):
            rasputindf = pd.DataFrame(columns=["datetime",'moon','edz', 'io'])
        else:
            rasputindf = pd.read_pickle('database/rasputinData.pickle')
        now = datetime.now()
        newdict = {
            'datetime':now
        }
        for objname, objprogress, objtotal in getRasputinQuestProgress():
            newdict[objname.lower()] = objprogress
        
        rasputindf = rasputindf.append(newdict, ignore_index=True)
        rasputindf.to_pickle('database/rasputinData.pickle')

        