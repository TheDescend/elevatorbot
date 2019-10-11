
import requests

bungieID = input('giff bungieNet-ID\n')

PARAMS = {'X-API-Key':'3743ea53f4014677a36be515239869b3'}
url = 'https://www.bungie.net/platform/User/GetMembershipsById/{}/3/'.format(bungieID)
r=requests.get(url=url, headers=PARAMS)
print('https://raid.report/pc/' + r.json()['Response']['destinyMemberships'][0]['membershipId'])