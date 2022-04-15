import json
from os import listdir
from os.path import isfile, join
from collections import defaultdict

def class_dump(clsDict, input_path='input', output_filename="cls_files.json"):
    pdf_files = [f for f in listdir(input_path) if isfile(join(input_path, f))]
    clsDict = defaultdict(list)
    for f in pdf_files:
        clsDict[f[7]].append(join(input_path, f))
    with open(output_filename, "w") as fr:
        json.dump(clsDict, fr)

if __name__ == "__main__":
    class_dump()