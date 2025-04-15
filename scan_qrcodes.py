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
                    help='path containing pdf files with scanned tasks. You can use blacklist folder as an input folder for ')
parser.add_argument('--save-logs', '-s', type=bool, default=False)
parser.add_argument('--load-logs', '-l', type=bool, default=False)
parser.add_argument('--check-size', type=bool, default=False)
parser.add_argument('--try-rotate', '-t', type=bool, default=False)
parser.add_argument('--resolution', '-r', type=int, default=300)
parser.add_argument('--bad-processing', '-b', type=bool, default=False)



args = parser.parse_args()



if not os.path.isdir(args.output_path):
    os.mkdir(args.output_path)

scanner = main.QRCodeScanner(args.output_path, save=args.save_logs, load=args.load_logs)
#renaming files to "{index}.pdf"
'''for i, path in enumerate(tqdm(os.listdir(args.input_path))):
    file = os.path.join(args.input_path, path)
    if os.path.isfile(file):
        os.rename(file, os.path.join(args.input_path, '{}.pdf'.format(i)))'''

if args.input_path:
    for path in tqdm(os.listdir(args.input_path)):
        file = os.path.join(args.input_path, path)
        if os.path.isfile(file):
            if not args.check_size:
                scanner.scanPdf(file, try_rotate=args.try_rotate, resolution=args.resolution, bad_processing=args.bad_processing)
scanner.collectWorks()