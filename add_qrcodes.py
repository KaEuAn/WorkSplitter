import argparse
import main
import class_dump
from tqdm import tqdm
import os

def logical_xor(a, b):
    return (a and not b) or (not a and b)

parser = argparse.ArgumentParser(description='Adding QRCodes and ID to the tasks for students')
parser.add_argument('--output-path', '--output', '-o', type=str, default='output',
                    help='destination path for the generated pdf-files')
parser.add_argument('--input-path', '--input', '-i',  type=str, default=None,
                    help='path containing pdf files with tasks in format yyyy_1_x, where x is a single-digit class number. If path is not provided, the info about files is taken from file "cls_files.json"')
parser.add_argument('--cls', '-c', type=str)
parser.add_argument('--number', '-n', type=int, default=1)
parser.add_argument('--start-student-id', '-s', type=int, default=1000)
parser.add_argument('--start-file-id', type=int, default=1)
parser.add_argument('--starting-page', type=int, default=200)
parser.add_argument('--page-count', '-p', type=int, default=None)



args = parser.parse_args()

if args.input_path is not None and args.starting_page is not None:
    raise RuntimeError('Conflicting arguments to the programm')
if args.page_count == 0:
    raise RuntimeError('Page count is equal to zero')
if logical_xor(args.page_count is None, args.starting_page is None):
    raise RuntimeError('Page count and starting page should be defined only together')

if not os.path.isdir(args.output_path):
    os.mkdir(args.output_path)

if args.page_count:
    phc = main.PdfHeaderChanger(None, output_path=args.output_path, startingStudentId=args.start_student_id, startingDocsId=args.start_file_id)
    for i in tqdm(range(args.number)):
        phc.add_empty_QR_Id(args.cls, args.page_count, custom_page_number=args.starting_page)
    phc.finish()
    exit()

if args.input_path:
    if not os.path.isdir(args.input_path):
        raise RuntimeError('input folder does not exsist')
    class_dump.class_dump(input_path=args.input_path)

phc = main.PdfHeaderChanger('cls_files.json', output_path=args.output_path, startingStudentId=args.start_student_id, startingDocsId=args.start_file_id)
for i in tqdm(range(args.number)):
    phc.add_work(args.cls)
phc.finish()