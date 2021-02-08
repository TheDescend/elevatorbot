from functions.dataTransformation import hasLowman, getClearCount
from functions.roleLookup import hasRole
from static.dict import premenHashes, cosHashes, lwHashes

spiderHash = 863940356

nervane = 4611686018470292252
neria = 4611686018484825875
hali = 4611686018468695677
ghost = 4611686018483427800
mystic = 4611686018467630031
red = 4611686018467395436


#assert hasRole(nervane ,'Solo Heroic Zero Hour', 'Addition')
#assert getSystemAndChars(neria) == [(3, 2305843009409826818), (3, 2305843009424985689), (3, 2305843009438144007), (3, 2305843009453204757)]
assert hasRole(red, 'Garden of Salvation Master', 'Y3')
assert hasLowman(mystic,2,premenHashes,False)

assert hasLowman(hali,3,premenHashes)
assert hasLowman(neria, 3, premenHashes)
assert getClearCount(hali, cosHashes) >= 54
#assert getClearCount(neria, cosHashes) >= 52
assert hasRole(neria,'Three-Man Heroic Menagerie','Addition')
assert hasRole(neria, 'Crown of Sorrow Master', 'Y2')
assert hasRole(neria, 'Scourge of the Past Master', 'Y2')
assert hasRole(neria,'Three-Man Gahlran','Addition')

assert not hasRole(ghost, 'Solo Zero Hour', 'Addition')

#assert hasRole(nervane ,'Solo Heroic Zero Hour', 'Addition')
assert hasLowman(hali,3,lwHashes, False, [])
assert hasRole(neria,'Three-Man Heroic Menagerie','Addition')

assert hasRole(ghost, 'Last Wish', 'Y2')


print('all assertions passed')