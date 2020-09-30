import os, sys, json, pandas, openpyxl, xlsxwriter
import pandas.io.formats.excel
import config
from functions import getNameToHashMapByClanid,getPlayerRoles
from dict import requirementHashes, clanids

# pylint: disable=W0223
# pylint: disable=abstract-class-instantiated
async def createSheet():
    path = os.path.dirname(os.path.abspath(__file__))
    sheetpath = path + '\\clanAchievementsShort.xlsx'
    writer = pandas.ExcelWriter(sheetpath, engine='xlsxwriter') # pylint: disable=W0223


    for clanid in clanids:
        memberids = await getNameToHashMapByClanid(clanid) # memberids['Hali'] is my destinyMembershipID
        t1 = {}
        t2 = {}
        userRoles = {}
        for username, userid in memberids.items():
            (t1,t2) = await getPlayerRoles(userid)
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
            worksheet.write(0, idx+1, val)
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
    return sheetpath

if __name__ == '__main__':
    await createSheet()