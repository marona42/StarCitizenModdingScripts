#!/usr/bin/python

# Convert global.ini.xlsx => global.ini

import sys
from localization import * 

def main(args):
    try:
        inputFilename = "global.ini.xlsx"
        outputFilename = "global.ini"
        if len(args) > 1:
            inputFilename = args[1]
        if len(args) > 2:
            outputFilename = args[2]
        print("Convert xsls to ini: {0} -> {1}".format(inputFilename, outputFilename))
        print("Process xlsx...")
        inputInis = LocalizationIni.FromXlsxFile(inputFilename, "global.ini", 2)
        originalIni = inputInis[0];
        translateIni = inputInis[1];
        VerifyTranslationIni(originalIni, translateIni, {})
        print("Write output...")
        outputIni = LocalizationIni.Empty()
        for key, value in originalIni.getItems():
            writeValue = translateIni.getKeyValue(key)
            if not writeValue:
                writeValue = value
            outputIni.putKeyValue(key, writeValue)
        outputIni.saveToIniFile(outputFilename)            
    except KeyboardInterrupt:
        input("Interrupted")
        return 1    
    except Exception as err:
        input("Error: {0}".format(err))
        return 1
    input('Done')
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
