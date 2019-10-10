import requests, zipfile, os, pickle, json, sqlite3, pandas
import config, setupdics

from setupdics import getNameFromHashActivity, getNameFromHashRecords, getNameFromHashAchievements, getNameFromHashUnlocks


requirementHashesScourge = [
    '1428463716', #All for one, one for all
    '1804999028', #hold the line
    '4162926221'  #to each their own
    ]

requirementHashesScourgeMaster = [
    '2648109757', #Like a diamond
    '772878705',  #solarstruck
    '496309570',  #voidstruck
    '105811740',  #thunderstruck
    '3780682732'  #stay classy
]

baseURL = "https://www.bungie.net/Platform"
PARAMS = {'X-API-Key': config.key}


def getJSONfromURL(requestURL):
    r=requests.get(url=baseURL + requestURL, headers=PARAMS)
    while(r.json()['ErrorCode'] > 1):
        r=requests.get(url=baseURL + requestURL, headers=PARAMS)
        print(r.json()['ErrorCode'])

    return r.json()

#all_data = {}
#for every table name in the dictionary

def getClearCount(playerid, activityHash):
    requestURL = "/Destiny2/3/Profile/" + playerid + "?components=100" #3 = steam
    profileInfo = getJSONfromURL(requestURL)
    characterids = profileInfo['Response']['profile']['data']['characterIds']
    
    count = 0
    for charid in characterids:
        requestURL = '/Destiny2/3/Account/'+ playerid + '/Character/' + charid + '/Stats/AggregateActivityStats/'
        memberJSON = getJSONfromURL(requestURL)['Response']['activities'] # acitivityHash & values
        for activity in memberJSON:
            if str(activity['activityHash']) == str(activityHash):
                count += int(activity['values']['activityCompletions']['basic']['value'])
    return count

def getHashesFromNameActivity(activityname, guided = False):
    listh = []
    for key in getNameFromHashActivity:
        if getNameFromHashActivity[key] == activityname:
            listh.append(key)
    return listh

scourgeHash = getHashesFromNameActivity('Scourge of the Past')
lwHash = getHashesFromNameActivity('Last Wish: Level 55')
cosHash = getHashesFromNameActivity('Crown of Sorrow: Normal')

#print(getNameFromHashRecords['105811740'])
#print(scourgeHash)

requestURL = "/GroupV2/2784110/members/" #bloodoak memberlist
memberJSON = getJSONfromURL(requestURL)
memberlist = memberJSON['Response']['results']
memberids = dict()
for member in memberlist:
    memberids[member['destinyUserInfo']['LastSeenDisplayName']] = member['destinyUserInfo']['membershipId']

# memberids['Hali'] is my destinyMembershipID
result = {}
for username, userid in memberids.items():
    requestURL = "/Destiny2/3/Profile/" + userid + "?components=900" #3 = steam
    achJSON = getJSONfromURL(requestURL)

    triumphs = achJSON['Response']['profileRecords']['data']['records']
    getCompletenessByTriumphHash = {}

    result[username] = {}

    clearcount = getClearCount(userid, scourgeHash[0]) + getClearCount(userid, scourgeHash[1]) #guided and not-guided
    result[username]['Scourge Completions'] = clearcount

    status = True
    for req in requirementHashesScourge:
        if req in getNameFromHashRecords:
            name = getNameFromHashRecords[req]
        else:
            name = getNameFromHashUnlocks[req]
        for part in triumphs[req]['objectives']:
            status &= bool(part['complete'])
        result[username][name] = str(status)
        
    status = True
    for req in requirementHashesScourgeMaster:
        name = getNameFromHashRecords[req]
        for part in triumphs[req]['objectives']:
            status &= bool(part['complete'])
        result[username][name] = str(status)

print(result)
print()
df = pandas.DataFrame(result)
df = df.transpose()
print(df)
df.to_excel(index=False)