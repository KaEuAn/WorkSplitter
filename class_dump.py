import json
from os import listdir
from os.path import isfile, join
from collections import defaultdict

def place_to_num(lst, file_pattern, place):
    for i, item in enumerate(lst):
        found = item.find(file_pattern)
        if found != -1:
            lst[i], lst[place] = lst[place], lst[i]
            return

def class_dump(input_path='input', output_filename="cls_files.json", special_sort=True):
    pdf_files = [f for f in listdir(input_path) if isfile(join(input_path, f))]
    clsDict = defaultdict(list)
    for f in pdf_files:
        #f[7] is the class number in the filename
        cls_number = f[7]
        if cls_number == '5' and 'test' in f:
            clsDict['5_test'].append(join(input_path, f))
        elif '0' <= cls_number <= '9': 
            clsDict[f[7]].append(join(input_path, f))
        else:
            clsDict['title'] = join(input_path, f)
    if special_sort:
        for cls, lst in clsDict.items():
            if cls == 'title':
                continue
            place_to_num(lst, 'mat_test', 0)
            place_to_num(lst, 'eng', 1)
            place_to_num(lst, 'rus_test', 2)
    with open(output_filename, "w") as fr:
        json.dump(clsDict, fr)

if __name__ == "__main__":
    class_dump()