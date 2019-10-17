import os, sys, json, pandas, openpyxl, xlsxwriter

import config
from functions import getNameToHashMapByClanid,getTriumphsJSON, playerHasClears, getClearCount,playerHasFlawless,playerHasCollectible,playerHasTriumph,playerHasRole,getPlayerRoles
from dict import requirementHashes, getNameFromHashActivity,getNameFromHashCollectible,getNameFromHashRecords

# pylint: disable=W0223
# pylint: disable=abstract-class-instantiated

path = os.path.dirname(os.path.abspath(__file__))
writer = pandas.ExcelWriter(path + '\\clanAchievements.xlsx', engine='xlsxwriter') # pylint: disable=W0223

#print(playerHasRole(4611686018468695677,'Levi Master','Y1'))

clanid = 2784110 #Bloodoak I

memberids = getNameToHashMapByClanid(clanid) # memberids['Hali'] is my destinyMembershipID
# temp = {}
# for key in sorted(memberids)[:3]:
#     temp[key] = memberids[key]
# memberids = temp #made smaller for debugging
membersystem = dict()
userRoles = {}
cur = 0
for year,yeardata in requirementHashes.items():
    yearResult = {}
    for username, userid in memberids.items():
        if not username in userRoles.keys():
            userRoles[username] = []
        #print('Processing user: ' + username + ' with id ' + userid)
        sys.stdout.write(f"\r({100*cur//len(memberids)}%) Processing user {username} with id {userid}" + ' '*20)
        sys.stdout.flush()
        if cur < len(memberids):
            cur += 1
        triumphs = getTriumphsJSON(userid)
        yearResult[username] = {}
        
        for role,roledata in yeardata.items():
            rolestatus = len(roledata) > 0
            if not 'requirements' in roledata:
                print('malformatted requirementHashes')
                continue
            for req in roledata['requirements']:
                if req == 'clears':
                    creq = roledata['clears']
                    for raid in creq:
                        requiredN = raid['count']
                        raidHash0 = raid['actHashes'][0]
                        activityname = getNameFromHashActivity[str(raidHash0)]
                        condition = activityname + ' clears (' + str(requiredN) + ')'

                        boolHasClears = playerHasClears(userid, requiredN, raid['actHashes'])
                        cc = 0
                        for actHash in raid['actHashes']:
                            cc += getClearCount(userid, actHash)
                        yearResult[username][condition] = str(boolHasClears) + ' (' + str(cc) + ')'
                        rolestatus &= boolHasClears
                elif req == 'flawless':
                    condition = 'flawless ' + getNameFromHashActivity[str(roledata['flawless'][0])]
                    if playerHasFlawless(userid, roledata['flawless']):
                            yearResult[username][condition] = 'True'
                            found = True
                    else:
                        rolestatus = False
                        yearResult[username][condition] = 'False'
                elif req == 'collectibles':
                    for collectible in roledata['collectibles']:
                        condition = getNameFromHashCollectible[str(collectible)]
                        if playerHasCollectible(userid, collectible):
                            yearResult[username][condition] = 'True'
                        else:
                            yearResult[username][condition] = 'False'
                            rolestatus = False
                elif req == 'records':
                    for recordHash in roledata['records']:
                        condition = getNameFromHashRecords[str(recordHash)]
                        if condition in yearResult[username]:
                            condition += '_'
                        status = playerHasTriumph(userid, recordHash)
                        yearResult[username][condition] = str(status)
                        rolestatus &= status

            yearResult[username][role] = str(rolestatus)
            if rolestatus:
                userRoles[username].append(role)
            else:
                userRoles[username].append('')

    df = pandas.DataFrame(yearResult)
    df = df.transpose()

    df.to_excel(writer, sheet_name = year + ' Roles')
print('generating sheets...')
actualRoles = {}
for username, uid in memberids.items():
    actualRoles[username] = getPlayerRoles(uid)
userRoles = {u:[rs if rs in actualRoles[u] else '' for rs in userRoles[u]] for u,r in userRoles.items()}

pandas.DataFrame(userRoles).transpose().to_excel(writer, header=None, sheet_name = 'User Roles')
workbook = writer.book
bold = workbook.add_format({'bold': True})

redBG = workbook.add_format({'bg_color': '#FFC7CE'})
greenBG = workbook.add_format({'bg_color': '#C6EFCE'})

# importantColumns = {
#     'Y1'        : ['A','D','G','J','M','P','W'],
#     'Y2'        : ['A','F', 'M','R','X','AE','AK'],
#     'Y3'        : ['A'],
#     'Addition'  : ['A','C','E','G','I']
# }

worksheet = writer.sheets['User Roles']
worksheet.set_column('A:A', 15, bold)
worksheet.set_column('B:M', 6, bold)

for year,yeardata in requirementHashes.items():
    curCol = 0
    worksheet.set_column(curCol, curCol, 15, bold)
    worksheet = writer.sheets[year + ' Roles']
    worksheet.set_column('A:AK', 2, None)
    for role,roledata in yeardata.items():
        curCol += 1
        for reqC, reqData in roledata.items():
            if reqC == 'flawless':
                curCol += 1
                #print('+1 for flawless')
            elif not reqC == 'requirements' and not reqC == 'replaced_by':
                curCol += len(reqData)
                #print(f'+{len(reqData)} for {reqC}')
                #print(f'req {reqC} has length {len(reqData)} and content {reqData}')
                #print(f'added req, curCol now {curCol}')
        
        worksheet.set_column(curCol, curCol, 15, bold)
        #print(f'{curCol} is bold.')

    worksheet.conditional_format("A2:ZZ300", {'type': 'text',
                                                'criteria': 'containing',
                                                'value': 'False',
                                                'format': redBG})
    worksheet.conditional_format("A2:ZZ300", {'type': 'text',
                                                'criteria': 'containing',
                                                'value': 'True',
                                                'format': greenBG})
    worksheet.set_zoom(80)
writer.save()
print('excel file created')
