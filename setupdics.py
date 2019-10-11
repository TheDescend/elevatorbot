import requests, zipfile, os, pickle, json, sqlite3

getNameFromHashRecords = {}
getNameFromHashActivity= {}
getNameFromHashCollectible = {}

def getManifest():
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

def fillDictFromDB(dictRef, table):
    if not os.path.exists(table + '.json'): 
        if not os.path.exists('Manifest.content'):
            getManifest()
        con = sqlite3.connect('manifest.content')
        cur = con.cursor()


        cur.execute(
        '''SELECT 
            json
        FROM 
        ''' + table
        )
        items = cur.fetchall()
        item_jsons = [json.loads(item[0]) for item in items]
        con.close()
        for ijson in item_jsons:
            if 'name' in ijson['displayProperties'].keys():
                dictRef[ijson['hash']] = ijson['displayProperties']['name']
        with open(table + '.json', 'w') as outfile:
            json.dump(dictRef, outfile)
    else:
        with open(table + '.json') as json_file:
            dictRef.update(json.load(json_file))

fillDictFromDB(getNameFromHashRecords, 'DestinyRecordDefinition')
fillDictFromDB(getNameFromHashActivity, 'DestinyActivityDefinition')
fillDictFromDB(getNameFromHashCollectible, 'DestinyCollectibleDefinition')