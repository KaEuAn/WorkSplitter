from PyPDF2 import PdfFileReader, PdfFileWriter
import argparse
import os
from tqdm import tqdm

def split_pdf(input_filedir, output_dir, input_filename):
    with open(input_filedir, 'rb') as input_stream:
        reader = PdfFileReader(input_stream)
        page_count = reader.getNumPages()
        for page in range(page_count):
            output_file = os.path.join(output_dir, input_filename + str(page) + ".pdf")
            with open(output_file, 'wb') as output_stream:
                writer = PdfFileWriter()
                writer.addPage(reader.getPage(page))
                writer.write(output_stream)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Adding QRCodes and ID to the tasks for students')
    parser.add_argument('--output-path', '--output', '-o', type=str, default='output_onepagers',
                        help='destination path for the generated pdf-files')
    parser.add_argument('--input-path', '--input', '-i',  type=str, default=None,
                        help='path containing pdf files with scanned tasks. You can use blacklist folder as an input folder for ')
    

    args = parser.parse_args()

    if not os.path.isdir(args.output_path):
        os.mkdir(args.output_path)

    
    if args.input_path:
        for path in tqdm(os.listdir(args.input_path)):
            file = os.path.join(args.input_path, path)
            split_pdf(file, args.output_path, path)