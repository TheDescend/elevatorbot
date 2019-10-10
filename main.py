import requests, zipfile, os, pickle, json, sqlite3, pandas, openpyxl
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

platform = {
    1: 'Xbox',
    2: 'Playstation',
    3: 'Steam',
    4: 'Blizzard',
    5: 'Stadia',
    10: 'Demon',
    254: 'BungieNext'
}

def getJSONfromURL(requestURL, baseURL=baseURL, console=False):
    r=None
    while(r == None or r.status_code != requests.codes[r'\o/']):
        try:
            #print('trying to get ' + str(baseURL) + str(requestURL))
            r = requests.get(url=baseURL + str(requestURL), headers=PARAMS)
            if r.status_code == 200:
                break
            if r.status_code == 400:
                if console:
                    return None
                print(requestURL + ' not on steam')
                for i in [1,2,4,5,10,254]:
                    #print('/Destiny2/' + str(i) + requestURL[11:])
                    console = getJSONfromURL('/Destiny2/' + str(i) + requestURL[11:], baseURL=baseURL, console=True)
                    if console is not None:
                        print('found on ' + platform.get(i))
                        return console
                return None
            else:#
                print(r.status_code)

        except requests.exceptions.RequestException as e:
            print(e)
            print('getting ' + baseURL + requests + ' failed')
            r=None

    return r.json()

#j = getJSONfromURL('/Destiny2/3/Profile/4611686018432289116?components=900')
#print(j)
#all_data = {}
#for every table name in the dictionary

def getClearCount(playerid, activityHash):
    rrBaseURL = 'https://b9bv2wd97h.execute-api.us-west-2.amazonaws.com/prod/api/player/'
    #requestURL = "/Destiny2/3/Profile/" + playerid + "?components=100" #3 = steam
    requestURL = playerid
    profileInfo = getJSONfromURL(requestURL, baseURL=rrBaseURL)
    activities = profileInfo['response']['activities']
    #characterids = profileInfo['response']['profile']['data']['characterIds']
    
    #count = 0
    #for charid in characterids:
    #    requestURL = '/Destiny2/3/Account/'+ playerid + '/Character/' + charid + '/Stats/AggregateActivityStats/'
    #    memberJSON = getJSONfromURL(requestURL)['Response']['activities'] # acitivityHash & values
    #    for activity in memberJSON:
    #        if str(activity['activityHash']) == str(activityHash):
    #            count += int(activity['values']['activityCompletions']['basic']['value'])
    for activity in activities:
        if str(activity['activityHash']) == str(activityHash):
            #print(activity['values'])
            return activity['values']['fullClears'] or 0

def getHashesFromNameActivity(activityname, guided = False):
    listh = []
    for key in getNameFromHashActivity:
        if getNameFromHashActivity[key] == activityname:
            listh.append(key)
    return listh

scourgeHash = getHashesFromNameActivity('Scourge of the Past')
lwHash = getHashesFromNameActivity('Last Wish: Level 55')
cosHash = getHashesFromNameActivity('Crown of Sorrow: Normal')

# print(scourgeHash) ['2812525063', '548750096']
#print(getClearCount(4611686018484825875, scourgeHash[1]))
# print(lwHash) ['2214608157', '2122313384']
#print(getClearCount(4611686018484825875, lwHash[1]))
# print(cosHash) ['3333172150', '960175301']
#print(getClearCount(4611686018484825875, cosHash[0]))

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
    print('processing user: ' + username + ' with id ' + userid)
    requestURL = "/Destiny2/3/Profile/" + userid + "?components=900" #3 = steam
    achJSON = getJSONfromURL(requestURL)
    if achJSON is None:
        result[username] = {}
        continue

    triumphs = achJSON['Response']['profileRecords']['data']['records']
    getCompletenessByTriumphHash = {}

    result[username] = {}

    clearcount = getClearCount(userid, scourgeHash[1]) #guided and not-guided
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

#print(result)
#print()
df = pandas.DataFrame(result)
df = df.transpose()
print(df)
df.to_excel('clanAchievements.xlsx')