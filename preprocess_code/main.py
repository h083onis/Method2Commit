import time
import sys
import json
import subprocess
from git import Repo
from gitdb.exc import BadName
import argparse
from java_parser import get_method_list
from clean_comment import remove_c_com_and_doc

#ファイルの拡張子が対象のものであるか判定
def is_auth_ext(file_path, auth_ext):
    splited_file = file_path.split('.')
    return len(splited_file) >= 2 and splited_file[-1].lower() in auth_ext

#ファイルの内容をテキストへ出力
def out_txt(repo, hexsha, filepath, type):
    output = repo.git.show(hexsha+("~1:" if type =='before' else ':')+filepath)
    output = remove_c_com_and_doc(output)
    with open(type+'.txt', 'w', encoding='utf-8', errors='ignore') as f:
        f.write(output.replace('\r\n', '\n'))


#変更されたファイルの前後の行番号を取得
def get_ch_line_num(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, text=True)
    if result.stdout == '':
        return None
    ch_line_num_list=[[],[]] #index 0 number of before  index 1 number of after
    [ch_line_num_list[0].append(tmp.split('\t')[1]) if tmp[0] == '<' \
        else ch_line_num_list[1].append(tmp.split('\t')[1]) \
            for tmp in result.stdout.split('\n')[:-1]]
    
    return ch_line_num_list

#変更された関数を返す
def get_ch_method(method_list, ch_num_line):
    ch_method_name_set = set()
    extracted_list = []
    for ch_line_num in ch_num_line:
        for i, method in enumerate(method_list):
            if i in extracted_list:
                continue
            if int(method['position'][0][0])+1 <= int(ch_line_num) \
                and int(method['position'][1][0])+1 >= int(ch_line_num):
                ch_method_name_set.add(method['class_name']+'\t'+method['method_name'])
                extracted_list.append(i)
                break
                
    return ch_method_name_set

#条件に一致するメソッドを返す
def look_up_method(class_method_name, method_list):
    for method in method_list:
        if class_method_name[0] == method['class_name'] \
            and class_method_name[1] == method['method_name']:
                return method
    return None

#変更された関数のペアの抽出
def extract_pair_ch_method(before_file_path, after_file_path, ch_num_line):
    before_method_list = get_method_list(before_file_path)
    after_method_list = get_method_list(after_file_path)
    before_ch_method_set = get_ch_method(before_method_list, ch_num_line[0])
    after_ch_method_set = get_ch_method(after_method_list, ch_num_line[1])
    ch_class_method_name_set = before_ch_method_set | after_ch_method_set
    ch_method_pairs = []
    for ch_class_method_name in ch_class_method_name_set:
        ch_method_pair = {}
        class_method_name = ch_class_method_name.split('\t')
        before_method = look_up_method(class_method_name, before_method_list)
        after_method = look_up_method(class_method_name, after_method_list)
        if before_method == None or after_method == None:
            continue
        ch_method_pair['class_name'] = class_method_name[0]
        ch_method_pair['method_name'] = class_method_name[1]
        ch_method_pair['before_content'] = before_method['content']
        ch_method_pair['after_content'] = after_method['content']
        ch_method_pair['before_ast'] = before_method['ast']
        ch_method_pair['after_ast'] = after_method['ast']
        ch_method_pairs.append(ch_method_pair)

    return ch_method_pairs
        
#コミット時の変更ファイル処理
def pipe_process(repo, commit, hexsha, params, commit_dict):
    auth_ext = params.auth_ext.split(',')
    diff = commit.diff(hexsha)
    command = "diff -B -w --old-line-format=<\t%dn\n --new-line-format=>\t%dn\n --unchanged-line-format= before.txt after.txt".split(' ')
    
    for item in diff:
        ch_type = item.change_type
        if not(is_auth_ext(item.b_path, auth_ext)) or not(ch_type == 'M' or ch_type == 'R'):
            continue
        codes_dict = {}
        out_txt(repo, hexsha, item.a_path, type='before')
        out_txt(repo, hexsha, item.b_path, type='after')
        
        codes_dict['before_file_path'] = item.a_path
        codes_dict['after_file_path'] = item.b_path
        ch_line_num = get_ch_line_num(command)
        if ch_line_num == None:
            continue
        codes_dict['ch_method_pairs'] = extract_pair_ch_method('before.txt', 'after.txt', ch_line_num)
        if len(codes_dict['ch_method_pairs']) == 0:
            continue
        commit_dict['codes'].append(codes_dict)
        

#処理の実行
def excute(params):
    commit_list = []
    repo = Repo(params.project)
    head = repo.head
    if head.is_detached:
        pointer = head.commit.hexsha
    else:
        pointer = head.reference
    commits = list(repo.iter_commits(pointer))
    commits.reverse()
    st = time.time()
    # 変更の対象ファイルをM,Rとする
    for i, item in enumerate(commits):
        print(str(i)+'/'+str(len(commits)))
        print(item.hexsha)
        commit_dict = {}
        commit_dict['commit_id'] = item.hexsha
        commit = repo.commit(item.hexsha)
        commit_dict['timestamp'] = commit.authored_date
        commit_dict['codes'] = []
        try:
            commit = repo.commit(item.hexsha+'~1')
            pipe_process(repo, commit, item.hexsha, params, commit_dict)
            commit_list.append(commit_dict)
        except BadName:
            continue
    
    with open(params.json_name, 'w') as f:
        json.dump(commit_list, f, indent=2)
    

#引数設定
def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-project', type=str, default='camel')
    parser.add_argument('-json_name', type=str, default='camel.json')
    parser.add_argument('-auth_ext', type=str, default='java')
    return parser


if __name__ == '__main__':
    params = read_args().parse_args()
    excute(params)
    sys.exit(0)