from commands.base_command import BaseCommand
from functions.dataLoading import getNameAndCrossaveNameToHashMapByClanid, getPGCR
from functions.database import lookupDiscordID, getSystemAndChars
from functions.network import getJSONfromURL
from static.dict import clanids


class maxPower(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Returns the players with the highest light level"
        params = []
        topic = "Destiny"
        super().__init__(description, params, topic)

    async def getLightLevel(self, client, destinyID):
        if not (discordID := lookupDiscordID(destinyID)) or not (user := client.get_user(discordID)):
            return ('None', 0)
        username = user.name
        localMax = 0
        sysCharList = getSystemAndChars(destinyID)
        for sys,charID in sysCharList:
            staturl = f"https://www.bungie.net/Platform/Destiny2/{sys}/Account/{destinyID}/Character/{charID}/Stats/Activities/?mode=7&count=3&page={0}" 
            rep = await getJSONfromURL(staturl)
            if not rep:
                continue
            for activity in rep['Response']['activities']:
                iid = activity['activityDetails']['instanceId']
                print(iid)
                if not (pgcrdata := await getPGCR(iid)):
                    print('getting pgcr data failed')
                    continue
                for player in pgcrdata['Response']['entries']:
                    playerID = player['player']['destinyUserInfo']['membershipId']
                    if playerID == destinyID:
                        ll = player['player']['lightLevel']
                        if ll > localMax:
                            localMax = ll
        return (username, localMax)


    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        with message.channel.typing():
            namePowerList = []
            for clanid,name in clanids.items():
                clanmap = await getNameAndCrossaveNameToHashMapByClanid(clanid)

                for destinyID in clanmap.keys():
                    namePowerList.append(await self.getLightLevel(client, destinyID))

        await message.channel.send("\n".join([f'{name}: {power}' for name, power in sorted(namePowerList, key=lambda ele:ele[1], reverse=True)][:20]))
