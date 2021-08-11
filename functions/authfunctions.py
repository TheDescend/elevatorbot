from database.database import lookupDiscordID, getDestinyDefinition, lookupSystem
from networking.models import WebResponse
from networking.network import get_json_from_bungie_with_token
from inspect                import currentframe, getframeinfo
from functions.formating    import embed_message

async def getUserMaterials(destinyID):
    system = 3
    url = f'https://stats.bungie.net/Platform/Destiny2/{system}/Profile/{destinyID}/?components=600'
    res = await get_json_from_bungie_with_token(url, await lookupDiscordID(destinyID))
    if not res.success:
        return res.error
    materialdict = list(res.content['Response']['characterCurrencyLookups']['data'].values())[0]['itemQuantities']
    return materialdict

async def getRasputinQuestProgress():
    haliUrl = 'https://stats.bungie.net/Platform/Destiny2/3/Profile/4611686018468695677/?components=301'
    res = await get_json_from_bungie_with_token(haliUrl, 171650677607497730)
    rasputinobjectives = res.content['Response']["characterUninstancedItemComponents"]["2305843009410156755"]["objectives"]["data"]["1797229574"]['objectives']
    obHashes = {
        1851115127 : 'EDZ',
        1851115126 : 'Moon',
        1851115125 : 'Io'
    }
    return [(obHashes[objective["objectiveHash"]],objective["progress"], objective["completionValue"]) for objective in rasputinobjectives]


async def getVendorData(discordID, destinyID, characterID, vendorID) -> WebResponse:
    system = await lookupSystem(destinyID)
    url = f'https://www.bungie.net/Platform/Destiny2/{system}/Profile/{destinyID}/Character/{characterID}/Vendors/{vendorID}/?components=400,401,402,304'
    return await get_json_from_bungie_with_token(url, discordID)


async def getSpiderMaterials(discordID, destinyID, characterID):
    """ Gets spiders current selling inventory, requires OAuth"""
    # 863940356 is spiders vendorID
    res = await getVendorData(discordID, destinyID, characterID, 863940356)
    if not res['result']:
        return {'result': None, 'error':res['error']}
    #gets the dictionary of sold items
    sales = res['result']['Response']['sales']['data']
    returntext = ''
    usermaterialdict = await getUserMaterials(destinyID)
    usermaterialreadabledict = {}
    
    for key,value in usermaterialdict.items():
        if keylookup := await getDestinyDefinition('DestinyInventoryItemDefinition', key):
            (_, _, materialname, *_) = keylookup
        else:
            materialname = 'Unknown'
        usermaterialreadabledict[materialname] = value
    #print(usermaterialreadabledict)

    embed = embed_message("Spider's Stock", description="Unlike his Fallen brethren, the stupid Spider ~~kidnapped our bird.~~ Update: He's free now")
    for sale in sales.values():
        if 'apiPurchasable' in sale.keys():
            #We don't care about bounties
            continue
        soldhash = sale["itemHash"]
        #only ever costs one material, so we just get the first one
        if not sale['costs']:
            #probably some quest item
            continue
        pricehash = sale["costs"][0]["itemHash"]
        pricequantity = sale["costs"][0]["quantity"]
        ownedamount = 0

        #requests to identify the items TODO save manuscript locally and look them up there?
        (_, _, soldname, *_) = await getDestinyDefinition("DestinyInventoryItemDefinition", soldhash)
        (_, _, pricename, *_) = await getDestinyDefinition("DestinyInventoryItemDefinition", int(pricehash))
        if soldname not in usermaterialreadabledict.keys():
            if 'Purchase ' in soldname:
                isPlural = (soldname[-1] == "s") and (not soldname == "Purchase Helium Filaments") and (not soldname == "Purchase Spinmetal Leaves")
                soldname = soldname[len('Purchase '):len(soldname)-isPlural]
                #e.g. Purchase Enhancement Prisms
            else:
                print(f'getSpiderMaterials:{getframeinfo(currentframe()).lineno} Could not find {soldname}')
                continue
        if soldname == 'Datalattice':
            soldname = 'Microphasic Datalattice'
        ownedamount = usermaterialreadabledict.get(soldname, -1) #find value, otherwise use name

        def replaceWithEmote(name):
            replacedict = {
                "Dusklight Shard": '<:DusklightShards:620647201940570133>',
                'Phaseglass Needle':'<:Phaseglass:620647202418851895>',
                'Seraphite':'<:Seraphite:620647202297085992>',
                'Legendary Shards':'<:LegendaryShards:620647202003484672>',
                'Alkane Dust':'<:AlkaneDust:620647201827454990>',
                'Microphasic Datalattice':'<:Datalattice:620647202015936536>',
                'Simulation Seed':'<:SimulationSeeds:620647203635200070>',
                'Glimmer':'<:Glimmer:620647202007810098>',
                'Enhancement Core':'<:EnhancementCores:620647201596637185>',
                'Helium Filament':'<:HeliumFilaments:707244746493657160>',
                'Etheric Spiral':'<:EthericSpiral:620647202267594792>',
                'Baryon Bough':'<:BaryonBough:755678814427807756>',
                'Enhancement Prism':'<:enhancementprism:801461164781469717>',
                'Spinmetal Leaves': '<:SpinmetalLeaves:810098590843535401>',
                'Glacial Starwort': '<:GlacialStarwort:810110131076726805>'
            }
            return replacedict.get(name, name)
        embed.add_field(name=soldname, value=f"**Owned**: {ownedamount:,} {replaceWithEmote(soldname)}\n**Cost**: {pricequantity:,} {replaceWithEmote(pricename)}", inline=True)
        returntext += f'selling  {replaceWithEmote(soldname)} for {replaceWithEmote(pricename)}, you already own {ownedamount:>12,d} {replaceWithEmote(soldname)}\n'
    return {'result': returntext, 'embed': embed, 'error': None}