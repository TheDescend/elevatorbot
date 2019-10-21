import os, sys, json, pandas, openpyxl, xlsxwriter
import pandas.io.formats.excel
import config
from functions import getNameToHashMapByClanid,getPlayerRoles
from dict import requirementHashes

# pylint: disable=W0223
# pylint: disable=abstract-class-instantiated

path = os.path.dirname(os.path.abspath(__file__))
writer = pandas.ExcelWriter(path + '\\clanAchievementsShort.xlsx', engine='xlsxwriter') # pylint: disable=W0223

clanids = [
    2784110, #Bloodoak I
    3373405, #BO2
    3702604, #BO3
    3702604, #Ascend Kappa
]

for clanid in clanids:
    memberids = getNameToHashMapByClanid(clanid) # memberids['Hali'] is my destinyMembershipID
    #memberids = {'Hali':4611686018468695677,'Neria':4611686018484825875,'Skeptic':4611686018467605174}
    t1 = {}
    t2 = {}
    userRoles = {}
    for username, userid in memberids.items():
        (t1,t2) = getPlayerRoles(userid)
        userRoles[username] = t1 + t2
    rolelist = []
    for y, yd in requirementHashes.items():
        rolelist += sorted(yd.keys())
    table = {}
    for username in memberids.keys():
        table[username] = []
        for role in rolelist:
            #print(f'{role} in {userRoles[username]}')
            if role in userRoles[username]:
                table[username].append('+')
            else:
                table[username].append('-')
    df = pandas.DataFrame()
    df = df.from_dict(table, orient='index', columns=rolelist)
    columnlist=df.columns
    df.to_excel(writer, header=False, startrow=1, sheet_name = str(clanid) + ' Roles')
    workbook  = writer.book
    worksheet = writer.sheets[str(clanid) + ' Roles']
    for idx, val in enumerate(columnlist):
        worksheet.write(0, idx, val)
print('generating sheets...')

workbook = writer.book
bold = workbook.add_format({'bold': True})

redBG = workbook.add_format({'bg_color': '#FFC7CE'})
greenBG = workbook.add_format({'bg_color': '#C6EFCE'})

verticalRole = workbook.add_format({'bold': True, 'rotation': 90})

for wname, worksheet in writer.sheets.items():
    worksheet.set_landscape()
    worksheet.set_row(0, None, verticalRole)
    worksheet.set_column(0, 100, 5)
    worksheet.conditional_format("A2:ZZ300", {'type': 'text',
                                                'criteria': 'containing',
                                                'value': '-',
                                                'format': redBG})
    worksheet.conditional_format("A2:ZZ300", {'type': 'text',
                                                'criteria': 'containing',
                                                'value': '+',
                                                'format': greenBG})
writer.save()

print('excel file created')