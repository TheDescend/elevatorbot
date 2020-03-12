from functions.roles import hasRole
from functions.dataLoading import getPlayersPastPVE
from functions.dataTransformation import hasLowman

from pprint import pprint

nervane = 4611686018470292252
hali = 4611686018468695677
neria = 4611686018484825875

#assert hasRole(nervane ,'Solo Heroic Zero Hour', 'Addition')
#assert hasLowman(hali,3,lwHashes, False, [])
assert hasRole(neria,'Three-Man Heroic Menagerie','Addition')

