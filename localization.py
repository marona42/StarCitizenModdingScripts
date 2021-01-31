#!/usr/bin/python

# Please install deps before usage:
#
# python -m pip install pandas
# python -m pip install xlrd
# python -m pip install xlsxwriter

import os
import sys
import pandas
import codecs
import math
import re
import collections

class splitConfig:
    @staticmethod
    def __ReadConfigKey(config, key_name):
        if not key_name in config:
            raise Exception(f"Missing key '{key_name}' in smartCAT config")
        key_value = config[key_name].strip()
        if len(key_value) == 0:
            raise Exception(f"Empty key '{key_name}' value in smartCAT config")
        return key_value

    @staticmethod
    def __ReadConfigKeyArray(config, key_name):
        key_value = splitConfig.__ReadConfigKey(config, key_name)
        return [x.strip() for x in key_value.split(',')]

    def __init__(self, config):
        self.files = []
        self.prefixMap = {}
        for file in config.keys():
            self.files.append(file)
            for prefix in [x.strip() for x in config[file].split(',')]:
                self.prefixMap[prefix] = file

    def searchKeyFile(self, key):
        for prefix in self.prefixMap:
            if key.startswith(prefix):
                return self.prefixMap[prefix]
        return None

class IniParseError(Exception):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
        lineNumber -- number of line which can't be parsed
    """

    def __init__(self, message, lineNumber):
        self.message = message
        self.lineNumber = lineNumber

    def __str__(self):
        return f'{self.message} at line: {self.lineNumber}'

class XlsxParseError(Exception):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
        lineNumber -- number of line which can't be parsed
    """

    def __init__(self, message, lineNumber):
        self.message = message
        self.lineNumber = lineNumber

    def __str__(self):
        return f'{self.message} at line: {self.lineNumber}'

class LocalizationIni:
    __utf8_bom = u'\ufeff'
    __delimiter = '='
    __whitespaces = "\r\n\t\ufeff"
    __namedFormatExpr = re.compile(r'\~[a-z]+\([^\)]*\)')
    __unnamedFormatExpr = re.compile(r'<[^-=< ][^>]*>|%ls|%s|%S|%i|%I|%u|%d|%[0-9.]*f|%\.\*f')
    __englishWordsExpr = re.compile(r'[A-Za-z]+')
    __parseExceptions = False

    @staticmethod
    def __RaiseException(exception):
        if LocalizationIni.__parseExceptions:
            raise exception
        else:
            input("Error: {0}".format(exception))

    @staticmethod
    def __ParseKeyValue(line):
        if line:
            strippedLine = line.strip(LocalizationIni.__whitespaces)
            if strippedLine:
                return strippedLine.split(LocalizationIni.__delimiter, 1)
        return None

    @staticmethod
    def __ParseXlsxCellValue(line):
        try:
            if math.isnan(line):
                return None
            else:
                return LocalizationIni.__ParseKeyValue(line)
        except Exception as e:
            return LocalizationIni.__ParseKeyValue(line)

    @staticmethod
    def __LoadFromIniFile(filename):
        data = collections.OrderedDict()
        with codecs.open(filename, "r", "utf-8") as inputFile:
            lineNumber = 1
            for line in inputFile:
                parts = LocalizationIni.__ParseKeyValue(line)
                if parts:
                    if len(parts) != 2:
                        LocalizationIni.__RaiseException(IniParseError("Missing key value separator '=': {0}".format(parts[0]), lineNumber))
                    else:
                        data[parts[0]] = parts[1]
                lineNumber += 1
        return data

    @staticmethod
    def __LoadFromXlsxFileColumn(filename, sheetName, columnIndex):
        data = collections.OrderedDict()
        with pandas.ExcelFile(filename) as inputFile:
            sheet = inputFile.parse(sheet_name=sheetName)
            lineNumber = 1
            for row in sheet.values:
                if columnIndex >= len(row):
                   LocalizationIni.__RaiseException(XlsxParseError("Invalid column index {0} for row".format(columnIndex), lineNumber))
                else:
                    parts = LocalizationIni.__ParseXlsxCellValue(row[columnIndex]);
                    if parts:
                        if len(parts) != 2:
                            LocalizationIni.__RaiseException(XlsxParseError("Missing key value separator '=': {0}".format(parts[0]), lineNumber))
                        else:
                            data[parts[0]] = parts[1]
                lineNumber += 1
        return data

    @staticmethod
    def __LoadFromXlsxFileColumns(filename, sheetName, columnsCount):
        data = []
        columnIndex = 0
        while columnIndex < columnsCount:
            data.append(collections.OrderedDict())
            columnIndex += 1
        with pandas.ExcelFile(filename) as inputFile:
            sheet = inputFile.parse(sheet_name=sheetName)
            lineNumber = 1
            for row in sheet.values:
                if len(row) == 0:
                    LocalizationIni.__RaiseException(XlsxParseError("Less than {0} columns found".format(columnsCount), lineNumber))
                    lineNumber += 1
                    continue
                parts = LocalizationIni.__ParseXlsxCellValue(row[0]);
                if parts:
                    if len(parts) != 2:
                        LocalizationIni.__RaiseException(XlsxParseError("Missing key value separator '=': {0}".format(parts[0]), lineNumber))
                    else:
                        data[0][parts[0]] = parts[1]
                        columnIndex = 1
                        while (columnIndex < columnsCount) and (columnIndex < len(row)):
                            subParts = LocalizationIni.__ParseXlsxCellValue(row[columnIndex]);
                            if subParts:
                                if len(subParts) != 2:
                                    LocalizationIni.__RaiseException(XlsxParseError("Missing translation key value separator '=': {0}".format(parts[0]), lineNumber))
                                else:
                                    if subParts[0] != parts[0]:
                                        LocalizationIni.__RaiseException(XlsxParseError("Translation key change found: {0} -> {1}".format(parts[0], subParts[0]), lineNumber))
                                    else:
                                        data[columnIndex][subParts[0]] = subParts[1]
                            columnIndex += 1
                lineNumber += 1
        return data

    @staticmethod
    def Empty():
        return LocalizationIni(collections.OrderedDict())

    @staticmethod
    def FromIniFile(filename):
        return LocalizationIni(LocalizationIni.__LoadFromIniFile(filename))

    @staticmethod
    def FromXlsxFile(filename, sheetName):
        return LocalizationIni(LocalizationIni.__LoadFromXlsxFileColumn(filename, sheetName, 0))

    @staticmethod
    def FromXlsxFile(filename, sheetName, columnsCount):
        result = []
        if columnsCount > 0:
            dataArray = LocalizationIni.__LoadFromXlsxFileColumns(filename, sheetName, columnsCount)
            for data in dataArray:
                result.append(LocalizationIni(data))
        return result

    @staticmethod
    def FromXlsxFiles(filename, sheetName, columnsCount, filenames):
        result = []
        if columnsCount > 0:
            dataArray = LocalizationIni.__LoadFromXlsxFileColumns(filename, sheetName, columnsCount)          
            for filename in filenames:
                additionalDataArray = LocalizationIni.__LoadFromXlsxFileColumns(filename + ".xlsx", filename, columnsCount)
                for i in range(0, columnsCount):
                    dataArray[i].update(additionalDataArray[i])
            for data in dataArray:
                result.append(LocalizationIni(data))
        return result

    def __init__(self, data):
        self.data = data

    def getItems(self):
        return self.data.items()

    def getItemsCount(self):
        return len(self.data)

    def isContainKey(self, key):
        return key in self.data

    def getKeyValue(self, key):
        return self.data.get(key)

    def putKeyValue(self, key, value):
        self.data[key] = value

    def getKeysSet(self):
        return set(self.data)

    def saveToIniFile(self, filename):
        with codecs.open(filename, "w", "utf-8") as outputFile:
            outputFile.write(LocalizationIni.__utf8_bom)
            for key, value in self.data.items():
                outputFile.write(key)
                outputFile.write(LocalizationIni.__delimiter)
                outputFile.write(value)
                outputFile.write('\r\n')

    def saveToXlsxFile(self, filename, sheetName):
        outputData = [ 'en' ]
        for key, value in self.data.items():
            line = key + LocalizationIni.__delimiter + value
            outputData.append(line)
        dataFrame = pandas.DataFrame(outputData, columns=[ 'A' ])
        dataFrame.to_excel(filename, sheet_name=sheetName, encoding='utf8', index=False, header=False)

    @staticmethod
    def GetNamedFormats(value):
        return set(LocalizationIni.__namedFormatExpr.findall(value))

    @staticmethod
    def GetUnnamedFormats(value):
        return LocalizationIni.__unnamedFormatExpr.findall(value)

    @staticmethod
    def GetTextWithoutFormats(value, removeFormats):
        result = value
        for removeFormat in removeFormats:
            result = result.replace(removeFormat, " ")
        return result

    @staticmethod
    def GetCleanText(value, *formats):
        result = value.replace("\\n", " ")
        for removeFormat in formats:
            result = LocalizationIni.GetTextWithoutFormats(result, removeFormat)
        return result

    @staticmethod
    def GetEnglishWords(value):
        return set(LocalizationIni.__englishWordsExpr.findall(value.replace("\\n", " ")))

    def SetEnableParseExceptions(enable):
        LocalizationIni.__parseExceptions = enable;

lostNewlineExpr = re.compile(r'[^\\]\\[^n\\]')
spaceBeforeNewlineExpr = re.compile(r' \\n')
truths = set(['True', 'true', 1, '1'])

def IsTruthCondition(value):
    return value in truths

def ReadCodepointCharactersSet(inputFilename):
    characterSet = set({ ' ', '\t' }); #, '\xa0'
    try:
        with codecs.open(inputFilename, "r", "utf-8") as inputFile:
            while True:
                prefix = inputFile.read(2)
                if not prefix:
                    break;
                if prefix != '\\u':
                    input("Found invalid prefix: {0}".format(prefix))
                    return 1
                codepoint = inputFile.read(4)
                if not codepoint:
                    input("Missing codepoint")
                    return 1
                characterSet.add(chr(int(codepoint, 16)))
    except Exception as err:
        input("Parse codepoints file error: {0}".format(err))
        return set()
    return characterSet

def VerifyTranslationIni(originalIni, translationIni, options):
    lostNewline = ('lost_newline' in options) and options['lost_newline'] in truths
    spaceBeforeNewline = ('space_before_newline' in options) and options['space_before_newline'] in truths
    englishWordsMismatch = ('english_words_mismatch' in options) and options['english_words_mismatch'] in truths

    allowedCharacters = set()
    if 'allowed_characters_file' in options:
        allowedCharactersFile = options['allowed_characters_file']
        if os.path.isfile(allowedCharactersFile):
            print(f"Read allowed characters: {allowedCharactersFile}")
            allowedCharacters = ReadCodepointCharactersSet(allowedCharactersFile)
    
    for key, value in originalIni.getItems():
        translateValue = translationIni.getKeyValue(key)
        if translateValue != None:
            if (len(translateValue) == 0) and (len(value) > 0):
                print(f"Error: empty translation - {key}")
                input()
                continue
            if len(allowedCharacters) > 0:
                invalidCharacters = set()
                for translateChar in translateValue:
                    if (translateChar not in allowedCharacters) and (translateChar not in value):
                       invalidCharacters.add(translateChar)
                if len(invalidCharacters) > 0:
                    print(f"Error: invalid characters in - {key}")
                    print(f"Characters: {invalidCharacters}")
                    input('')
            origUnnamedFormats = LocalizationIni.GetUnnamedFormats(value)
            translateUnnamedFormats = LocalizationIni.GetUnnamedFormats(translateValue)
            if origUnnamedFormats != translateUnnamedFormats:
                print(f"Error: unnamed format seq change - {key}")
                print("Format original : ", origUnnamedFormats)
                print("Format translate : ", translateUnnamedFormats)
                input('')
            origNamedFormats = LocalizationIni.GetNamedFormats(value)
            translateNamedFormats = LocalizationIni.GetNamedFormats(translateValue)
            if origNamedFormats != translateNamedFormats:
                print(f"Error: named format seq change - {key}")
                print("Format original : ", origNamedFormats)
                print("Format translate : ", translateNamedFormats)
                input('')
            if lostNewline:
                count = len(lostNewlineExpr.findall(translateValue))
                if count > 0:
                    input(f"Note: lost newline \\n [{count}] - {key}")
            if spaceBeforeNewline:
                count = len(spaceBeforeNewlineExpr.findall(translateValue))
                if count > 0:
                    input(f"Note: space before \\n [{count}] - {key}")
            if englishWordsMismatch:
                translateCleanValue = LocalizationIni.GetCleanText(translateValue, translateUnnamedFormats, translateNamedFormats)
                translateEngWords = LocalizationIni.GetEnglishWords(translateCleanValue)
                if len(translateEngWords) > 0:
                    cleanValue = LocalizationIni.GetCleanText(value, origUnnamedFormats, origNamedFormats)
                    origEngWords = LocalizationIni.GetEnglishWords(cleanValue)
                    if not translateEngWords.issubset(origEngWords):
                        print(f"Note: use undefined word in - {key}")
                        print("English words original : ", origEngWords)
                        print("English words translate : ", translateEngWords)
                        print("English words diff : ", translateEngWords.difference(origEngWords))
                        input('')

