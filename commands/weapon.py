from commands.base_command import BaseCommand

import datetime
import discord
import os
import pandas as pd
import matplotlib.pyplot as plt

from commands.rank import write_line
from functions.dataLoading import searchForItem, getCharacterID
from database.database import lookupDestinyID, getTopWeapons, getDestinyDefinition, getWeaponInfo, getPgcrActivity
from functions.formating import embed_message


# gets detailed info about a weapon
class weapon(BaseCommand):
    # these hashes are supported, or use the numeric mode. Default is 0
    activities = {
        "everything": 0,
        "patrol": 6,
        "pve": 7,
        "pvp": 5,
        "raids": 4,
        "story": 2,
        "strikes": 3
    }
    classes = {
        "warlock": 2271682572,
        "hunter": 671679327,
        "titan": 3655393761
    }
    stats = [
        "kills",
        "precisionkills",
        "precisionkillspercent"
    ]

    def __init__(self):
        # A quick description for the help message
        description = "Shows in-depth weapon stats with lots of room for customization"
        params = [f"*mode {'|'.join(list(self.activities.keys()))}", f"*activityhash hash", "*time dd/mm/yy dd/mm/yy", f"*class {'|'.join(list(self.classes.keys()))}", f"*stat {'|'.join(list(self.stats))}", "*graph", "weaponName"]
        topic = "Destiny"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        async with message.channel.typing():
            # get params
            weapon_name, showcase, mode, activity_hash, start, end, char_class, stat = await compute_parameters(message, params, self.activities, self.classes, self.stats)
            destinyID = lookupDestinyID(mentioned_user.id)
            charID = await getCharacterID(destinyID, self.classes[char_class]) if char_class else None

            # get weapon info
            weapon_name, weapon_hashes = await searchForItem(client, message, weapon_name)
            if not weapon_name:
                return

            # get all weapon infos
            kwargs = {
                "characterID": charID,
                "mode": mode,
                "activityID": activity_hash,
                "start": start,
                "end": end
            }

            # loop through every variant of the weapon and add that together
            result = []
            for entry in weapon_hashes:
                result.extend(getWeaponInfo(destinyID, entry, **{k: v for k, v in kwargs.items() if v is not None}))

            # throw error if no weapon
            if not result:
                await message.reply(embed=embed_message(
                    "Error",
                    f'No weapon stats found for {weapon_name}'
                ))
                return

            if showcase == "number":
                # get data
                kills = 0
                precision_kills = 0
                max_kills = 0
                max_kills_id = None
                for instanceID, uniqueweaponkills, uniqueweaponprecisionkills in result:
                    kills += uniqueweaponkills
                    precision_kills += uniqueweaponprecisionkills
                    if uniqueweaponkills > max_kills:
                        max_kills = uniqueweaponkills
                        max_kills_id = instanceID
                percent_precision_kills = precision_kills / kills if kills else 0
                avg_kills = kills / len(result)
                res = await getPgcrActivity(max_kills_id)
                max_kills_date = res[3]
                max_kills_mode = getDestinyDefinition("DestinyActivityModeDefinition", res[5])[2]
                max_kills_name = getDestinyDefinition("DestinyActivityDefinition", res[2])[2]

                # make and post embed
                embed = embed_message(
                    f"{weapon_name} stats for {mentioned_user.display_name}",
                    f"",
                    f"""mode={mode}, start={start.strftime('%d/%m/%Y')}, end={end.strftime('%d/%m/%Y')}{", activityHash=" + str(activity_hash) if activity_hash else ""}{", class=" + str(char_class) if char_class else ""}"""
                )
                embed.add_field(name="Total Kills", value=f"**{kills:,}**", inline=True)
                embed.add_field(name="Total Precision Kills", value=f"**{precision_kills:,}**", inline=True)
                embed.add_field(name="% Precision Kills", value=f"**{round(percent_precision_kills*100, 2)}%**", inline=True)
                embed.add_field(name="Average Kills", value=f"**{round(avg_kills, 2)}**\nIn {len(result)} Activities", inline=True)
                embed.add_field(name="Maximum Kills", value=f"**{max_kills:,}**\nIn Activity ID: {max_kills_id}\n{max_kills_mode} - {max_kills_name}\nOn: {max_kills_date.strftime('%d/%m/%y')}", inline=True)
                await message.reply(embed=embed)

            elif showcase == "graph":
                # get the time instead of the instance id and sort it so the earliest date is first
                weapon_hashes = []
                for instanceID, uniqueweaponkills, uniqueweaponprecisionkills in result:
                    instance_time = await getPgcrActivity(instanceID)[3]
                    weapon_hashes.append((instance_time, uniqueweaponkills, uniqueweaponprecisionkills))
                weapon_hashes = sorted(weapon_hashes, key=lambda x: x[0])

                # get clean, relevant data in a DF. easier for the graph later
                df = pd.DataFrame(columns=["datetime", "statistic"])
                name = ""
                statistic1 = 0
                statistic2 = 0
                time = weapon_hashes[0][0]
                for instance_time, uniqueweaponkills, uniqueweaponprecisionkills in weapon_hashes:
                    if instance_time.date() == time.date():
                        if stat == "kills":
                            statistic1 += uniqueweaponkills
                            name = "Kills"
                        elif stat == "precisionkills":
                            statistic1 += uniqueweaponprecisionkills
                            name = "Precision Kills"
                        elif stat == "precisionkillspercent":
                            statistic1 += uniqueweaponkills
                            statistic2 += uniqueweaponprecisionkills
                            name = "% Precision Kills"
                        time = instance_time
                    else:
                        # append to DF
                        entry = {
                            'datetime': time.date(),
                            'statistic': statistic2 / statistic1 if stat == "precisionkillspercent" else statistic1
                        }
                        df = df.append(entry, ignore_index=True)

                        # save new data
                        if stat == "kills":
                            statistic1 = uniqueweaponkills
                            name = "Kills"
                        elif stat == "precisionkills":
                            statistic1 = uniqueweaponprecisionkills
                            name = "Precision Kills"
                        elif stat == "precisionkillspercent":
                            statistic1 = uniqueweaponkills
                            statistic2 = uniqueweaponprecisionkills
                            name = "% Precision Kills"
                        time = instance_time

                # append to DF
                entry = {
                    'datetime': time,
                    'statistic': statistic2 / statistic1 if stat == "precisionkillspercent" else statistic1
                }
                df = df.append(entry, ignore_index=True)

                # convert to correct file types
                df['datetime'] = pd.to_datetime(df['datetime'])
                df['statistic'] = pd.to_numeric(df['statistic'])

                # building the graph
                # Create figure and plot space
                fig, ax = plt.subplots(figsize=(20, 10))
                ax.yaxis.grid(True)

                # filling bar chart
                ax.bar(
                    df['datetime'],
                    df['statistic'],
                    color="#45b6fe"
                )

                # Set title and labels for axes
                ax.set_title(f"{weapon_name} stats for {mentioned_user.display_name}", fontweight="bold", size=30, pad=20)
                ax.set_xlabel("Date", fontsize=20)
                ax.set_ylabel(name, fontsize=20)

                # saving file
                title = "weapon.png"
                plt.savefig(title)

                # sending them the file
                await message.reply(f"""*mode={mode}, start={start.strftime('%d/%m/%Y')}, end={end.strftime('%d/%m/%Y')}{", activityHash=" + str(activity_hash) if activity_hash else ""}{", class=" + str(char_class) if char_class else ""}*""", file=discord.File(title))

                # delete file
                os.remove(title)


# shows you your top 10 weapons or top 10 weapons and the one you specified
class topWeapons(BaseCommand):
    # these hashes are supported, or use the numeric mode. Default is 0
    activities = {
        "everything": 0,
        "patrol": 6,
        "pve": 7,
        "pvp": 5,
        "raids": 4,
        "story": 2,
        "strikes": 3
    }
    classes = {
        "warlock": 2271682572,
        "hunter": 671679327,
        "titan": 3655393761
    }
    stats = [
        "kills",
        "precisionkills",
        "precisionkillspercent"
    ]

    def __init__(self):
        # A quick description for the help message
        description = "Shows your top10 weapons with with lots of room for customization"
        params = [f"*mode {'|'.join(list(self.activities.keys()))}", f"*activityhash hash", "*time dd/mm/yy dd/mm/yy", f"*class {'|'.join(list(self.classes.keys()))}", f"*stat {'|'.join(list(self.stats))}", "*weaponName"]
        topic = "Destiny"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        async with message.channel.typing():
            # get params
            weapon_name, _, mode, activity_hash, start, end, char_class, stat = await compute_parameters(message, params, self.activities, self.classes, self.stats)
            destinyID = lookupDestinyID(mentioned_user.id)
            charID = await getCharacterID(destinyID, self.classes[char_class]) if char_class else None

            # get the real weapon name
            if weapon_name:
                weapon_name, _ = await searchForItem(client, message, weapon_name)
                if not weapon_name:
                    return

            # get all weaponID infos
            kwargs = {
                "characterID": charID,
                "mode": mode,
                "activityID": activity_hash,
                "start": start,
                "end": end
            }
            result = getTopWeapons(destinyID, **{k: v for k, v in kwargs.items() if v is not None})

            # loop through that and get data
            data = []
            for weaponID, uniqueweaponkills, uniqueweaponprecisionkills in result:
                # get the name
                weapon_data = [(await getDestinyDefinition("DestinyInventoryItemDefinition", weaponID))[2]]

                if stat == "kills":
                    statistic = uniqueweaponkills
                    weapon_data.append(statistic)
                    weapon_data.append(f"{statistic:,}")
                elif stat == "precisionkills":
                    statistic = uniqueweaponprecisionkills
                    weapon_data.append(statistic)
                    weapon_data.append(f"{statistic:,}")
                elif stat == "precisionkillspercent":
                    statistic = uniqueweaponkills / uniqueweaponprecisionkills if uniqueweaponprecisionkills != 0 else 0
                    weapon_data.append(statistic)
                    weapon_data.append(f"{round(statistic*100, 2)}%")

                data.append(tuple(weapon_data))

            # sort by index specified
            sorted_data = sorted(data, key=lambda x: x[1], reverse=True)

            # get the data for the embed
            i = 0
            ranking = []
            found = False if weapon_name else True
            for name, _, statistic in sorted_data:
                i += 1
                if len(ranking) < 12:
                    # setting a flag if name is in list
                    if weapon_name == name:
                        found = True
                        ranking.append(write_line(i, f"""[{name}]""", stat.capitalize(), statistic))
                    else:
                        ranking.append(write_line(i, name, stat.capitalize(), statistic))

                # looping through rest until original user is found
                elif (len(ranking) >= 12) and (not found):
                    # adding only this name
                    if weapon_name == name:
                        ranking.append("...")
                        ranking.append(write_line(i, name, stat.capitalize(), statistic))
                        found = True
                        break

                else:
                    break

            # write "0" as data, since it is not in there
            if not found:
                ranking.append("...")
                ranking.append(write_line(i, weapon_name, stat.capitalize(), 0))

            # make and post embed
            embed = embed_message(
                f"Top Weapons for {mentioned_user.display_name}",
                "\n".join(ranking),
                f"""mode={mode}, start={start.strftime('%d/%m/%Y')}, end={end.strftime('%d/%m/%Y')}{", activityHash=" + str(activity_hash) if activity_hash else ""}{", class=" + str(char_class) if char_class else ""}"""
            )
            await message.reply(embed=embed)


async def compute_parameters(message, params, activities, classes, stats):
    weapon_name = ""
    showcase = "number"
    mode = 0
    activity_hash = None
    start = datetime.datetime.min
    end = datetime.datetime.now()
    char_class = None
    stat = "kills"
    look_for = ""
    for param in params:
        param = param.lower()

        # get mode
        if look_for == "mode":
            try:
                if param in activities:
                    mode = activities[param]
                    look_for = ""
                    continue
                else:
                    mode = int(param)
                    look_for = ""
                    continue
            except ValueError:
                await error_message(message, f"The mode parameter must be in \n`{'|'.join(list(activities.keys()))}`")
                return

        # convert dates
        elif look_for == "time":
            try:
                if start == datetime.datetime.min:
                    start = datetime.datetime.strptime(param, "%d/%m/%y")
                else:
                    end = datetime.datetime.strptime(param, "%d/%m/%y")
                    if end < start:
                        raise ValueError
                    look_for = ""
                    continue
            except ValueError:
                await error_message(message, f"The time parameter must be like \n**Start->**`dd/mm/yy dd/mm/yy`**<-End**")
                return

        # get class
        elif look_for == "class":
            if param in classes:
                char_class = param
                look_for = ""
                continue
            else:
                await error_message(message, f"The class parameter must be in \n`{'|'.join(list(classes.keys()))}`")
                return

        # get type of statistic
        elif look_for == "stat":
            if param in stats:
                stat = param
                look_for = ""
                continue
            else:
                await error_message(message, f"The stat parameter must be in \n`{'|'.join(list(stats))}`")
                return

        # get activity hash
        elif look_for == "activityhash":
            try:
                activity_hash = int(param)
                look_for = ""
                continue
            except ValueError:
                await error_message(message, f"The activityHash parameter must be in an integer.`")
                return

        if param == "graph":
            showcase = "graph"
            continue
        elif param == "mode":
            look_for = param
        elif param == "time":
            look_for = param
        elif param == "class":
            look_for = param
        elif param == "stat":
            look_for = param
        elif param == "activityhash":
            look_for = param

        if not look_for:
            # set weapon name
            weapon_name += param + " "

    return weapon_name, showcase, mode, activity_hash, start, end, char_class, stat


async def error_message(message, text):
    await message.reply(embed=embed_message(
        'Error',
        text
    ))
