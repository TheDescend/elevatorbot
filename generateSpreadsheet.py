import os, json, pandas, openpyxl, xlsxwriter

import config
from functions import getNameToHashMapByClanid,getTriumphsJSON, playerHasClears, getClearCount,playerHasFlawless,playerHasCollectible,playerHasTriumph,playerHasRole
from dict import requirementHashes, getNameFromHashActivity,getNameFromHashCollectible,getNameFromHashRecords

# pylint: disable=W0223
# pylint: disable=abstract-class-instantiated

path = os.path.dirname(os.path.abspath(__file__))
writer = pandas.ExcelWriter(path + '\\clanAchievements.xlsx', engine='xlsxwriter') # pylint: disable=W0223

#print(playerHasRole(4611686018468695677,'Levi Master','Y1'))

clanid = 2784110 #Bloodoak I

memberids = getNameToHashMapByClanid(clanid) # memberids['Hali'] is my destinyMembershipID
membersystem = dict()
userRoles = {}

for year,yeardata in requirementHashes.items():
    yearResult = {}
    for username, userid in memberids.items():
        if not username in userRoles.keys():
            userRoles[username] = []
        print('Processing user: ' + username + ' with id ' + userid)
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

pandas.DataFrame(userRoles).transpose().to_excel(writer, header=None, sheet_name = 'User Roles')
workbook = writer.book
bold = workbook.add_format({'bold': True})

redBG = workbook.add_format({'bg_color': '#FFC7CE'})
greenBG = workbook.add_format({'bg_color': '#C6EFCE'})

importantColumns = {
    'Y1'        : ['A','D','G','J','M','P','W'],
    'Y2'        : ['A','F', 'M','R','X','AE','AK'],
    'Y3'        : ['A'],
    'Addition'  : ['A','C','E','G','I']
}

worksheet = writer.sheets['User Roles']
worksheet.set_column('A:A', 15, bold)
worksheet.set_column('B:M', 6, bold)

for year,yeardata in requirementHashes.items():
    worksheet = writer.sheets[year + ' Roles']
    worksheet.set_column('A:AK', 2)
    for header in worksheet.headers:
        for role in yeardata:
            if header == role:
                worksheet.set_column(header.range, 6, bold) #TODO

    for let in importantColumns[year]:
        worksheet.set_column(let +':'+let, 15, bold)
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
