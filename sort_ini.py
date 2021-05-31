import configparser

target_title='global_31.ini'

with open(target_title, 'r',encoding='utf​-8-sig') as f:
    config_string = '[DEFAULT]\n' + f.read()
origindata = configparser.ConfigParser(delimiters='=',strict=True,interpolation=None)
origindata.optionxform=str
origindata.read_string(config_string)

with open(target_title[:-4]+'_sorted.ini','w',encoding='utf​-8-sig') as f:
    for keyword in sorted(origindata['DEFAULT']):
        if '﻿' in keyword: keyword = keyword.replace("﻿","")
        f.write(keyword+'='+origindata['DEFAULT'][keyword]+'\n')