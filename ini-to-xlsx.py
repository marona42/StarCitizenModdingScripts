#!/usr/bin/python

# Convert global.ini => global.ini.xlsx

import sys
import configparser
from localization import * 

def main(args):
    try:
        inputFilename = "global.ini"
        if len(args) > 1:
            inputFilename = args[1]
        outputFilename = inputFilename + ".xlsx"
        print("Convert ini to xsls: {0} -> {1}".format(inputFilename, outputFilename))
        config = configparser.ConfigParser()
        if not config.read('convert.ini'):
            print('Note: No convert config file - convert.ini')
        print("Process ini...")
        inputIni = LocalizationIni.FromIniFile(inputFilename)
        if 'split-documents' in config:
            print("Split ini...")
            split = splitConfig(config['split-documents'])
            mainIni = LocalizationIni.Empty()
            splitInis = {}
            for splitFile in split.files:
                splitInis[splitFile] = LocalizationIni.Empty()
            for item in inputIni.getItems():
                keyFile = split.searchKeyFile(item[0])
                if keyFile:
                    splitInis[keyFile].putKeyValue(item[0], item[1])
                else:
                    mainIni.putKeyValue(item[0], item[1])
            print(f"Write output main {outputFilename}...")
            mainIni.saveToXlsxFile(outputFilename, "global.ini")
            print(f"Written lines: {mainIni.getItemsCount()}")
            for splitFile in splitInis:
                splitIni = splitInis[splitFile]
                print(f"Write output split {splitFile}.xlsx...")
                splitIni.saveToXlsxFile(splitFile + ".xlsx", splitFile)
                print(f"Written lines: {splitIni.getItemsCount()}")
        else:
            print("Write output xlsx...")
            inputIni.saveToXlsxFile(outputFilename, "global.ini")
            print(f"Written lines: {inputIni.getItemsCount()}")
    except KeyboardInterrupt:
        print("Interrupted")
        return 1
    except Exception as err:
        print("Error: {0}".format(err))
        return 1
    print('Done')
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
