from functions.dataLoading import getTriumphsJSON
from functions.network  import getJSONfromURL
from events.base_event import BaseEvent

import json
import pandas
import datetime
import os
import concurrent.futures



class refreshSealPickle(BaseEvent):
    def __init__(self):
        interval_minutes = 1440  # Set the interval for this event
        super().__init__(interval_minutes)

    def getTriumphData(self, triumph, not_available, cant_earn_anymore):
        rep = getJSONfromURL(f"https://www.bungie.net/Platform/Destiny2/Manifest/DestinyRecordDefinition/{triumph}/")

        # converting to python dict (for true -> True conversion)
        rep = json.loads(json.dumps(rep))

        if rep and rep['Response']:
            try:
                if rep['Response']["titleInfo"]["hasTitle"]:
                    # ignore titles that don't have objectives
                    if rep['Response']["objectiveHashes"]:
                        if int(triumph) not in not_available:
                            still_available = bool(int(triumph) not in cant_earn_anymore)
                            return [
                                triumph,
                                rep['Response']["displayProperties"]["name"],
                                rep['Response']["titleInfo"]["titlesByGender"]["Male"],
                                still_available,
                            ]

            except Exception as exc:
                pass
                # print(f'generated an exception: {exc}')


    # Override the run() method
    # It will be called once every day
    async def run(self, *client):
        not_available = [
            837071607,  # shaxx
            1754815776,  # wishbringer
        ]
        cant_earn_anymore = [
            2254764897,  # MMIX
            2707428411,  # Undying
            2460356851,  # Dawn
            2945528800,  # flawless s10
            1983630873,  # Conqueror s10
            2860165064  # almighty
        ]

        print("Refreshing seals.pickle")

        # create dataframe if file doesn't exist
        try:
            file = pandas.read_pickle('database/seals.pickle')
        except FileNotFoundError:
            file = pandas.DataFrame({"date": [datetime.date.min]})

        triumphs = getTriumphsJSON(4611686018467765462)

        seals = []
        if triumphs is None:
            return False

        # converting to python dict (for true -> True conversion)
        triumphs = json.loads(json.dumps(triumphs))

        with concurrent.futures.ThreadPoolExecutor(os.cpu_count() * 1) as pool:
            futurelist = [pool.submit(self.getTriumphData, triumph, not_available, cant_earn_anymore) for triumph in triumphs]
            for future in concurrent.futures.as_completed(futurelist):
                try:
                    result = future.result()
                    if result:
                        seals.append(result)

                except Exception as exc:
                    pass
                    # print(f'generated an exception: {exc}')

        # print(seals)

        # write new pickle
        file["date"] = [datetime.date.today()]
        file["seals"] = [seals]
        file.to_pickle('database/seals.pickle')

        print("Done refreshing seals.pickle")