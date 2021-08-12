import datetime

from ElevatorBot.database.database import getDestinyDefinition
from ElevatorBot.events.base_event import BaseEvent
from ElevatorBot.functions.authfunctions import getVendorData
from ElevatorBot.functions.destinyPlayer import DestinyPlayer
from ElevatorBot.functions.formating import embed_message
from ElevatorBot.functions.persistentMessages import bot_status


class ArmorStatsNotifier(BaseEvent):
    """ Every week, this checks the vendor rolls and dms people if they signed up for that """


    def __init__(
        self
    ):
        dow_day_of_week = "tue"
        dow_hour = 20
        dow_minute = 0
        super().__init__(scheduler_type="cron", dow_day_of_week=dow_day_of_week, dow_hour=dow_hour, dow_minute=dow_minute)


    async def run(
        self,
        client
    ):
        # check for the rolls mystic likes since everyone seems to want that
        def these_are_the_rolls_mystic_likes(
            class_types,
            item_definition,
            item_stats,
            stat_names
        ):
            if (class_types[item_definition[3]] == "Hunter") and ((item_stats[stat_names["Mobility"]]["value"] + item_stats[stat_names["Recovery"]]["value"] +
                                                                   item_stats[stat_names["Intellect"]]["value"]) > 50):
                return True
            elif (class_types[item_definition[3]] == "Titan") and ((item_stats[stat_names["Resilience"]]["value"] + item_stats[stat_names["Recovery"]][
                "value"] + item_stats[stat_names["Intellect"]]["value"]) > 50):
                return True
            elif (class_types[item_definition[3]] == "Warlock") and ((item_stats[stat_names["Discipline"]]["value"] + item_stats[stat_names["Recovery"]][
                "value"] + item_stats[stat_names["Intellect"]]["value"]) > 50):
                return True
            return False


        # send msg to user
        async def message_user(
            client,
            discordID,
            vendor_name,
            item_definition,
            stats,
            total_stats
        ):
            embed = embed_message(
                f"{vendor_name} is selling {item_definition[2]}",
                f"**Class:** {class_types[item_definition[3]]}\n**Slot:** {(await getDestinyDefinition('DestinyInventoryBucketDefinition', item_definition[4]))[2]}\n**Total Stats:** {total_stats}"
            )
            for stat_name, statID in stat_names.items():
                embed.add_field(name=stat_name, value=f"Total: {stats[statID]['value']}", inline=True)

            # send that to user
            user = client.get_user(discordID)
            if user:
                await user.send(embed=embed)


        # vendors that sell armor
        armor_selling_vendors = {
            "Ada-1": 350061650,
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
        destiny_player = await DestinyPlayer.from_discord_id(238388130581839872)
        characters = await destiny_player.get_character_info()

        # loop through charIDs
        for character_id in characters:
            # loop through vendors
            for vendor_name, vendorID in armor_selling_vendors.items():
                res = await getVendorData(destiny_player.discord_id, destiny_player.destiny_id, character_id, vendorID)

                try:
                    sales = res.content['Response']['itemComponents']['stats']['data']
                    definitions = res.content['Response']['sales']['data']
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
                        item_definition = await getDestinyDefinition("DestinyInventoryItemDefinition", definitions[saleID]['itemHash'])
                    except KeyError:
                        continue

                    """ text users that we found sth if that applies """
                    # kigstn
                    if (class_types[item_definition[3]] == "Warlock") and (item_stats[stat_names["Recovery"]]["value"] > 20) and (
                        item_stats[stat_names["Discipline"]]["value"] > 20):
                        await message_user(client, 238388130581839872, vendor_name, item_definition, item_stats, total_stats)
                    elif (class_types[item_definition[3]] == "Warlock") and (item_stats[stat_names["Recovery"]]["value"] >= 28):
                        await message_user(client, 238388130581839872, vendor_name, item_definition, item_stats, total_stats)
                    elif (class_types[item_definition[3]] == "Hunter") and (item_stats[stat_names["Recovery"]]["value"] > 20) and (
                        item_stats[stat_names["Mobility"]]["value"] > 20):
                        await message_user(client, 238388130581839872, vendor_name, item_definition, item_stats, total_stats)

                    # neria
                    if (class_types[item_definition[3]] == "Hunter") and (item_stats[stat_names["Mobility"]]["value"] > 23) and (total_stats > 63):
                        await message_user(client, 109022023979667456, vendor_name, item_definition, item_stats, total_stats)

                    # ini
                    if (item_stats[stat_names["Mobility"]]["value"] > 20) or (item_stats[stat_names["Recovery"]]["value"] > 20) or (
                        item_stats[stat_names["Intellect"]]["value"] > 20):
                        await message_user(client, 171371726444167168, vendor_name, item_definition, item_stats, total_stats)
                    elif these_are_the_rolls_mystic_likes(class_types, item_definition, item_stats, stat_names):
                        await message_user(client, 171371726444167168, vendor_name, item_definition, item_stats, total_stats)

                    # red
                    if (class_types[item_definition[3]] == "Titan") and (
                        (item_stats[stat_names["Recovery"]]["value"] + item_stats[stat_names["Resilience"]]["value"]) > 29):
                        await message_user(client, 264456189905993728, vendor_name, item_definition, item_stats, total_stats)
                    elif (class_types[item_definition[3]] == "Titan") and ((item_stats[stat_names["Resilience"]]["value"] + item_stats[stat_names["Recovery"]][
                        "value"] + item_stats[stat_names["Intellect"]]["value"]) > 50):
                        await message_user(client, 264456189905993728, vendor_name, item_definition, item_stats, total_stats)

                    # mystic
                    if (class_types[item_definition[3]] == "Hunter") and ((item_stats[stat_names["Mobility"]]["value"] + item_stats[stat_names["Recovery"]][
                        "value"] + item_stats[stat_names["Intellect"]]["value"] + item_stats[stat_names["Resilience"]]["value"]) > 58):
                        await message_user(client, 211838266834550785, vendor_name, item_definition, item_stats, total_stats)
                    elif (class_types[item_definition[3]] == "Hunter") and ((item_stats[stat_names["Mobility"]]["value"] + item_stats[stat_names["Recovery"]][
                        "value"] + item_stats[stat_names["Discipline"]]["value"] + item_stats[stat_names["Resilience"]]["value"]) > 58):
                        await message_user(client, 211838266834550785, vendor_name, item_definition, item_stats, total_stats)
                    elif (class_types[item_definition[3]] == "Hunter") and ((item_stats[stat_names["Mobility"]]["value"] + item_stats[stat_names["Recovery"]][
                        "value"] + item_stats[stat_names["Strength"]]["value"] + item_stats[stat_names["Resilience"]]["value"]) > 58):
                        await message_user(client, 211838266834550785, vendor_name, item_definition, item_stats, total_stats)
                    elif (class_types[item_definition[3]] == "Titan") and ((item_stats[stat_names["Resilience"]]["value"] + item_stats[stat_names["Recovery"]][
                        "value"] + item_stats[stat_names["Intellect"]]["value"] + item_stats[stat_names["Discipline"]]["value"]) > 58):
                        await message_user(client, 211838266834550785, vendor_name, item_definition, item_stats, total_stats)
                    elif (class_types[item_definition[3]] == "Warlock") and ((item_stats[stat_names["Discipline"]]["value"] +
                                                                              item_stats[stat_names["Recovery"]]["value"] + item_stats[stat_names["Intellect"]][
                                                                                  "value"] + item_stats[stat_names["Resilience"]]["value"]) > 58):
                        await message_user(client, 211838266834550785, vendor_name, item_definition, item_stats, total_stats)

                    # tom
                    if total_stats > 60:
                        await message_user(client, 286616836844290049, vendor_name, item_definition, item_stats, total_stats)
                    elif these_are_the_rolls_mystic_likes(class_types, item_definition, item_stats, stat_names):
                        await message_user(client, 286616836844290049, vendor_name, item_definition, item_stats, total_stats)

                    # exiled
                    if these_are_the_rolls_mystic_likes(class_types, item_definition, item_stats, stat_names):
                        await message_user(client, 206878830017773568, vendor_name, item_definition, item_stats, total_stats)

        # update the status
        await bot_status(client, "Vendor Armor Roll Lookup", datetime.datetime.now(tz=datetime.timezone.utc))


class GunsmithBountiesNotifier(BaseEvent):
    """ Every day, this checks the gunsmith mods and dms people if they signed up for that """


    def __init__(
        self
    ):
        dow_day_of_week = "*"
        dow_hour = 19
        dow_minute = 30
        super().__init__(scheduler_type="cron", dow_day_of_week=dow_day_of_week, dow_hour=dow_hour, dow_minute=dow_minute)


    async def run(
        self,
        client
    ):
        # msg user
        async def gunsmith_msg(
            client,
            discordID,
            mod_name
        ):
            user = client.get_user(discordID)
            if user:
                await user.send(f"Gunsmith is selling {mod_name}!")


        # get ids for lookups, using kigstn's data for this one
        destiny_player = await DestinyPlayer.from_discord_id(238388130581839872)
        characters = await destiny_player.get_character_info()

        # check gunsmith mods
        res = await getVendorData(destiny_player.discord_id, destiny_player.destiny_id, list(characters)[0], 672118013)
        if res.success:
            for sales in res.content['Response']['sales']['data'].values():
                """ message users """

                # jayce
                if sales['itemHash'] == 179977568:
                    await gunsmith_msg(client, 672853590465052692, "Grasp of the Warmind")

                # ini
                if sales['itemHash'] == 2216063960:
                    await gunsmith_msg(client, 171371726444167168, "Rage of the Warmind")

        print("Done with gunsmith bounty checks")
