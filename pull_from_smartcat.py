# pull from smartcat project.
# requires export-smartcat.py, smartcat.ini
import configparser
import openpyxl as xl     #pip install openpyxl needed!
import export_smartcat

config_title='sc_ko'
docs = export_smartcat.main(['pullfs',config_title]) #[[doc id,이름],...]

log = open('pull.log','w')

transdata={}
overwrited,nodata=0,0
for doc in docs:
    if len(docs) > 1:
        print(f"Reading {doc[1]}")
    wd= xl.load_workbook(doc[1]+'.xlsx',read_only=True)
    ws = wd.active
    for rowd in ws.rows:
        #print(rowd[0].value)
        if len(rowd)>1: print(f"Warning: multi row detected in {rowd}")
        (inkey,indata) = rowd[0].value.split('=',1)
        if inkey in transdata != None:
            #print(f"Warning: overwrite duplicated keyword in {rowd}({inkey}) : {transdata[inkey]}")
            log.write(f"Warning: overwrite duplicated keyword in {rowd}({inkey}) : {transdata[inkey]}\n")
            overwrited+=1
        transdata[inkey]=indata


with open('global_ref.ini', 'r',encoding='utf​-8-sig') as f:
    config_string = '[DEFAULT]\n' + f.read()
origindata = configparser.ConfigParser(delimiters='=',strict=True,interpolation=None)
origindata.optionxform=str
origindata.read_string(config_string)

with open('global_pull.ini','w',encoding='utf​-8-sig') as f:
    #f.write('\ufeff')       #UTF8 with BOM
    for keyword in origindata['DEFAULT']:
        if '﻿' in keyword: keyword = keyword.replace("﻿","")
        if keyword in transdata:
            f.write(keyword+'='+transdata[keyword]+'\n')
        else:
            #print(f"Warning : No translated data of '{keyword}', write original data instead.")
            log.write(f"Warning : No translated data of '{keyword}', write original data instead.\n")
            f.write(keyword+'='+origindata['DEFAULT'][keyword]+'\n')
            nodata+=1

with open('depreciated_keywords.log','w') as f:
    for keyword in transdata:
        if keyword not in origindata['DEFAULT']:
            f.write(f"keyword '{keyword}' is not used at original .ini file anymore.\n")

if overwrited+nodata>1:
    print(f"Merge done with {overwrited} overwritten, {nodata} original data uses")
else:
    print("Merge successfully done")