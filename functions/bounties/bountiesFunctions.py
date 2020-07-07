import os
import pickle

# Channels:
# #leaderboards
# #register
# #tournament

# I'd call those from bloodbot.py
def registerMessage(client, channelID):
    pass
    # everyone who reacts to this get's bounbties and pings

def giveOutBounties(client):
    pass
    # give all signed up members their bounties, maybe every week, as a dm?
    # that'd be a way to have it run weekly https://stackoverflow.com/questions/43670224/python-to-run-a-piece-of-code-at-a-defined-time-every-day

def startTournament():
    pass


def saveAsGlobalVar(name, value):
    if not os.path.exists('functions/bounties/channelIDs.pickle'):
        file = {}
    else:
        with open('functions/bounties/channelIDs.pickle', "rb") as f:
            file = pickle.load(f)

    file[name] = value

    with open('functions/bounties/channelIDs.pickle', "wb") as f:
        pickle.dump(file, f)

