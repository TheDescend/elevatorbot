from functions import getPlayersPastPVE, getPGCR, getJSONfromURL
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import BUNGIE_TOKEN
import pandas as pd
import requests
import json
import matplotlib.pyplot as plt
from decimal import Decimal
import os
plt.rcParams['backend'] = "Qt4Agg"

bungieAPI_URL = "https://www.bungie.net/Platform"
PARAMS = {'X-API-Key': BUNGIE_TOKEN}
dummy = None
session = requests.Session()

centerNodeDestinyID = 4611686018468433098
edges = pd.DataFrame(columns=['from', 'to', 'weight'])

charURL = "https://stats.bungie.net/Platform/Destiny2/3/Profile/{}/?components=100,200"
characterinfo = None
platform = None
characterinfo = session.get(url=charURL.format(centerNodeDestinyID), headers=PARAMS).json()
charIDs = characterinfo['Response']['characters']['data'].keys()
activitylist = []
for characterID in charIDs:
    for pagenr in range(100):
        staturl = f"https://www.bungie.net/Platform/Destiny2/3/Account/{centerNodeDestinyID}/Character/{characterID}/Stats/Activities/?mode=4&count=250&page={pagenr}" 
        # None	0 Everything
        # Story	2	 
        # Strike	3	 
        # Raid	4	 
        # AllPvP	5	 
        # Patrol	6	 
        # AllPvE	7	
        rep = session.get(url=staturl, headers=PARAMS).json()
        if not rep or not rep['Response'] or 'activities' not in rep['Response']:
            #no more data found for the character, moving on to next
            break
        activitylist += rep['Response']['activities']
if not os.path.exists('raiddata'):
    os.mkdir('raiddata')

#save for safety
with open(f'raiddata/{centerNodeDestinyID}.activitylist', 'w') as f:
    f.write(json.dumps(activitylist))

#only account for completed activities
completedacts = []
for act in activitylist:
    if act['values']['completed']['basic']['value'] == 1:
        completedacts.append(act)

#get all ids needed for the pgcr reports
instanceIds = [act['activityDetails']['instanceId'] for act in completedacts]

#aquire all the pgcr data
pgcrlist = []
for instanceId in instanceIds:
    pgcrurl = f'https://www.bungie.net/Platform/Destiny2/Stats/PostGameCarnageReport/{instanceId}/'
    pgcrlist += session.get(url=staturl, headers=PARAMS).json()['Response']['entries']

#extract partners from pgcrlist
partners = []
for char in pgcrlist:
    user = char['player']['destinyUserInfo']
    partners.append((user['membershipId'],user['displayName']))

#put them into a dataframe, group by unique users and count the common raids
df = pd.DataFrame(partners,columns=['destinyid','username'])
count = df.groupby(['destinyid','username']).size().reset_index(name='counts')
sortedcount = count.sort_values('counts', ascending=False)
#smallsample = sortedcount.drop(sortedcount.index[0]).nlargest(20,'counts')

if not os.path.exists('frienddata'):
    os.mkdir('frienddata')
sortedcount['from'] = [centerNodeDestinyID]*len(sortedcount.index)
sortedcount.to_pickle(f'/friendata/{centerNodeDestinyID}.dataframe')
print(sortedcount)
print('\n\n')
outputedge = pd.DataFrame(columns=['from', 'to', 'weight'])
outputedge['from'] = sortedcount['from']
outputedge['to'] = sortedcount['destinyid']
outputedge['weight'] = sortedcount['counts']
edges.append(sortedcount, verify_integrity = True)
print(edges)


# smallsample.plot(x='username', y='counts', kind='bar')
# plt.gcf().subplots_adjust(bottom=0.4)
# plt.savefig('img.png')
# print('done')

