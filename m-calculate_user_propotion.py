import xml.etree.ElementTree as ET

filename = 'test_file.xliff'
userattrib = '{SmartcatXliff}last-modified-user'

doc_tree = ET.parse(filename)

unit_root = doc_tree.getroot()[0][1]

res_dict = {}

for tunit in unit_root.findall('{urn:oasis:names:tc:xliff:document:1.2}trans-unit'):
    if userattrib in tunit.attrib.keys():
        if tunit.attrib[userattrib] not in res_dict.keys():
            res_dict[tunit.attrib[userattrib]] = []
        else:
            res_dict[tunit.attrib[userattrib]].append(tunit.attrib['id'])

total_num = 0
for user in res_dict:
    total_num += len(res_dict[user])
for user in res_dict:
    print(f"{user:35}: {len(res_dict[user]):5}({len(res_dict[user])*100/total_num:4.1f}%)")