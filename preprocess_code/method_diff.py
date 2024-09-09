import json
import argparse
import sys
import subprocess

import re
def is_test(file):
    #check path
    pattern = r'/test(|s)/'
    if re.search(pattern, file['before_file_path']) != None \
        or re.search(pattern, file['after_file_path']) != None:
        return True
    #check file
    pattern = r'Test'
    if re.search(pattern, file['before_file_path'].split('/')[-1]) != None \
        or re.search(pattern, file['after_file_path'].split('/')[-1]) != None:
        return True
    
def out_diff_txt(diff_text):
    flag = False
    before_list = []
    after_list = []
    lines = diff_text.split('\n')
    for line in lines[:-1]:
        if line[0:2] == '@@':
            if flag == False:
                flag = True
        elif line[0] == '\\':
            continue
        elif flag:
            if line[0] == '-':
                before_list.append(line[1:])
            elif line[0] == '+':
                after_list.append(line[1:])
            else:
                before_list.append(line[1:])
                after_list.append(line[1:])
        
    return ' '.join(before_list), ' '.join(after_list)

def out_txt2file(filename, text):
    with open(filename, 'w', encoding='utf-8', errors='ignore') as f:
        f.write(text)
    
    
def diff_method(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, text=True)
    before_txt, after_txt = out_diff_txt(result.stdout)
    return before_txt, after_txt

def main(params):
    commit_list = []
    command = "diff -B -w -u before.txt after.txt".split(' ')
    with open(params.json_data) as f:
        data = json.load(f)
        
    for i, commit in enumerate(data):
        print(str(i)+'/'+str(len(data)))
        if commit['codes'] == []:
            continue
        commit_dict = {}
        commit_dict['commit_id'] = commit['commit_id']
        commit_dict['timestamp'] = commit['timestamp']
        commit_dict['codes'] = []
        for file in commit['codes']:
            if is_test(file):
                continue
            file_dict = {}
            file_dict['before_file_path'] = file['before_file_path']
            file_dict['after_file_path'] = file['after_file_path']
            file_dict['ch_method_pairs'] = []
            for method in file['ch_method_pairs']:
                method_dict = {}
                out_txt2file('before.txt', method['before_content'])
                out_txt2file('after.txt', method['after_content'])
                before_txt, after_txt = diff_method(command)
                method_dict['class_name'] = method['class_name']
                method_dict['method_name'] = method['method_name']
                method_dict['before_content'] = before_txt
                method_dict['after_content'] = after_txt
                file_dict['ch_method_pairs'].append(method_dict)
            commit_dict['codes'].append(file_dict)
        if len(commit_dict['codes']) == 0:
            continue
        commit_list.append(commit_dict)
    with open(params.json_name, 'w') as f:
        json.dump(commit_list, f, indent=2)            
            
    

#引数設定
def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-json_name', type=str, default='../data/camel_ctxt.json')
    parser.add_argument('-json_data', type=str, default='../data/camel3.json')
    return parser


if __name__ == '__main__':
    params = read_args().parse_args()
    main(params)
    sys.exit(0)