import requests,config

bungieID = input('giff bungieNet-ID\n')

PARAMS = {'X-API-Key':config.key}
url = 'https://www.bungie.net/platform/User/GetMembershipsById/{}/3/'.format(bungieID)
r=requests.get(url=url, headers=PARAMS)
print('https://raid.report/pc/' + r.json()['Response']['destinyMemberships'][0]['membershipId'])