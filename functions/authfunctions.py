from functions.database     import getToken
from oauth                  import refresh_token
from static.config          import BUNGIE_TOKEN
from functions.network      import getJSONfromURL

import requests
session = requests.Session()

def getJSONwithToken(url, discordID):
    """ Takes url and discordID, returns JSON """

    token = getToken(discordID)
    if not token:
        return None

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
        return None

    return res

def getSpiderMaterials(discordID, destinyID, characterID):
    """ Gets spiders current selling inventory, requires OAuth"""

    system = 3 #they're probably on PC
    #863940356 is spiders vendorID
    url = f'https://www.bungie.net/Platform/Destiny2/{system}/Profile/{destinyID}/Character/{characterID}/Vendors/863940356/?components=400,401,402'
    res = getJSONwithToken(url, discordID)
    if not res:
        return None
    #gets the dictionary of sold items
    sales = res['Response']['sales']['data']
    itemhashurl = 'https://bungie.net/platform/Destiny2/Manifest/DestinyInventoryItemDefinition/{hashIdentifier}/'
    returntext = ''
    for sale in sales.values():
        soldhash = sale["itemHash"]
        pricehash = sale["costs"][0]["itemHash"]

        #requests to identify the items TODO save manuscript locally and look them up there?
        soldurl = itemhashurl.format(hashIdentifier=soldhash)
        priceurl = itemhashurl.format(hashIdentifier=pricehash)

        #get the name of the sold material
        r = getJSONfromURL(soldurl)
        soldname = r['Response']['displayProperties']['name'][9:]
        if 'traitIds' in r['Response'] and 'item_type.bounty' in r['Response']['traitIds']:
            continue
        
        #get the name of the asked material
        r = getJSONfromURL(priceurl)
        pricename = r['Response']['displayProperties']['name']

        returntext += f'selling {sale["quantity"]} {soldname} for {sale["costs"][0]["quantity"]} {pricename}\n'
    return returntext