import xml.etree.ElementTree as ET
import sys
import os
import pickle
import export_smartcat

def load_data():
    try:
        with open('translator_statics.pkl', 'rb') as f:
            return pickle.load(f)
    except:
        return {}

def search_xliff():
    res = []
    for file in os.listdir(os.getcwd()):
        if file.endswith(".xliff"):
            res.append(['PH',file])
    return res
    #[['PH','global_ini_pull.xliff'],['PH','global_lines_pull.xliff']]

def calc_propotion():   #TODO: 변화값 계산하기
    userattrib = '{SmartcatXliff}last-modified-user'
    docs = search_xliff()
    for doc in docs:
        doc_tree = ET.parse(doc[1])
        unit_root = doc_tree.getroot()[0][1]

        res_dict = {}
        data_dict = load_data()

        for tunit in unit_root.findall('{urn:oasis:names:tc:xliff:document:1.2}trans-unit'):
            if userattrib in tunit.attrib.keys():
                data_dict[tunit.attrib['id']] = tunit.attrib[userattrib]

    for id in data_dict:
        if id == 'res': continue
        if data_dict[id] not in res_dict.keys():
            res_dict[data_dict[id]] =  0
        else:
            res_dict[data_dict[id]] += 1

    total_num = sum(res_dict.values())
    for user in res_dict:
        print(f"{user:35}: {res_dict[user]:5}({res_dict[user]*100/total_num:4.1f}%)")

    data_dict['res'] = res_dict
    with open('translator_statics.pkl', 'wb') as f:
        pickle.dump(data_dict, f)


def main(args):
    config_title = "sc_ko_m"
    #docs = export_smartcat.main(["pullfs", config_title,"xliff"])  # [[doc id,이름],...]
    #calc_propotion(docs)
    #MEMO: currently downloading xliff via API masks user name. useless.

    calc_propotion()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
