import requests, zipfile, os, pickle, json, sqlite3
  
baseURL = "https://www.bungie.net/Platform"
PARAMS = {'X-API-Key':'3743ea53f4014677a36be515239869b3'}

def getJSONfromURL(requestURL):
    r=requests.get(url=baseURL + requestURL, headers=PARAMS)
    return r.json()

def get_manifest():
    if not os.path.exists('Manifest.content'):
        manifest_url = 'http://www.bungie.net/Platform/Destiny2/Manifest/'

        #get the manifest location from the json
        r = requests.get(manifest_url)
        manifest = r.json()
        print(manifest['Response'].keys())
        mani_url = 'http://www.bungie.net'+manifest['Response']['mobileWorldContentPaths']['en']

        #Download the file, write it to 'MANZIP'
        r = requests.get(mani_url)
        with open("MANZIP", "wb") as zip:
            zip.write(r.content)
        #print("Download Complete!")

        #Extract the file contents, and rename the extracted file
        # to 'Manifest.content'
        with zipfile.ZipFile('MANZIP') as zip:
            name = zip.namelist()
            zip.extractall()
        os.rename(name[0], 'Manifest.content')
    con = sqlite3.connect('manifest.content')
    cur = con.cursor()

    cur.execute(
    '''SELECT 
        json
    FROM 
        DestinyRecordDefinition
    ''')
    items = cur.fetchall()
    #print(items)
    item_jsons = [json.loads(item[0]) for item in items]
    getHashFromName = []
    for ijson in item_jsons:
        getHashFromName[ijson['displayProperties']['name']] = ijson['hash']
    return getHashFromName
    #all_data = {}
    #for every table name in the dictionary
   
getHashFromName = get_manifest()
exit(0)

requestURL = "/GroupV2/2784110/members/" #bloodoak memberlist
memberJSON = getJSONfromURL(requestURL)
memberlist = memberJSON['Response']['results']
memberids = dict()
for member in memberlist:
    memberids[member['destinyUserInfo']['LastSeenDisplayName']] = member['destinyUserInfo']['membershipId']

# memberids['Hali'] is my destinyMembershipID

testid = memberids['Hali']
requestURL = "/Destiny2/3/Profile/" + testid + "?components=100" #3 = steam
profileInfo = getJSONfromURL(requestURL)
characterids = profileInfo['Response']['profile']['data']['characterIds']
#print(characterids)

userid = memberids['Hali']
requestURL = "/Destiny2/3/Profile/" + userid + "?components=900" #3 = steam
achJSON = getJSONfromURL(requestURL)

triumphs = achJSON['Response']['profileRecords']['data']['records']

for t in triumphs:
    curT = triumphs[t]

    complete = bool(curT['objectives'][0]['complete'])
    tHash = curT['objectives'][0]['objectiveHash'] #iterate over 0?
    print(tHash)
    
    break

    
#check


#/Destiny/{membershipType}/Account/{destinyMembershipId}/Triumphs/
#/Destiny2/{membershipType}/Profile/{destinyMembershipId}/'''