from functions.database     import getToken, lookupDiscordID
from oauth                  import refresh_token
from static.config          import BUNGIE_TOKEN
from functions.network      import getJSONfromURL
from static.dict            import getNameFromHashInventoryItem

import requests
session = requests.Session()

def getJSONwithToken(url, discordID):
    """ Takes url and discordID, returns JSON """

    token = getToken(discordID)
    if not token:
        return None
    #print(f'using {token}')
    headers = {'Authorization': f'Bearer {token}', 'x-api-key': BUNGIE_TOKEN, 'Accept': 'application/json'}
    r = session.get(url, headers = headers)
    
    if b'Unauthorized' in r.content:
        print('xml 401 found')
        refresh_token(discordID)
        return getJSONwithToken(url, discordID)
    
    res = r.json()

    if int(res['ErrorCode']) == 401:
        print('json 401 found')
        refresh_token(discordID)
        return getJSONwithToken(url, discordID)
    
    if int(res['ErrorCode']) != 1:
        print(f'ErrorCode is not 1, but {res["ErrorCode"]}')
        return None

    #print(f'Tokenfunction returned {res}')
    return res

def getUserMaterials(destinyID):
    system = 3
    url = f'https://stats.bungie.net/Platform/Destiny2/{system}/Profile/{destinyID}/?components=600'
    res = getJSONwithToken(url, lookupDiscordID(destinyID))
    if not res:
        return None
    materialdict = list(res['Response']['characterCurrencyLookups']['data'].values())[0]['itemQuantities']
    return materialdict

def getSpiderMaterials(discordID, destinyID, characterID):
    """ Gets spiders current selling inventory, requires OAuth"""

    system = 3 #they're probably on PC
    #863940356 is spiders vendorID
    url = f'https://www.bungie.net/Platform/Destiny2/{system}/Profile/{destinyID}/Character/{characterID}/Vendors/863940356/?components=400,401,402'
    res = getJSONwithToken(url, discordID)
    if not res:
        print('result was none')
        return None
    #gets the dictionary of sold items
    sales = res['Response']['sales']['data']
    itemhashurl = 'https://bungie.net/platform/Destiny2/Manifest/DestinyInventoryItemDefinition/{hashIdentifier}/'
    returntext = ''
    usermaterialdict = getUserMaterials(destinyID)
    usermaterialreadabledict = {}
    #print(getNameFromHashInventoryItem.keys())
    for key,value in usermaterialdict.items():
        if not str(key) in getNameFromHashInventoryItem:
            print(key)
            continue
        materialname = getNameFromHashInventoryItem[str(key)]
        usermaterialreadabledict[materialname] = value
    #print(usermaterialreadabledict)

    for sale in sales.values():
        soldhash = sale["itemHash"]
        pricehash = sale["costs"][0]["itemHash"]
        ownedamount = 0

        #requests to identify the items TODO save manuscript locally and look them up there?
        soldurl = itemhashurl.format(hashIdentifier=soldhash)
        priceurl = itemhashurl.format(hashIdentifier=pricehash)

        #get the name of the sold material
        r = getJSONfromURL(soldurl)
        soldname = r['Response']['displayProperties']['name'][9:]
        if 'traitIds' in r['Response'] and 'item_type.bounty' in r['Response']['traitIds']:
            continue

        #print(r['Response'])
        
        #get the name of the asked material
        pricename = getNameFromHashInventoryItem[str(pricehash)]

        if soldname in usermaterialreadabledict.keys():
            ownedamount = usermaterialreadabledict[soldname]
        else:
            soldnamecut = soldname[:-1]
            if soldnamecut in usermaterialreadabledict.keys():
                ownedamount = usermaterialreadabledict[soldnamecut]
            else:
                print(soldname)
                print(usermaterialreadabledict.keys())
            
            

        #returntext += f'selling {sale["quantity"]} {soldname} for {sale["costs"][0]["quantity"]} {pricename}\n'
        returntext += f'selling {ownedamount} {soldname} for {pricename}\n'

    returntext = returntext.replace('Dusklight Shard', '<:DusklightShards:620647201940570133>')
    returntext = returntext.replace('Phaseglass Needle', '<:Phaseglass:620647202418851895>')
    returntext = returntext.replace('Seraphite', '<:Seraphite:620647202297085992>')
    returntext = returntext.replace('Legendary Shards', '<:LegendaryShards:620647202003484672>')
    returntext = returntext.replace('Alkane Dust', '<:AlkaneDust:620647201827454990>')
    returntext = returntext.replace('Data Lattice', '<:Datalattice:620647202015936536>')
    returntext = returntext.replace('Simulation Seeds', '<:SimulationSeeds:620647203635200070>')
    returntext = returntext.replace('Glimmer', '<:Glimmer:620647202007810098>')
    returntext = returntext.replace('Enhancement Cores', '<:EnhancementCores:620647201596637185>')
    returntext = returntext.replace('Helium Filaments', '<:HeliumFilaments:707244746493657160>')
    return returntext