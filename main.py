import requests, zipfile, os, sys, pickle, json, sqlite3, pandas, openpyxl, xlsxwriter, time
import config

from dict import *

# pylint: disable=W0223
# pylint: disable=abstract-class-instantiated

globalStart = time.perf_counter()
globalIntervals = globalStart

baseURL = "https://www.bungie.net/Platform"
PARAMS = {'X-API-Key': config.key}
path = os.path.dirname(os.path.abspath(__file__))
writer = pandas.ExcelWriter(path + '\\clanAchievements.xlsx', engine='xlsxwriter') # pylint: disable=W0223

systemdict = {}
jsondict = {}
def getJSONfromURL(requestURL, baseURL=baseURL, console=False, playerid=None):
    if requestURL in jsondict:
        return jsondict[requestURL]
    r = requests.get(url=baseURL + str(requestURL), headers=PARAMS)
    if r.status_code == 200:
        jsondict[requestURL] = r.json()
        return r.json()
    elif r.status_code == 400:
        if console:
            return None
        print(requestURL + ' not on steam')
        for i in [1,2,4,5,10,254]:
            console = getJSONfromURL('/Destiny2/' + str(i) + requestURL[11:], baseURL=baseURL, console=True, playerid = playerid)
            if console is not None:
                print('found on ' + platform.get(i))
                systemdict[playerid] = i
                jsondict[requestURL] = console
                return console
        return None
    else:
        print('request for ' + baseURL + requestURL + ' failed with code ' + str(r.status_code))
    return r.json()

activities = {}

def playerHasCollectible(playerid, cHash, systemid=3):
    if playerid in systemdict:
        systemid = systemdict[playerid]
    userCollectibles = getJSONfromURL('/Destiny2/{}/Profile/{}?components=800'.format(systemid, playerid), playerid=userid)
    collectibles = userCollectibles['Response']['profileCollectibles']['data']['collectibles']
    return collectibles[cHash]['state'] == 0

def getClearCount(playerid, activityHash):
    if not str(playerid) in activities.keys():
        rrBaseURL = 'https://b9bv2wd97h.execute-api.us-west-2.amazonaws.com/prod/api/player/'
        requestURL = playerid
        profileInfo = getJSONfromURL(requestURL, baseURL=rrBaseURL, playerid=userid)
        activities[str(playerid)] = profileInfo['response']['activities']

    notfound = -1
    for activity in activities[str(playerid)]:
        if str(activity['activityHash']) == str(activityHash):
            return activity['values']['fullClears'] or 0
        else:
            notfound = 0
    return notfound

def flawlessList(playerid):
    rrBaseURL = 'https://b9bv2wd97h.execute-api.us-west-2.amazonaws.com/prod/api/player/'
    requestURL = playerid
    profileInfo = getJSONfromURL(requestURL, baseURL=rrBaseURL, playerid=playerid)
    activities = profileInfo['response']['activities']

    flawlessL = []
    for raid in activities:
        if 'flawlessDetails' in raid['values'].keys():
            flawlessL.append(str(raid['activityHash']))
    return flawlessL

def getTriumphsJSON(playerid, system=3):
    if playerid in systemdict:
        system = systemdict[playerid]
    requestURL = "/Destiny2/{}/Profile/{}?components=900".format(system, playerid) 
    achJSON = getJSONfromURL(requestURL, playerid=playerid)
    return achJSON['Response']['profileRecords']['data']['records']

def playerHasTriumph(playerid, recordHash):
    status = True
    triumphs = getTriumphsJSON(playerid)
    for part in triumphs[recordHash]['objectives']:
        status &= (str(part['complete']) == 'True')
    return status

def playerHasClears(playerid, n, raidHashes):
    count = 0
    for h in raidHashes:
        count += getClearCount(playerid, h)
    return count >= n

def playerHasFlawless(playerid, raidHashes):
    flawlessL = flawlessList(userid)
    for r in raidHashes:
        if r in flawlessL:
            return True
    return False

def playerHasRole(playerid, role, year):
    roledata = requirementHashes[year][role]
    if not 'requirements' in roledata:
        print('malformatted requirementHashes')
        return None
    for req in roledata['requirements']:
        if req == 'clears':
            creq = roledata['clears']
            for raid in creq:
                requiredN = raid['count']
                if not playerHasClears(playerid, requiredN, raid['actHashes']):
                    return False
        elif req == 'flawless':
            if not playerHasFlawless(playerid, roledata['flawless']):
                return False
        elif req == 'collectibles':
            for collectible in roledata['collectibles']:
                if not playerHasCollectible(playerid, collectible):
                    return False
        elif req == 'records':
            for recordHash in roledata['records']:
                if not playerHasTriumph(playerid, recordHash):
                    return False
    return True

#print(playerHasRole(4611686018468695677,'Levi Master','Y1'))

requestURL = "/GroupV2/2784110/members/" #bloodoak memberlist
memberJSON = getJSONfromURL(requestURL)
memberlist = memberJSON['Response']['results']
memberids  = dict()
membersystem = dict()
for member in memberlist:
    memberids[member['destinyUserInfo']['LastSeenDisplayName']] = member['destinyUserInfo']['membershipId']

# memberids['Hali'] is my destinyMembershipID
userRoles = {}
for year,yeardata in requirementHashes.items():
    yearResult = {}
    for username, userid in memberids.items():
        if not username in userRoles.keys():
            userRoles[username] = []
        print('Processing user: ' + username + ' with id ' + userid)
        triumphs = getTriumphsJSON(userid)
        yearResult[username] = {}
        
        for role,roledata in yeardata.items():
            rolestatus = len(roledata) > 0
            if not 'requirements' in roledata:
                print('malformatted requirementHashes')
                continue
            for req in roledata['requirements']:
                if req == 'clears':
                    creq = roledata['clears']
                    for raid in creq:
                        requiredN = raid['count']
                        activityname = getNameFromHashActivity[str(raid['actHashes'][0])]
                        condition = activityname + ' clears (' + str(requiredN) + ')'

                        boolHasClears = playerHasClears(userid, requiredN, raid['actHashes'])
                        cc = getClearCount(userid, raid['actHashes'][0])
                        yearResult[username][condition] = str(boolHasClears) + ' (' + str(cc) + ')'
                        rolestatus &= boolHasClears
                elif req == 'flawless':
                    condition = 'flawless ' + getNameFromHashActivity[roledata['flawless'][0]]
                    if playerHasFlawless(userid, roledata['flawless']):
                            yearResult[username][condition] = 'True'
                            found = True
                    else:
                        rolestatus = False
                        yearResult[username][condition] = 'False'
                elif req == 'collectibles':
                    for collectible in roledata['collectibles']:
                        condition = getNameFromHashCollectible[collectible]
                        if playerHasCollectible(userid, collectible):
                            yearResult[username][condition] = 'True'
                        else:
                            yearResult[username][condition] = 'False'
                            rolestatus = False
                elif req == 'records':
                    for recordHash in roledata['records']:
                        condition = getNameFromHashRecords[recordHash]
                        status = playerHasTriumph(userid, recordHash)
                        yearResult[username][condition] = str(status)
                        rolestatus &= (str(status) == 'True')

            yearResult[username][role] = str(rolestatus)
            if rolestatus:
                userRoles[username].append(role)
            else:
                userRoles[username].append('')

    df = pandas.DataFrame(yearResult)
    df = df.transpose()

    df.to_excel(writer, sheet_name = year + ' Roles')

pandas.DataFrame(userRoles).transpose().to_excel(writer, header=None, sheet_name = 'User Roles')
workbook = writer.book
fat = workbook.add_format({'bold': True})

redBG = workbook.add_format({'bg_color': '#FFC7CE'})
greenBG = workbook.add_format({'bg_color': '#C6EFCE'})

importantColumns = {
    'Y1'  : ['A','D','G','J','M','P','W'],
    'Y2'  : ['A','F', 'M','R','X','AE','AK'],
    'Y3'  : ['A']
}

worksheet = writer.sheets['User Roles']
worksheet.set_column('A:A', 15, fat)
worksheet.set_column('B:M', 6, fat)

for year in requirementHashes:
    worksheet = writer.sheets[year + ' Roles']
    worksheet.set_column('A:AK', 2)
    for let in importantColumns[year]:
        worksheet.set_column(let +':'+let, 15, fat)
    worksheet.conditional_format("A2:ZZ300", {'type': 'text',
                                                'criteria': 'containing',
                                                'value': 'False',
                                                'format': redBG})
    worksheet.conditional_format("A2:ZZ300", {'type': 'text',
                                                'criteria': 'containing',
                                                'value': 'True',
                                                'format': greenBG})
    worksheet.set_zoom(80)
writer.save()
print('excel file created')