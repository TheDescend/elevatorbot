
import requests

baseURL = "https://www.bungie.net/Platform"
PARAMS = {'X-API-Key':'3743ea53f4014677a36be515239869b3'}

def getJSONfromURL(requestURL):
    r=requests.get(url=baseURL + requestURL, headers=PARAMS)
    return r.json()

requestURL = "/GroupV2/2784110/members/" #bloodoak memberlist
memberJSON = getJSONfromURL(requestURL)
memberlist = memberJSON['Response']['results']
memberids = dict()
for member in memberlist:
    memberids[member['destinyUserInfo']['LastSeenDisplayName']] = member['destinyUserInfo']['membershipId']

# memberids['Hali'] is my destinyMembershipID
# uses lastSeenDisplayName

bungieID = memberids['Hali']
print(bungieID)