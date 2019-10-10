import requests, zipfile, os, pickle, json, sqlite3, pandas, openpyxl, xlsxwriter
import config, setupdics

from setupdics import getNameFromHashActivity, getNameFromHashRecords, getNameFromHashAchievements, getNameFromHashUnlocks

# from https://data.destinysets.com/
requirementHashes = {
    'Y1':{
        'Levi':[]
    },
    'Y2':{
        'Crown': [
            {'clears' : 15,
            'actHash' : '3333172150'}, #• Minimum 15 full clears
            '1575460004', #• Limited Blessings
            '1575460003', #• Total Victory
            '1575460002'#• With Both Hands
        ],
        'Crown Master': [
            {'clears' : 30,
            'actHash' : '3333172150'}, #• Minimum 15 full clears
            '1558682416', #Crown of Ease [Flawless]
            '1558682417', #• Arc Borne :Arc: 
            '1558682418', #• Void Borne :Void: 
            '1558682419', #• Solar Borne :Solar: 
            '1558682428' #• Stay Classy [Same Class]
        ],
        'Scourge': [
            {'clears' : 15,
            'actHash' : '548750096'},
            '1428463716', #All for one, one for all
            '1804999028', #hold the line
            '4162926221'  #to each their own
        ],

        'ScourgeMaster': [
            {'clears' : 30,
            'actHash' : '548750096'},
            '2648109757', #Like a diamond
            '772878705',  #solarstruck
            '496309570',  #voidstruck
            '105811740',  #thunderstruck
            '3780682732',  #stay classy
            ],
        'Last Wish':[
            {'clears' : 15,
            'actHash' : '2122313384'},   #• Minimum 15 full clears
        '2822000740', #• Summoning Ritual
        '2196415799', #• Coliseum Champion
        '1672792871', #• Forever Fight
        '149192209', #• Keep Out
        '3899933775' #• Strength of Cheesery
        ],

        'Last Wish Master': [
            {'clears' : 15,
            'actHash' : '2122313384'}, #Minimum 30 full clears
            '4177910003', #Petra's Run [Flawless]
            '3806804934', #Thunderstruck :Arc:
            '567795114', #The New Meta [Same Class]
            '1373122528', #Night Owl :Void:
            '2398356743' #Sunburn :Solar:
        ]
    },
    'Y3': {
        'Garden':[],
        'Garden Master':[]
    }

}


baseURL = "https://www.bungie.net/Platform"
PARAMS = {'X-API-Key': config.key}
writer = pandas.ExcelWriter('clanAchievements.xlsx', engine='xlsxwriter')

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
    notfound = -1
    for activity in activities:
        if str(activity['activityHash']) == str(activityHash):
            #print(activity['values'])
            return activity['values']['fullClears'] or 0
        else:
            notfound = 0
    print('didn''t find ' + str(activityHash) + ' in activitylist for ''getClearCount'' of ' + str(userid) +'')
    return notfound

def getHashesFromNameActivity(activityname, guided = False):
    listh = []
    for key in getNameFromHashActivity:
        if getNameFromHashActivity[key] == activityname:
            listh.append(key)
    return listh

#addtional entries for guided games, but who needs that
scourgeHash = '548750096' #getHashesFromNameActivity('Scourge of the Past')
lwHash = '2122313384' #getHashesFromNameActivity('Last Wish: Level 55')
cosHash = '3333172150' #getHashesFromNameActivity('Crown of Sorrow: Normal')

# print(scourgeHash) ['2812525063', '548750096']
#print(getClearCount(4611686018484825875, scourgeHash[1]))
# print(lwHash) ['2214608157', '2122313384']
#print(getClearCount(4611686018484825875, lwHash[1]))
#print(cosHash) ['3333172150', '960175301']
#print(getClearCount(4611686018484825875, cosHash[0]))

requestURL = "/GroupV2/2784110/members/" #bloodoak memberlist
memberJSON = getJSONfromURL(requestURL)
memberlist = memberJSON['Response']['results']
memberids = dict()
for member in memberlist:
    memberids[member['destinyUserInfo']['LastSeenDisplayName']] = member['destinyUserInfo']['membershipId']

# memberids['Hali'] is my destinyMembershipID
userTriumphs = {}
for year in requirementHashes:
    result = {}
    for username, userid in memberids.items():
        print(year + ' processing user: ' + username + ' with id ' + userid)
        if str(userid) in userTriumphs.keys():
            triumphs = userTriumphs[str(userid)]
        else:
            requestURL = "/Destiny2/3/Profile/" + userid + "?components=900" #3 = steam
            achJSON = getJSONfromURL(requestURL)

            triumphs = achJSON['Response']['profileRecords']['data']['records']
            userTriumphs[str(userid)] = triumphs
        
        result[username] = {}
        if achJSON is None:
                break
        yearReqs = requirementHashes[year]
        for role in yearReqs:
            roleReqs = yearReqs[role]
            rolestatus = len(roleReqs) > 0
            for rHash in roleReqs:
                if isinstance(rHash, dict):
                    cc = getClearCount(userid, rHash['actHash'])
                    requiredN = rHash['clears']
                    condition = role + ' clears (' + str(requiredN) + ')'
                    result[username][condition] = str(cc >= requiredN) + ' (' + str(cc) + ')'
                    rolestatus &= (str(cc >= requiredN) == 'True')
                    continue

                status = True
                #if rHash in roleReqs:
                name = getNameFromHashRecords[rHash]
                #else:
                #    print('found in unlocks')
                #    name = getNameFromHashUnlocks[rHash]
                for part in triumphs[rHash]['objectives']:
                    status &= (str(part['complete']) == 'True')
                result[username][name] = str(status)
                rolestatus &= (str(status) == 'True')
            result[username][role] = str(rolestatus)

    df = pandas.DataFrame(result)
    df = df.transpose()


    df.to_excel(writer, sheet_name = year + ' Roles')

workbook = writer.book
fat = workbook.add_format({'bold': True})

redBG = workbook.add_format({'bg_color': '#FFC7CE'})
greenBG = workbook.add_format({'bg_color': '#C6EFCE'})

importantColumns = {
    'Y1' : ['A'],
    'Y2' :  ['A','F', 'M','R','X','AE','AK'],
    'Y3' : ['A']
}
color_range = "A2:ZZ300".format(298)

for year in requirementHashes:
    worksheet = writer.sheets[year + ' Roles']
    worksheet.set_column('A:AK', 2)
    for let in importantColumns[year]:
        worksheet.set_column(let +':'+let, 15, fat)
    worksheet.conditional_format(color_range, {'type': 'text',
                                                'criteria': 'containing',
                                                'value': 'False',
                                                'format': redBG})
    worksheet.conditional_format(color_range, {'type': 'text',
                                                'criteria': 'containing',
                                                'value': 'True',
                                                'format': greenBG})
    worksheet.set_zoom(80)
writer.save()
print('excel file created')