# push to smartcat project.
# requires export-smartcat.py, smartcat.ini
import configparser
import openpyxl as xl     #pip install openpyxl needed!
import export_smartcat

config_title='sc_ko'
splitthreshold=50000
log = open('pull.log','w')

transdata={}
overwrited,nodata=0,0

with open('global_ref.ini', 'r',encoding='utf​-8-sig') as f:
    origin_str = '[DEFAULT]\n' + f.read()
origindata = configparser.ConfigParser(delimiters='=',strict=True,interpolation=None)
origindata.optionxform=str
origindata.read_string(origin_str)

partcnt,splitcnt=1,1
wb=xl.workbook.Workbook()
ws=wb.active
for keyword in origindata['DEFAULT']:
    if ('WIP' in keyword or '2950' in keyword): continue    #exclude by keyword
    if ('(PH)' in origindata['DEFAULT'][keyword] or '[PH]' in origindata['DEFAULT'][keyword] or 'WIP' in origindata['DEFAULT'][keyword] or
        '*DELETE THIS*' in origindata['DEFAULT'][keyword] or 'DO NOT USE' in origindata['DEFAULT'][keyword] or 'PLACEHOLDER' in origindata['DEFAULT'][keyword] or
        origindata['DEFAULT'][keyword]=='' ): continue    #exclude by text
    ws.append([f"{keyword}={origindata['DEFAULT'][keyword]}"])
    if splitcnt > splitthreshold:
        splitcnt=0
        wb.save(filename=f"_global_P{partcnt}.ini.xlsx")
        partcnt+=1
        wb=xl.workbook.Workbook()
        ws=wb.active
wb.save(filename=f"_global_P{partcnt}.ini.xlsx")
print("Split ini to xlsx Done")
