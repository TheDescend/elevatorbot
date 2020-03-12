from functions.roles import hasRole
from functions.dataLoading import getPlayersPastPVE

from pprint import pprint

nervane = 4611686018470292252
hali = 4611686018468695677

def nervanecheck():
    assert hasRole(nervane ,'Solo Heroic Zero Hour', 'Addition')

pastpve = getPlayersPastPVE(hali)
for pve in pastpve:
    if 4 in pve['activityDetails']['modes']:
        pprint(pve)
        break


