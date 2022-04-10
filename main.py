import qrcode
from PIL import Image
import cv2 as cv
from collections import defaultdict
from PyPDF2 import PdfFileReader, PdfFileWriter
import os, docx, json
from docx.shared import Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH


def fullname_convert(name):
    return name.replace(' ', '_')

class QRCodeMaker:

    def update(self):
        self._str = "ID:{}:class:{}".format(self.ID, self._cls)

    @property
    def cls(self):
        return self._cls

    @cls.setter
    def cls(self, value):
        self._cls = value
        self.update()
    
    def __init__(self, errorCorrect=qrcode.ERROR_CORRECT_H, cls=None, filename="temp/QRcode.png"):
        self._QRCode = qrcode.QRCode(error_correction=errorCorrect)
        self.ID = 0
        self.cls = cls
        self._QRCodeImage = None
        self.tempQRCodeFilename = filename

    def make(self):
        self._QRCode.add_data(self._str)
        self._QRCodeImage = self._QRCode.make_image()
        self._QRCode.clear()
        self._QRCodeImage.save(self.tempQRCodeFilename)
        self.ID += 1
        self.update()
        return self._QRCodeImage

class HeaderChanger:

    def __init__(self, desc_filename, output_filename="temp/output{}.docx"):
        self.docs_count = 0
        self.output_filename = output_filename
        self.QRMaker = QRCodeMaker()
        with open(desc_filename, 'r') as desc_file:
            self.docsByCls = {cls: docx.Document(filename) for cls, filename in json.load(desc_file).items()}

    def update_doc(self, doc, ID):
        for section in doc.sections:
            for paragraph in section.header.paragraphs:
                if paragraph.text[:2] == "ID":
                    paragraph.text = "ID: {}".format(ID)
        doc.add_picture(self.QRMaker.tempQRCodeFilename, width=Cm(6))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        doc.paragraphs[-1].right_indent = Cm(0)
        doc.paragraphs[-1].left_indent = Cm(0)
        doc.paragraphs[-1].space_after = Cm(0)
        doc.paragraphs[-1].space_before = Cm(0)
        doc.paragraphs[-1].text = "fjfldsjfldsjf ldsjaflkjdslf jslkfjlsjfldsjf lkdsjfsd jfldjsfls jdlakfjsafj"
    
    def add_doc(self, doc):
        doc.save(self.output_filename.format(self.docs_count))
        self.docs_count += 1

    def add_work(self, cls):
        self.QRMaker.cls = cls
        curID = self.QRMaker.ID
        QRImage = self.QRMaker.make()
        self.update_doc(self.docsByCls[cls], curID)
        self.add_doc(self.docsByCls[cls])


class QRCodeScanner:

    def __init__(self):
        self._detector = cv.QRCodeDetector()
        self._image = None
        self._works = defaultdict(list)
        self._image_type = 'png'


    def scanPdf(self, path, filename):
        pdfPath = os.path.join(path, filename)
        pdfs = convert_from_path(pdfPath, 400)
        for pdfList in pdfs:
            imagePath = os.path.join(path, filename[:-3] + self._image_type)
            image = cv.imread(imagePath)
            retval, points, straight_qrcode = self._detector.detectAndDecode(image)
            self._works[retval].append(imagePath)
    
        

if __name__ == "__main__":
    hc = HeaderChanger("cls_files.json")
    hc.add_work("5")