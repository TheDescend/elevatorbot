import datetime
import os

import discord

from commands.base_command import BaseCommand
from functions.dataLoading import getCharacterInfoList, getProfile, getCharactertypeList
from functions.dataTransformation import getCharStats, getPlayerSeals, getIntStat, getTop10PveGuns, getGunsForPeriod, \
    getPossibleStats
from functions.database import lookupDestinyID, lookupSystem
from functions.formating import embed_message
from static.globals import dev_role_id


class stat(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Gives you stats for your account. Use !stat help for a list of possible values"
        params = ['statName']
        topic = "Destiny"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        name = params[0]

        destinyID = lookupDestinyID(mentioned_user.id)
        if not destinyID:
            await message.channel.send(f'Unable to get your destiny-stats. Please contact a {message.guild.get_role(dev_role_id)}')
            return
        if name == 'resurrections':
            given = await getIntStat(destinyID, 'resurrectionsPerformed')
            received = await getIntStat(destinyID, 'resurrectionsReceived')
            await message.channel.send(f'{mentioned_user.mention}, you have revived **{given}** people and got revived **{received}** times! 🚑')
        elif name == 'meleekills':
            melees = await getIntStat(destinyID, 'weaponKillsMelee')
            await message.channel.send(f'{mentioned_user.mention}, you have punched **{melees}** enemies to death! 🖍️')

        elif name == 'superkills':
            melees = await getIntStat(destinyID, 'weaponKillsSuper')
            await message.channel.send(f'{mentioned_user.mention}, you have used your supers to extinguish **{melees}** enemies! <a:PepoCheer:670678495923273748>')

        elif name == 'longrangekill':
            snips = await getIntStat(destinyID, 'longestKillDistance')
            await message.channel.send(f'{mentioned_user.mention}, you sniped an enemy as far as **{snips}** meters away <:Kapp:670369121808154645>')
        elif name == 'top10pveguns':
            async with message.channel.typing():
                imgpath = await getTop10PveGuns(destinyID)
                with open(imgpath, 'rb') as f:
                    await message.channel.send(f'{mentioned_user.mention}, here are your top10 guns used in raids', file=discord.File(f))
                os.remove(imgpath)
        elif name == 'pve': #starttime endtime
            start = params[1]
            end = params[2]
            await message.channel.send(await getGunsForPeriod(destinyID, start, end))
            #"2020-03-31"
        elif name == 'deaths':
            stats = []
            for charid, chardesc in await getCharactertypeList(destinyID):
                stats.append((chardesc, await getCharStats(destinyID, charid, 'deaths')))
            printout = "\n".join([f'Your {chardesc} has {"{:,}".format(count)} deaths' for chardesc,count in stats])
            await message.channel.send(printout)
        elif name == 'help':
            await message.channel.send(f'''
            {message.author.mention}, use those arguments for !stat *<argument>*:
            > **resurrections**: *Shows how many players you revived and how many times you got revived*
            > **meleekills**: *Shows how many enemies you've punched to death*
            > **superkills**: *Shows how many enemies you've killed with your super*
            > **longrangekill**: *Shows how far you've sniped*
            > **top10raidguns**: *Shows a piechart of your favourite guns* 
             other possible stats include {", ".join(await getPossibleStats())}
             ''')
        elif name in await getPossibleStats():
            stats = []
            for charid, chardesc in await getCharactertypeList(destinyID):
                stats.append((chardesc, await getCharStats(destinyID, charid, name)))
            printout = "\n".join([f'Your {chardesc} has {"{:,}".format(int(count))} {name}' for chardesc,count in stats])
            await message.channel.send(printout)
        else:
            await message.channel.send('Use !stat help for a list of commands :)')


class stats(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Gives you various destiny stats"
        topic = "Destiny"
        params = []
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        async with message.channel.typing():
            # get basic user data
            destinyID = lookupDestinyID(mentioned_user.id)
            system = lookupSystem(destinyID)
            heatmap_url = f"https://chrisfried.github.io/secret-scrublandeux/guardian/{system}/{destinyID}"
            characterIDs, character_data = await getCharacterInfoList(destinyID)
            character_playtime = {}     # in seconds
            for characterID in characterIDs:
                character_playtime[characterID] = await getCharStats(destinyID, characterID, "secondsPlayed")

            embed = embed_message(
                f"{mentioned_user.display_name}'s Destiny Stats",
                f"**Total Playtime:** {str(datetime.timedelta(seconds=sum(character_playtime.values())))} \n[Click to see your heatmap]({heatmap_url})",
                "For info on achievable discord roles, type !roles"
            )

            """ char info field """
            embed.add_field(name="⁣", value=f"__**Characters:**__", inline=False)
            for characterID in characterIDs:
                text = f"""Playtime: {str(datetime.timedelta(seconds=character_playtime[characterID]))} \n⁣\nPower: {int(await getCharStats(destinyID, characterID, "highestLightLevel")):,} \nActivities: {int(await getCharStats(destinyID, characterID, "activitiesCleared")):,} \nKills: {int(await getCharStats(destinyID, characterID, "kills")):,} \nDeaths: {int(await getCharStats(destinyID, characterID, "deaths")):,} \nEfficiency: {round(await getCharStats(destinyID, characterID, "efficiency"), 2)}"""
                embed.add_field(name=f"""{character_data[characterID]["class"]} ({character_data[characterID]["race"]} / {character_data[characterID]["gender"]})""", value=text, inline=True)

            """ triumph info field """
            embed.add_field(name="⁣", value=f"__**Triumphs:**__", inline=False)

            # get triumph data
            triumphs = await getProfile(destinyID, 900)
            embed.add_field(name="Lifetime Triumph Score", value=f"""{triumphs["profileRecords"]["data"]["lifetimeScore"]:,}""", inline=True)
            embed.add_field(name="Active Triumph Score", value=f"""{triumphs["profileRecords"]["data"]["activeScore"]:,}""", inline=True)
            embed.add_field(name="Legacy Triumph Score", value=f"""{triumphs["profileRecords"]["data"]["legacyScore"]:,}""", inline=True)

            # get triumph completion rate
            triumphs_data = triumphs["profileRecords"]["data"]["records"]
            triumphs_completed = 0
            triumphs_no_data = 0
            for triumph in triumphs_data.values():
                status = True
                if "objectives" in triumph:
                    for part in triumph['objectives']:
                        status &= part['complete']
                elif "intervalObjectives" in triumph:
                    for part in triumph['intervalObjectives']:
                        status &= part['complete']
                else:
                    triumphs_no_data += 1
                    continue
                if status:
                    triumphs_completed += 1
            embed.add_field(name="Triumphs", value=f"{triumphs_completed} / {len(triumphs_data) - triumphs_no_data}", inline=True)

            # get seal completion rate
            seals, completed_seals = await getPlayerSeals(destinyID)
            embed.add_field(name="Seals", value=f"{len(completed_seals)} / {len(seals)}", inline=True)

            # collection completion data
            collections_data = (await getProfile(destinyID, 800))["profileCollectibles"]["data"]["collectibles"]
            collectibles_completed = 0
            for collectible in collections_data.values():
                if collectible['state'] & 1 == 0:
                    collectibles_completed += 1
            embed.add_field(name="Collections", value=f"{collectibles_completed} / {len(collections_data)}", inline=True)

        await message.reply(embed=embed)
