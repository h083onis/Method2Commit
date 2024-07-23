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
    #class check
    if re.search(pattern, file['ch_method_pairs'][0]['class_name']) != None:
        return True