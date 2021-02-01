#!/usr/bin/python

# Export and download translation file from smartCAT.
# Please make sure before use script you're created
# configuation file for script. See example below.
#
# Example (smartcat.ini):
# [config_name]
# accountId = 
# authKey =
# documentId = 
# languageId = 

import sys
import time
import configparser
from smartcat import *

class smartCatConfig:
    @staticmethod
    def __ReadConfigKey(config, key_name):
        if not key_name in config:
            raise Exception(f"Missing key '{key_name}' in smartCAT config")
        key_value = config[key_name].strip()
        if len(key_value) == 0:
            raise Exception(f"Empty key '{key_name}' value in smartCAT config")
        return key_value

    @staticmethod
    def __ReadConfigKeyPair(config, key_name):
        key_value = smartCatConfig.__ReadConfigKey(config, key_name)
        return [x.strip() for x in key_value.split(',', 1)]

    def __init__(self, config):
        self.accountId = smartCatConfig.__ReadConfigKey(config, 'accountId')
        self.authKey = smartCatConfig.__ReadConfigKey(config, 'authKey')
        self.documentIds = []
        documentIndex = 1
        while f'documentId_{documentIndex}' in config:
            self.documentIds.append(smartCatConfig.__ReadConfigKeyPair(config, f'documentId_{documentIndex}'))
            documentIndex = documentIndex + 1
        self.languageId = smartCatConfig.__ReadConfigKey(config, 'languageId')

    def printDocumentIds(self):
        print('Available export files ids:')
        documentIndex = 1
        for documentPair in self.documentIds:
            print(f"{documentIndex} - {documentPair[1]}")
            documentIndex = documentIndex + 1

    def readDocumentIds(self,mode):
        if len(self.documentIds) > 1:
            self.printDocumentIds()
            if mode!='pullfs':  ids = set(map(int, filter(None, input("Enter export ids (optional): ").split(' '))))
            else: ids=''
            if len(ids) == 0:
                return set(range(1, len(self.documentIds) + 1))
            return [id for id in ids if id > 0 and id <= len(self.documentIds)];
        return set(range(1, len(self.documentIds) + 1))


def export_multilang_csv(document_resource, document_id, output_file_name):
    print(f'Export document: {output_file_name}')
    with document_resource.request_export(document_ids=document_id, target_type='multilang_Csv') as export_result:
        if export_result.status_code != 200:
            print('Error: Failed request status code - ', export_result.status_code)
            return 1
        print('Export started')
        export_json = json.loads(export_result.text)
        export_task_id = export_json['id']
        wait_download_ready = False
        try:
            while True:
                with document_resource.download_export_result(export_task_id) as download_result:
                    if download_result.status_code == 200:
                        if wait_download_ready:
                            print('')
                        wait_download_ready = False
                        print('Download started')
                        with open(output_file_name, 'wb') as out_file:
                            for chunk in download_result.iter_content(chunk_size=8192):
                                out_file.write(chunk)
                        print('Download completed')
                        break
                    elif download_result.status_code == 204:
                        if wait_download_ready:
                            print('.', end='')
                        else:
                            print('Wait download ready', end='')
                            wait_download_ready = True
                        time.sleep(1)
                    else:
                        if wait_download_ready:
                            print('')
                        print('Error: export status code - ', download_result.status_code)
                        return 1
        except:
            if wait_download_ready:
                print('')
            raise
        print('Export completed')
        return 0

def export_target(document_resource, document_id, output_file_name):
    print(f'Export document: {output_file_name}')
    with document_resource.request_export(document_ids=document_id, target_type='target') as export_result:
        if export_result.status_code != 200:
            print('Error: Failed request status code - ', export_result.status_code)
            return 1
        print('Export started')
        export_json = json.loads(export_result.text)
        export_task_id = export_json['id']
        wait_download_ready = False
        try:
            while True:
                with document_resource.download_export_result(export_task_id) as download_result:
                    if download_result.status_code == 200:
                        if wait_download_ready:
                            print('')
                        wait_download_ready = False
                        print('Download started')
                        with open(output_file_name+'.xlsx', 'wb') as out_file:
                            for chunk in download_result.iter_content(chunk_size=8192):
                                out_file.write(chunk)
                        print('Download completed')
                        break
                    elif download_result.status_code == 204:
                        if wait_download_ready:
                            print('.', end='')
                        else:
                            print('Wait download ready', end='')
                            wait_download_ready = True
                        time.sleep(1)
                    else:
                        if wait_download_ready:
                            print('')
                        print('Error: export status code - ', download_result.status_code)
                        return 1
        except:
            if wait_download_ready:
                print('')
            raise
        print('Export completed')
        return 0

def main(args):
    result = 1
    config_name = ''
    if len(args) > 1:
        config_name = args[1]
    try:
        config = configparser.ConfigParser()
        if not config.read('smartcat.ini'):
            print('Error: Missing config file - smartcat.ini')
            return 1
        if len(config.sections()) == 0:
            print('Error: No sections in smartCAT config')
            return 1
        print('Available smartCAT config - ', ', '.join(str(e) for e in config.sections()))
        if len(config_name) == 0:
            config_name = input("Enter smartCAT config name: ").strip()
            while not config.has_section(config_name):
                if len(config_name) > 0:
                    print("Unknown smartCAT config name - ", config_name)
                config_name = input("Enter smartCAT config name: ").strip()
        elif not config.has_section(config_name):
            print("Unknown smartCAT config name - ", config_name)
            return 1
        print("Use smartCAT config name - ", config_name)
        smartCAT_config = smartCatConfig(config[config_name])
        exportDocumentIds = smartCAT_config.readDocumentIds(args[0])
        api = SmartCAT(smartCAT_config.accountId, smartCAT_config.authKey, SmartCAT.SERVER_EUROPE)
        for id in exportDocumentIds:
            documentInfo = smartCAT_config.documentIds[id - 1]
            document_id = documentInfo[0] + '_' + smartCAT_config.languageId
            result = export_target(api.document, document_id, documentInfo[1])
    except Exception as err:
        print('Error: Failed export: {0}'.format(err))
    except KeyboardInterrupt as err:
        print('Interrupted')
    if result == 0:
        print('Done')
    if args[0] == 'pullfs': return smartCAT_config.documentIds
    else: return result

if __name__ == "__main__":
    sys.exit(main(sys.argv))
