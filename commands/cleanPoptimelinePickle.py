# can be deleted after used once. Cleans up the !poptimeline command

from commands.base_command  import BaseCommand

import pandas as pd

class cleanpoptimelinepickle(BaseCommand):
    def __init__(self):
        description = f'dev'
        params = []
        super().__init__(description, params)


    async def handle(self, params, message, client):
        # reading data and preparing it

        data = pd.read_pickle('database/steamPlayerData.pickle')
        data.to_pickle('database/steamPlayerData.pickle.bckp')


        run = True
        while run:
            b = False
            for i in range(len(data)):
                if b:
                    break

                datetime = data["datetime"].iloc[i]
                players = data["players"].iloc[i]


                for j in range(len(data)):
                    if i == j:
                        continue

                    datetime2 = data["datetime"].iloc[j]
                    players2 = data["players"].iloc[j]

                    try:
                        if datetime.date() == datetime2.date():
                            if players > players2:
                                data = data.iloc[:j].append(data.iloc[j+1:])
                            else:
                                data = data.iloc[:i].append(data.iloc[i+1:])
                            data = data.reset_index(drop=True)
                            b = True
                            break
                    except KeyError:
                        pass
            if not b:
                run = False
            else:
                data = data.reset_index(drop=True)
        data = data.reset_index(drop=True)
        data.to_pickle('database/steamPlayerData.pickle')