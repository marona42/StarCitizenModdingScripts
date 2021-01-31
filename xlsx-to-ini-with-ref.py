#!/usr/bin/python

# Convert global.ini.xlsx & global_ref.ini => global.ini

import sys
import configparser
from localization import * 

versionFormat = ' - v{0}'
versionAddKeys = set(['pause_ForegroundMainMenuScreenName'])
allowOutdatedTranslationUse = True
excludeTranslateKeys = set(['mobiGlas_ui_notification_Party_Title'])
excludeUIInteractors = False

def isInteraction(name):
    if name.startswith("ui_interactor_") or name.startswith("interaction_") or name.startswith("ui_PromptPress") or name.startswith("innerthought_grimhex_elevator") :
        return True
    if name == "generic_go_down" or name == "generic_go_up" or name == "generic_lower_floor" or name == "generic_upper_floor":
        return True
    return False

def compareFormats(refValue, origValue):
    refFormats = LocalizationIni.GetUnnamedFormats(refValue)
    origFormats = LocalizationIni.GetUnnamedFormats(origValue)
    if refFormats != origFormats:
        return False
    refFormats = LocalizationIni.GetNamedFormats(refValue)
    origFormats = LocalizationIni.GetNamedFormats(origValue)
    if refFormats != origFormats:
        return False
    return True

def threeWayMerge(key, refValue, origValue, translateValue):
    if (refValue == origValue):
        return translateValue
    if allowOutdatedTranslationUse and compareFormats(refValue, origValue):
        print("Note: outdated translation key used: ", key)
        return translateValue
    print("Note: reference key used: ", key)
    return refValue

def isTranslatableKey(key):
    return ((not excludeUIInteractors) or (not isInteraction(key))) and (key not in excludeTranslateKeys)

def main(args):
    try:
        inputFilename = "global.ini.xlsx"
        outputFilename = "global.ini"
        referenceIniFilename = "global_ref.ini"
        if len(args) > 1:
            inputFilename = args[1]
        if len(args) > 2:
            outputFilename = args[2]
        if len(args) > 3:
            referenceIniFilename = args[3]
        print("Convert ini to xsls (with ref {2}): {0} -> {1}".format(inputFilename, outputFilename, referenceIniFilename))
        splitDocuments = []
        verifyOptions = { 'allowed_characters_file': 'allowed_codepoints.txt' }
        config = configparser.ConfigParser()
        if config.read('convert.ini'):
            if 'general' in config:
                generalConfig = dict(config.items('general'))
                if 'allow_outdated_translation' in generalConfig:
                    allowOutdatedTranslationUse = IsTruthCondition(generalConfig['allow_outdated_translation'])
                if 'exclude_translate_keys' in generalConfig:
                    excludeTranslateKeys.update([x.strip() for x in filter(None, generalConfig['exclude_translate_keys'].split(',')) if len(x.strip()) > 0])
            if 'verify' in config:
                verifyOptions.update(dict(config.items('verify')))
            if 'split-documents' in config:
                splitDocuments = splitConfig(config['split-documents']).files
        else:
            print('Note: No convert config file - convert.ini')
        if len(args) > 4:
            version = " ".join(args[4:])
        else:
            version = input("Enter version (optional): ")
        print("Process reference ini...")
        referenceIni = LocalizationIni.FromIniFile(referenceIniFilename)
        print("Reference keys: {0}".format(referenceIni.getItemsCount()))
        print("Process xlsx...")
        inputInis = LocalizationIni.FromXlsxFiles(inputFilename, "global.ini", 2, splitDocuments)
        originalIni = inputInis[0];
        translateIni = inputInis[1];
        if originalIni.getItemsCount() > 0:
            print("Translated keys: {0}/{1} ({2:.2f}%)".format(translateIni.getItemsCount(), originalIni.getItemsCount(),
                                                               translateIni.getItemsCount() / originalIni.getItemsCount() * 100))
            print("           left: {0}".format(originalIni.getItemsCount() - translateIni.getItemsCount()))
            #print("           keys: {0}".format(originalIni.getKeysSet() - translateIni.getKeysSet()))
        VerifyTranslationIni(originalIni, translateIni, verifyOptions)
        print("Write output...")
        outputIni = LocalizationIni.Empty()
        for key, value in referenceIni.getItems():
            writeValue = value
            if translateIni.isContainKey(key) and isTranslatableKey(key):
                writeValue = threeWayMerge(key, value, originalIni.getKeyValue(key), translateIni.getKeyValue(key))
            if version and (key in versionAddKeys):
                writeValue = writeValue + versionFormat.format(version)
                print("Info: Added version to key: {0}".format(key))
            outputIni.putKeyValue(key, writeValue)
        outputIni.saveToIniFile(outputFilename)
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
