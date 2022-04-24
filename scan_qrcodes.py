import argparse
import main
import class_dump
from tqdm import tqdm
import os
from pympler.tracker import SummaryTracker
tracker = SummaryTracker()

def logical_xor(a, b):
    return (a and not b) or (not a and b)

parser = argparse.ArgumentParser(description='Adding QRCodes and ID to the tasks for students')
parser.add_argument('--output-path', '--output', '-o', type=str, default='output',
                    help='destination path for the generated pdf-files')
parser.add_argument('--input-path', '--input', '-i',  type=str, default=None,
                    help='path containing pdf files with scanned tasks')
parser.add_argument('--save-logs', '-s', type=str, default=None)
parser.add_argument('--load-logs', '-l', type=str, default=None)



args = parser.parse_args()

if args.input_path is None and args.load_logs:
    raise RuntimeError('No input folder or load file were provided')

if not os.path.isdir(args.output_path):
    os.mkdir(args.output_path)

scanner = main.QRCodeScanner(args.output_path, save=args.save_logs, load=args.load_logs)
#renaming files to index.pdf
'''for i, path in enumerate(tqdm(os.listdir(args.input_path))):
    file = os.path.join(args.input_path, path)
    if os.path.isfile(file):
        os.rename(file, os.path.join(args.input_path, '{}.pdf'.format(i)))'''
for path in tqdm(os.listdir(args.input_path)):
    tracker.print_diff()
    file = os.path.join(args.input_path, path)
    if os.path.isfile(file):
        scanner.scanPdf(file)
        
scanner.collectWorks()