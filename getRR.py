import requests, config

bungieID = input('giff bungieNet-ID\n')

PARAMS = {'X-API-Key':config.key}
url = 'https://www.bungie.net/platform/User/GetMembershipsById/{}/{}/'.format(bungieID,3)
r=requests.get(url=url, headers=PARAMS)
memberships = r.json()['Response']['destinyMemberships']
for membership in memberships:
    if membership['membershipType'] == 3:
        print('https://raid.report/pc/' + membership['membershipId'])
