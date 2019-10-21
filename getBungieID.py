
import requests, config

clanid = '2784110'
displayName = 'Hali'

baseURL = "https://www.bungie.net/Platform"
PARAMS = {'X-API-Key':config.BUNGIE_TOKEN}

def getJSONfromURL(requestURL):
    r=requests.get(url=baseURL + requestURL, headers=PARAMS)
    return r.json()

requestURL = "/GroupV2/" + clanid + "/members/"
memberJSON = getJSONfromURL(requestURL)
memberlist = memberJSON['Response']['results']
memberids = dict()
for member in memberlist:
    memberids[member['destinyUserInfo']['LastSeenDisplayName']] = member['destinyUserInfo']['membershipId']

# memberids['Hali'] is my destinyMembershipID
# uses lastSeenDisplayName

bungieID = memberids[displayName]
print(bungieID)
