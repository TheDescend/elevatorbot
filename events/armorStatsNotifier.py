from events.base_event import BaseEvent
from functions.authfunctions import getVendorData
from functions.dataLoading import getCharacterList
from functions.database import lookupDestinyID, getDestinyDefinition
from functions.formating import embed_message


class ArmorStatsNotifier(BaseEvent):
    """ Every week, this checks the vendor rolls and dms people if they signed up for that """

    def __init__(self):
        # bot is running on est, that should give it enough time (reset is at 12pm there)
        dow_day_of_week = "tue"
        dow_hour = 14
        dow_minute = 0
        super().__init__(scheduler_type="cron", dow_day_of_week=dow_day_of_week, dow_hour=dow_hour, dow_minute=dow_minute)

    async def run(self, client):
        # send msg to user
        async def message_user(client, discordID, vendor_name, item_definition, stats, total_stats):
            embed = embed_message(
                f"{vendor_name} is selling {item_definition[2]}",
                f"**Class:** {class_types[item_definition[3]]}\n**Slot:** {getDestinyDefinition('DestinyInventoryBucketDefinition', item_definition[4])[2]}\n**Total Stats:** {total_stats}"
            )
            for stat_name, statID in stat_names.items():
                embed.add_field(name=stat_name, value=f"Total: {stats[statID]['value']}", inline=True)

            # send that to user
            user = client.get_user(discordID)
            if user:
                await user.send(embed=embed)

        # vendors that sell armor
        armor_selling_vendors = {
            "Zavala": 69482069,
            "Drifter": 248695599,
            "Shaxx": 3603221665,
            "Devrim Kay": 396892126,
            "Failsafe": 1576276905
        }

        # armor stats
        stat_names = {
            "Mobility": "2996146975",
            "Resilience": "392767087",
            "Recovery": "1943323491",
            "Discipline": "1735777505",
            "Intellect": "144602215",
            "Strength": "4244567218"
        }

        # class types
        class_types = {
            0: "Titan",
            1: "Hunter",
            2: "Warlock",
        }

        # get ids for lookups, using kigstn's data for this one
        discordID = 238388130581839872
        destinyID = lookupDestinyID(discordID)
        characterIDs = (await getCharacterList(destinyID))[1]

        # loop through charIDs
        for characterID in characterIDs:
            # loop through vendors
            for vendor_name, vendorID in armor_selling_vendors.items():
                res = await getVendorData(discordID, destinyID, characterID, vendorID)

                try:
                    sales = res['result']['Response']['itemComponents']['stats']['data']
                    definitions = res['result']['Response']['sales']['data']
                except KeyError:
                    print(f"Vendor {vendor_name} has no sold items")
                    continue

                # loop through items sold
                for saleID, sale in sales.items():
                    # check if item is armor
                    if not stat_names["Mobility"] in sale["stats"]:
                        continue
                    item_stats = sale["stats"]
                    total_stats = sum([x["value"] for x in item_stats.values()])

                    # catch dummy armors that are not sold but show up for some reason. Also class items are meh
                    try:
                        item_definition = getDestinyDefinition("DestinyInventoryItemDefinition", definitions[saleID]['itemHash'])
                    except KeyError:
                        continue

                    """ text users that we found sth if that applies """
                    # kigstn
                    if (class_types[item_definition[3]] == "Warlock") and (item_stats[stat_names["Recovery"]]["value"] > 20) and (item_stats[stat_names["Discipline"]]["value"] > 20):
                        await message_user(client, 238388130581839872, vendor_name, item_definition, item_stats, total_stats)

                    # neria
                    if (class_types[item_definition[3]] == "Hunter") and (item_stats[stat_names["Mobility"]]["value"] > 23) and (total_stats > 63):
                        await message_user(client, 109022023979667456, vendor_name, item_definition, item_stats, total_stats)

                    # ini
                    if (item_stats[stat_names["Mobility"]]["value"] > 20) or (item_stats[stat_names["Recovery"]]["value"] > 20) or (item_stats[stat_names["Intellect"]]["value"] > 20):
                        await message_user(client, 171371726444167168, vendor_name, item_definition, item_stats, total_stats)
