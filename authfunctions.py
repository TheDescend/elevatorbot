from database   import getToken
from oauth      import refresh_token
from config     import BUNGIE_TOKEN

import requests


def getJSONwithToken(url, discordID):
    """ Takes url and discordID, returns JSON """

    token = getToken(discordID)
    if not token:
        return None

    headers = {'Authorization': f'Bearer {token}', 'x-api-key': BUNGIE_TOKEN}
    r = requests.get(url, headers = headers)
    res = r.json()

    if int(res['ErrorCode']) == 401:
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
        r = getJSONwithToken(soldurl, discordID)
        soldname = r['Response']['displayProperties']['name'][9:]
        if 'traitIds' in r['Response'] and 'item_type.bounty' in r.json()['Response']['traitIds']:
            continue
        
        #get the name of the asked material
        r = getJSONwithToken(priceurl, discordID)
        pricename = r['Response']['displayProperties']['name']

        returntext += f'selling {sale["quantity"]} {soldname} for {sale["costs"][0]["quantity"]} {pricename}\n'
    return returntext