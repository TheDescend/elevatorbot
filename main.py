import requests, zipfile, os, pickle, json, sqlite3
import config
import setupdics
from setupdics import getHashFromNameActivity, getHashFromNameRecords

requirements = ['Like a Diamond', 'All for One, One for All', 'Hold the Line', 'To Each Their Own','Solarstruck']
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
    for _ in range(0,10):
        r=requests.get(url=baseURL + requestURL, headers=PARAMS)
        if r is not None:
            break
    return r.json()

#all_data = {}
#for every table name in the dictionary

def getClearCount(playerid):
    requestURL = "/Destiny2/3/Profile/" + playerid + "?components=100" #3 = steam
    profileInfo = getJSONfromURL(requestURL)
    characterids = profileInfo['Response']['profile']['data']['characterIds']
    
    for charid in characterids:
        requestURL = '/Destiny2/3/Account/'+ playerid + '/Character/' + charid + '/Stats/AggregateActivityStats/'
        memberJSON = getJSONfromURL(requestURL)['Response']['activities'] # acitivityHash & values
        print(memberJSON[0])
        break

getNameFromHashRecords = {str(v): k for k, v in getHashFromNameRecords.items()}
getNameFromHashActivities = {str(v): k for k, v in getHashFromNameActivity.items()}

requestURL = "/GroupV2/2784110/members/" #bloodoak memberlist
memberJSON = getJSONfromURL(requestURL)
memberlist = memberJSON['Response']['results']
memberids = dict()
for member in memberlist:
    memberids[member['destinyUserInfo']['LastSeenDisplayName']] = member['destinyUserInfo']['membershipId']

# memberids['Hali'] is my destinyMembershipID

userid = memberids['Hali']

getClearCount(userid)

requestURL = "/Destiny2/3/Profile/" + userid + "?components=900" #3 = steam
#print(requestURL)
achJSON = getJSONfromURL(requestURL)

triumphs = achJSON['Response']['profileRecords']['data']['records']

getCompletenessByTriumphHash = {}

#hashreqs = {str(getHashFromName[req]):req for req in requirements}
#print(hashreqs.keys())

for req in requirementHashesScourge:
    name = getNameFromHashRecords[req]
    status = triumphs[req]['objectives'][0]['complete']

    print('Hali' + ';' + name + ';' + str(status))
#for t in triumphs:
#    if str(t) in hashreqs.keys():
#        if bool(triumphs[t]['objectives'][0]['complete']):
#            print('Hali' + ' has completed the triumph ' + hashreqs[str(t)])
#        else:
#            print('Hali' + ' has not completed the triumph ' + hashreqs[str(t)])
#    
#    curT = triumphs[t]
#    if 'objectives' in curT:
#        complete = bool(curT['objectives'][0]['complete'])
#        tHash = curT['objectives'][0]['objectiveHash'] #iterate over 0?
#        #print(tHash)
#        if str(tHash) in getNameFromHash.keys():
#            print(getNameFromHash[str(tHash)])
#
        #getCompletenessByTriumphHash[tHash] = complete

#print(getHashFromName.keys())

#for req in requirements:
#    reqHash = getHashFromName[req]
#    if getCompletenessByTriumphHash[reqHash]:
#        print('Hali' + ' has completed the triumph ' + req)
#    else:
#        print('Hali' + ' has not completed the triumph ' + req)
print('done')

#/Destiny/{membershipType}/Account/{destinyMembershipId}/Triumphs/
#/Destiny2/{membershipType}/Profile/{destinyMembershipId}/'''