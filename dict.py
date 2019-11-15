import requests, zipfile, os, pickle, json, sqlite3


getNameFromHashRecords = {}
getNameFromHashActivity= {}
getNameFromHashCollectible = {}

# from https://data.destinysets.com/
spirePHashes = [3213556450]
spireHashes = [119944200]
eaterPHashes = [809170886]
eaterHashes = [3089205900]
leviHashes = [2693136600,2693136601,2693136602,2693136603,2693136604,2693136605] #there's like 12 of each
leviPHashes = [417231112,508802457,757116822, 771164842, 1685065161, 1800508819, 2449714930,3446541099,3857338478,3879860661, 3912437239,4206123728]
scourgeHashes = [548750096] 
lwHashes = [2122313384]
cosHashes = [3333172150] 
gosHashes = [3845997235,2659723068]

clanids = [
    2784110, #Bloodoak I
    3373405, #BO2
    3702604, #BO3
    3702604, #Ascend Kappa
]


requirementHashes = {
    'Y1':{
        'Spire of Stars': {
            'requirements': ['clears'],
            'clears': [
                {'count' : 4,
                'actHashes' : spireHashes}, #normal
                {'count' : 2,
                'actHashes' : spirePHashes} #prestige 
            ],
            'replaced_by': 'Spire of Stars Master'
        },
        'Spire of Stars Master': {
            'requirements': ['clears','flawless'],
            'clears': [
                {'count' : 15,
                'actHashes' : spirePHashes}  #prestige
            ],
            'flawless' : spireHashes + spirePHashes
        },
        'Eater of Worlds': {
            'requirements': ['clears'],
            'clears': [
                {'count' : 4,
                'actHashes' : eaterHashes}, #normal
                {'count' : 2,
                'actHashes' : eaterPHashes} #prestige
            ],
            'replaced_by':'Eater of Worlds Master'
        },
        'Eater of Worlds Master': {
            'requirements': ['clears','flawless'],
            'clears': [
                {'count' : 15,
                'actHashes' : eaterPHashes}
            ], #prestige
            'flawless': eaterHashes + eaterPHashes
        },
        'Leviathan': {
            'requirements': ['clears'],
            'clears': [
                {'count' : 4,
                'actHashes' : leviHashes}, #normal
                {'count' : 2,
                'actHashes' : leviPHashes} #prestige
            ],
            'replaced_by': 'Leviathan Master'
        },
        'Leviathan Master': {
            'requirements': ['clears','flawless','collectibles'],
            'clears':[
                {'count' : 15,
                'actHashes' : leviPHashes}, #prestige
            ],
            'flawless': leviHashes + leviPHashes,
            'collectibles': [
                1766893932, #good dog
                1766893933, #splish splash
                1766893935, #two enter, one leaves
                1766893934  #take the throne
            ]
        }
    },
    'Y2':{
        'Crown of Sorrow': {
            'requirements': ['clears','records'],
            'clears':[
                {'count' : 15,
                'actHashes' : cosHashes}
            ], #• Minimum 15 full clears
            'records': [
                1575460004,    #Limited Blessings
                1575460003,    #Total Victory
                1575460002,    #With Both Hands
           ],
           'replaced_by': 'Crown of Sorrow Master'
       },
        'Crown of Sorrow Master': {
            'requirements': ['clears','records'],
            'clears': [
                {'count' : 30,
                'actHashes' : cosHashes} #Minimum 15 full clears
            ],
            'records': [
                1558682416,    #Crown of Ease [Flawless]
                1558682417,    #Arc Borne :Arc: 
                1558682418,    #Void Borne :Void: 
                1558682419,    #Solar Borne :Solar: 
                1558682428    #Stay Classy [Same Class]
            ]
        },
        'Scourge of the Past': {
            'requirements': ['clears','records'],
            'clears': [
                {'count' : 15,
                'actHashes' : scourgeHashes}
            ],
            'records':[
                1428463716,    #All For One, One For All
                1804999028,    #Hold the Line
                4162926221,    #To Each Their Own
            ],
            'replaced_by':'Scourge of the Past Master'
        },
        'Scourge of the Past Master': {
            'requirements': ['clears','records'],
            'clears': [
                {'count' : 30,
                'actHashes' : scourgeHashes}
            ],
            'records': [
                2648109757,    #Like a Diamond
                772878705,     #Solarstruck
                496309570,     #Voidstruck
                105811740,     #Thunderstruck
                3780682732,    #Stay Classy
            ]
        },
        'Last Wish':{
            'requirements': ['clears','records'],
            'clears' :[
                {'count' : 15,
                'actHashes' : lwHashes},   #Minimum 15 full clears
            ],
            'records':[
                2822000740,    #Summoning Ritual
                2196415799,    #Coliseum Champion
                1672792871,    #Forever Fight
                149192209,     #Keep Out
                3899933775    #Strength of Memory
            ],
            'replaced_by':'Last Wish Master'
        },
        'Last Wish Master': {
            'requirements': ['clears','records'],
            'clears': [
                {'count' : 30,
                'actHashes' : lwHashes}
            ], #Minimum 15 full clears
            'records': [
                4177910003,    #Petra's Run [Flawless]
                3806804934,    #Thunderstruck :Arc:
                567795114,     #The New Meta [Same Class]
                1373122528,    #Night Owl :Void:
                2398356743    #Sunburn :Solar:
            ]
        }
 },
    'Y3':{
        'Garden': {
            'requirements': ['clears','records'],
            'clears':[
                {'count' : 15,
                'actHashes' : gosHashes} #Minimum 15 full clears
            ], 
            'records': [
                3281243931, #Leftovers
                1925300422, #A Link to the Chain
                1661612473, #To the Top
                3167166053, #Zero to One Hundred
            ],
            'replaced_by':'Garden Master'
       },
        'Garden Master': {
            'requirements': ['clears','records'],
            'clears': [
                {'count' : 30,
                'actHashes' : gosHashes} #Minimum 30 full clears
            ],
            'records': [
                3144827156, #Inherent Perfection [Flawless]
                2841179989, #Fluorescent Foliage :Arc: 
                4019629605, #Shade in the Garden :Void: 
                3382024472, #Photosynthesis :Solar: 
                4025379205, #Garden Party [Same Class]
            ]
        }
    },
    'Addition':{
        'Niobe\'s Torment': {
            'requirements': ['collectibles'],
            'collectibles': [
                3531075476, #Armory Forged Shell
            ]
        },
        'Solo Flawless Shattered Throne': {
            'requirements': ['records'],
             'records': [
                1290451257, #Solo Flawless Shattered Throne
            ]
        },
        'Flawless Shattered Throne': {
            'requirements': ['records'],
            'records': [
                2029263931, #Flawless Shattered Throne
            ],
            'replaced_by':'Solo Flawless Shattered Throne'
        },
        'Solo Shattered Throne': {
            'requirements': ['records'],
            'records': [
                851701008, #Solo Shattered Throne
            ],
            'replaced_by':'Solo Flawless Shattered Throne'
        }
        #'Name': {
        #    'requirements': ['collectibles'],
        #    'collectibles': [
        #        hash #comment
        #    ]
        #}
    }
}

platform = {
    1: 'Xbox',
    2: 'Playstation',
    3: 'Steam',
    4: 'Blizzard',
    5: 'Stadia',
    10: 'Demon',
    254: 'BungieNext'
}

def getManifest():
    manifest_url = 'http://www.bungie.net/Platform/Destiny2/Manifest/'
    binaryLocation = "cache/MANZIP"
    os.makedirs(os.path.dirname(binaryLocation), exist_ok=True)

    #get the manifest location from the json
    r = requests.get(manifest_url)
    manifest = r.json()
    mani_url = 'http://www.bungie.net' + manifest['Response']['mobileWorldContentPaths']['en']

    #Download the file, write it to 'MANZIP'
    r = requests.get(mani_url)
    with open(binaryLocation, "wb") as zip:
        zip.write(r.content)

    #Extract the file contents, and rename the extracted file to 'Manifest.content'
    with zipfile.ZipFile(binaryLocation) as zip:
        name = zip.namelist()
        zip.extractall()
    os.rename(name[0], 'cache/Manifest.content')

def fillDictFromDB(dictRef, table):
    if not os.path.exists('cache/' + table + '.json'): 
        if not os.path.exists('cache/Manifest.content'):
            getManifest()

        #Connect to DB
        con = sqlite3.connect('cache/Manifest.content')
        cur = con.cursor()

        #Query the DB
        cur.execute(
        '''SELECT 
            json
        FROM 
        ''' + table
        )
        items = cur.fetchall()
        item_jsons = [json.loads(item[0]) for item in items]
        con.close()

        #Iterate over DB-JSONs and put named ones into the corresponding dictionary
        for ijson in item_jsons:
            if 'name' in ijson['displayProperties'].keys():
                dictRef[ijson['hash']] = ijson['displayProperties']['name']
        with open('cache/' + table + '.json', 'w') as outfile:
            json.dump(dictRef, outfile)
    else:
        with open('cache/' + table + '.json') as json_file:
            dictRef.update(json.load(json_file))

fillDictFromDB(getNameFromHashRecords, 'DestinyRecordDefinition')
fillDictFromDB(getNameFromHashActivity, 'DestinyActivityDefinition')
fillDictFromDB(getNameFromHashCollectible, 'DestinyCollectibleDefinition')
