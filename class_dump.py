import json

def class_dump(clsDict, output_filename="cls_files.json"):
    with open(output_filename, "w") as fr:
        json.dump(clsDict, fr)

if __name__ == "__main__":
    clsDict = {"5": "11.docx"}
    class_dump(clsDict)