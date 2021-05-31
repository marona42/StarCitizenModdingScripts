# makes the first xlsx for upload smartcat project
# requires export-smartcat.py, smartcat.ini
import configparser
import openpyxl as xl     #pip install openpyxl needed!

splitthreshold=50000

with open('global_ref.ini', 'r',encoding='utf​-8-sig') as f:        #target ref ini file
    origin_str = '[DEFAULT]\n' + f.read()
origindata = configparser.ConfigParser(delimiters='=',strict=True,interpolation=None)
origindata.optionxform=str
origindata.read_string(origin_str)

partcnt,splitcnt=1,1
wb=xl.workbook.Workbook()
ws=wb.active
ws.append(["en","ko"])      #put your target language to second element
for keyword in origindata['DEFAULT']:
    if ('(PH)' in origindata['DEFAULT'][keyword] or '[PH]' in origindata['DEFAULT'][keyword] or 'WIP' in origindata['DEFAULT'][keyword] or
        '*DELETE THIS*' in origindata['DEFAULT'][keyword] or 'DO NOT USE' in origindata['DEFAULT'][keyword] or 'PLACEHOLDER' in origindata['DEFAULT'][keyword] or
        origindata['DEFAULT'][keyword]=='' ): continue    #exclude by text
    ws.append([f"{keyword}={origindata['DEFAULT'][keyword]}"])
    if splitcnt > splitthreshold:
        splitcnt=0
        wb.save(filename=f"global_push_P{partcnt}.xlsx")
        partcnt+=1
        wb=xl.workbook.Workbook()
        ws=wb.active
wb.save(filename=f"global_push_P{partcnt}.xlsx")
print(f"Split ini with {partcnt} xlsx file(s) Done")
