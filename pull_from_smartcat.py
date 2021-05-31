# pull from smartcat project.
# requires export-smartcat.py, smartcat.ini
import os
import configparser
import openpyxl as xl     #pip install openpyxl needed!
import export_smartcat

config_title='sc_ko'
docs = export_smartcat.main(['pullfs',config_title]) #[[doc id,이름],...]

log = open('pull.log','w')

transdata,phdata={},{}
overwrited,nodata,excluded=0,0,0
for doc in docs:
    if len(docs) > 1:
        print(f"Reading {doc[1]}")
    wd= xl.load_workbook(doc[1]+'.xlsx',read_only=True)
    ws = wd.active
    for rowd in ws.iter_rows(min_row=2):
        #print(rowd[0].value)
        if len(rowd)>2: print(f"Warning: multiple rows detected in {rowd}")
        if rowd[1].value is not None:
            if '=' not in rowd[1].value: print(f"Warning: {rowd[1].value}")
            (inkey,indata) = rowd[1].value.split('=',1)
        else:
            continue
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

with open('PHkeywords.ini', 'r',encoding='utf​-8-sig') as f:
    config_string = '[DEFAULT]\n' + f.read()
phdata = configparser.ConfigParser(delimiters='=',strict=True,interpolation=None)
phdata.optionxform=str
phdata.read_string(config_string)

with open('manualkeywords.ini', 'r',encoding='utf​-8-sig') as f:
    config_string = '[DEFAULT]\n' + f.read()
mndata = configparser.ConfigParser(delimiters='=',strict=True,interpolation=None)
mndata.optionxform=str
mndata.read_string(config_string)

if os.path.exists("global_pull.ini"):
    os.rename('global_pull.ini','global_pull_old.ini')

with open('global_pull.ini','w',encoding='utf​-8-sig') as f:
    #f.write('\ufeff')       #UTF8 with BOM
    for keyword in origindata['DEFAULT']:
        if '﻿' in keyword: keyword = keyword.replace("﻿","")
        if keyword in transdata:
            #if not transdata[keyword].isascii():                #for calculate progress
            f.write(keyword+'='+transdata[keyword]+'\n')
        else:   #doesn't exist in smartcat data
            #print(f"Warning : No translated data of '{keyword}', write original data instead.")
            if keyword in phdata['DEFAULT']:    #check if data exist in PHKeywords.ini
                f.write(keyword+'='+phdata['DEFAULT'][keyword]+'\n')
                continue
            else:
                f.write(keyword+'='+origindata['DEFAULT'][keyword]+'\n')
            if '[PH]' in origindata['DEFAULT'][keyword] or 'WIP' in origindata['DEFAULT'][keyword] or '*DELETE THIS*' in origindata['DEFAULT'][keyword] :
                excluded+=1
                continue
            log.write(f"Warning : No translated data of '{keyword}', write original data instead.\n")
            nodata+=1

    for keyword in mndata['DEFAULT']:
        if keyword in transdata:
            print(f"manual input keyword '{keyword}' is already exist in translated data")
        else:
            f.write(keyword+'='+mndata['DEFAULT'][keyword]+'\n')

decnt=0
with open('depreciated_keywords.log','w') as f:
    for keyword in transdata:
        if keyword not in origindata['DEFAULT']:
            f.write(f"keyword '{keyword}' is not used at original .ini file anymore.\n")
            decnt+=1

if overwrited+nodata>1:
    print(f"Merge done with {overwrited} overwritten, {nodata} original data uses, {excluded} placeholders")
else:
    print(f"Merge successfully done with skipping {excluded} placeholders")
if decnt>0:
    print("There are depreciated keywords on translated data. please check depreciated_keywords.log file.")