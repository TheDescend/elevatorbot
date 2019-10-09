
import requests, zipfile, os, pickle, json, sqlite3

if not os.path.exists('Manifest.content'):
    manifest_url = 'http://www.bungie.net/Platform/Destiny2/Manifest/'

    #get the manifest location from the json
    r = requests.get(manifest_url)
    manifest = r.json()
    #print(manifest['Response'].keys())
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

getHashFromNameRecords = {}
getHashFromNameActivity = {}

if not os.path.exists('achievements.json'):
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

    for ijson in item_jsons:
        getHashFromNameRecords[ijson['displayProperties']['name']] = ijson['hash']
    
    with open('achievements.json', 'w') as outfile:
        json.dump(getHashFromNameRecords, outfile)
else:
    with open('achievements.json') as json_file:
        getHashFromNameRecords = json.load(json_file)



if not os.path.exists('activities.json'):
    con = sqlite3.connect('manifest.content')
    cur = con.cursor()

    cur.execute(
    '''SELECT 
        json
    FROM 
        DestinyActivityDefinition
    ''')
    items = cur.fetchall()
    #print(items)
    item_jsons = [json.loads(item[0]) for item in items]

    for ijson in item_jsons:
        getHashFromNameActivity[ijson['displayProperties']['name']] = ijson['hash']
    
    with open('activities.json', 'w') as outfile:
        json.dump(getHashFromNameActivity, outfile)
else:
    with open('activities.json') as json_file:
        getHashFromNameActivity = json.load(json_file)