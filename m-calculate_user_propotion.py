# Caculate user propotion by counting editors from smartcat's exported *.xliff files
import xml.etree.ElementTree as ET
import sys
import os
import pickle
import export_smartcat

def load_data():
    '''loads previous statistics from dumped data(translator_statics.pkl file)'''
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

def parse_data():
    '''parse and counts how many segements are touched per user'''
    data_dict = {}
    userattrib = '{SmartcatXliff}last-modified-user'
    docs = search_xliff()
    for doc in docs:
        doc_tree = ET.parse(doc[1])
        unit_root = doc_tree.getroot()[0][1]

        data_dict = load_data()

        if('res' in data_dict):
            prev_res = data_dict['res']
            data_dict.pop('res')
        else:
            prev_res = {}

        for tunit in unit_root.findall('{urn:oasis:names:tc:xliff:document:1.2}trans-unit'):
            if userattrib in tunit.attrib.keys():
                data_dict[tunit.attrib['id']] = tunit.attrib[userattrib]

    return (data_dict,prev_res)

def calc_propotion(data_dict):
    '''receives data_dict to calculate actual propotion, returns as dict[user]=number of touched segment'''
    res_dict = {}
    for id in data_dict:
        if id == 'res': continue
        if data_dict[id] not in res_dict.keys():
            res_dict[data_dict[id]] =  0
        else:
            res_dict[data_dict[id]] += 1

    return res_dict


def print_propotion(res_dict, prev_dict = None):
    '''prints number of segments, propotions.'''
    total_num = sum(res_dict.values())
    if prev_dict:
        total_num_prev = sum(prev_dict.values())
    for user in res_dict:
        if prev_dict != None and user in prev_dict:
            print(f"{user:35}: {res_dict[user]:5} ({res_dict[user]-prev_dict[user]:+5}, {prev_dict[user]*100/total_num_prev:4.1f}% -> {res_dict[user]*100/total_num:4.1f}%)")
        else:
            print(f"{user:35}: {res_dict[user]:5} ({res_dict[user]:+5}, {0:4.1f}% -> {res_dict[user]*100/total_num:4.1f}%)")

def dump_data(data_dict,res_dict):
    '''dump processed data_dict and res_dict for later comparsion'''
    data_dict['res'] = res_dict
    with open('translator_statics.pkl', 'wb') as f:
        pickle.dump(data_dict, f)


def main(args):
    config_title = "sc_ko_m"
    #docs = export_smartcat.main(["pullfs", config_title,"xliff"])  # [[doc id,이름],...]
    #calc_propotion(docs)
    #MEMO: currently downloading xliff via API masks user name. useless smartcat.

    cur_primitivedata, prev_data =  parse_data()
    cur_data = calc_propotion(cur_primitivedata)
    print_propotion(cur_data,prev_data)

    dump_data(cur_primitivedata,cur_data)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
