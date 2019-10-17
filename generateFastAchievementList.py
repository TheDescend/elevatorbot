import os, sys, json, pandas, openpyxl, xlsxwriter
import pandas.io.formats.excel
import config
from functions import getNameToHashMapByClanid,getTriumphsJSON, playerHasClears, getClearCount,playerHasFlawless,playerHasCollectible,playerHasTriumph,playerHasRole,getPlayerRoles
from dict import requirementHashes, getNameFromHashActivity,getNameFromHashCollectible,getNameFromHashRecords

import concurrent.futures
# pylint: disable=W0223
# pylint: disable=abstract-class-instantiated

def main():
    path = os.path.dirname(os.path.abspath(__file__))
    writer = pandas.ExcelWriter(path + '\\clanAchievementsShort.xlsx', engine='xlsxwriter') # pylint: disable=W0223

    #print(playerHasRole(4611686018468695677,'Levi Master','Y1'))

    clanids = [
        2784110, #Bloodoak I
        3373405, #BO2
        3702604, #BO3
        3556786, #Ascend
    ]

    for clanid in clanids:
        memberids = getNameToHashMapByClanid(clanid) # memberids['Hali'] is my destinyMembershipID
        #memberids = {'Hali':4611686018468695677,'Neria':4611686018484825875,'Skeptic':4611686018467605174}
        t1 = {}
        t2 = {}
        userRoles = {}
        with concurrent.futures.ProcessPoolExecutor() as executor:
            for username, (t1,t2) in zip(sorted(memberids.keys()), executor.map(getPlayerRoles, sorted(memberids.values()))):
                userRoles[username] = t1 + t2
        rolelist = []
        for _, yd in requirementHashes.items():
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


    #workbook = xlsxwriter.Workbook(path + '\\clanAchievementsShort.xlsx')


    workbook = writer.book

    redBG = workbook.add_format({'bg_color': '#FFC7CE'})
    greenBG = workbook.add_format({'bg_color': '#C6EFCE'})

    verticalRole = workbook.add_format({'bold': True, 'rotation': 90})
    #verticalRole.set_rotation(90)

    for _, worksheet in writer.sheets.items():
        worksheet.set_landscape()
        worksheet.set_row(0, None, verticalRole)
        worksheet.set_column(0, 0, 10)
        worksheet.set_column(1, 100, 3)
        worksheet.conditional_format("A2:ZZ300", {'type': 'text',
                                                    'criteria': 'containing',
                                                    'value': '-',
                                                    'format': redBG})
        worksheet.conditional_format("A2:ZZ300", {'type': 'text',
                                                    'criteria': 'containing',
                                                    'value': '+',
                                                    'format': greenBG})
        #print(wname + ' set')
    #worksheet.write(0, 0, 'This text is rotated', verticalRole)
    #worksheet.set_column('F:M', 6, verticalRole)
    writer.save()

    print('excel file created')
    # for year,yeardata in requirementHashes.items():
    #     curCol = 0
    #     worksheet.set_column(curCol, curCol, 15, bold)
    #     worksheet = writer.sheets[year + ' Roles']
    #     worksheet.set_column('A:AK', 2, None)
    #     for role,roledata in yeardata.items():
    #         curCol += 1
    #         for reqC, reqData in roledata.items():
    #             if reqC == 'flawless':
    #                 curCol += 1
    #                 #print('+1 for flawless')
    #             elif not reqC == 'requirements' and not reqC == 'replaced_by':
    #                 curCol += len(reqData)
    #                 #print(f'+{len(reqData)} for {reqC}')
    #                 #print(f'req {reqC} has length {len(reqData)} and content {reqData}')
    #                 #print(f'added req, curCol now {curCol}')
            
    #         worksheet.set_column(curCol, curCol, 15, bold)
    #         #print(f'{curCol} is bold.')

    #     worksheet.conditional_format("A2:ZZ300", {'type': 'text',
    #                                                 'criteria': 'containing',
    #                                                 'value': 'False',
    #                                                 'format': redBG})
    #     worksheet.conditional_format("A2:ZZ300", {'type': 'text',
    #                                                 'criteria': 'containing',
    #                                                 'value': 'True',
    #                                                 'format': greenBG})
    #     worksheet.set_zoom(80)

if __name__ == '__main__':
    main()

