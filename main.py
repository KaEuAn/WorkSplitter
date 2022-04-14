import qrcode
from PIL import Image
import cv2 as cv
from collections import defaultdict
from reportlab.pdfgen import canvas
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
    
    def __init__(self, errorCorrect=qrcode.ERROR_CORRECT_H, cls=None, filename="temp/QRcode.png", size=(100, 100)):
        self._QRCode = qrcode.QRCode(error_correction=errorCorrect)
        self.ID = 0
        self.size = size
        self.cls = cls
        self._QRCodeImage = None
        self.tempQRCodeFilename = filename

    def make(self):
        self._QRCode.add_data(self._str)
        self._QRCodeImage = self._QRCode.make_image()
        self._QRCode.clear()
        self._QRCodeImage = self._QRCodeImage.resize(self.size)
        self._QRCodeImage.save(self.tempQRCodeFilename)
        self.ID += 1
        self.update()
        return self._QRCodeImage

class WordHeaderChanger:

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
        doc.add_picture(self.QRMaker.tempQRCodeFilename, width=Cm(3))
    
    def add_doc(self, doc):
        doc.save(self.output_filename.format(self.docs_count))
        self.docs_count += 1

    def add_work(self, cls):
        self.QRMaker.cls = cls
        curID = self.QRMaker.ID
        QRImage = self.QRMaker.make()
        self.update_doc(self.docsByCls[cls], curID)
        self.add_doc(self.docsByCls[cls])


class PdfHeaderChanger:
    def __init__(self, desc_filename, output_filename="output/{}.pdf", max_count=100):
        self.docs_count = 0
        self.page_count = 0
        self.max_count = max_count
        self.output_filename = output_filename
        self.outputPdf = None
        self.QRMaker = QRCodeMaker()
        with open(desc_filename, 'r') as desc_file:
            self.docsByCls = json.load(desc_file)
        self.newOutputDocument()

    def newOutputDocument(self):
        if self.outputPdf:
            with open(self.output_filename.format(self.docs_count), "wb") as out:
                self.outputPdf.write(out)
        
        self.outputPdf = PdfFileWriter()
        self.docs_count += 1


    def make_pdf2merge(self):
        newPdf = canvas.Canvas('temp/pdf2merge.pdf')
        newPdf.drawImage(self.QRMaker.tempQRCodeFilename, 490, 740)
        newPdf.drawString(65, 810,"{}".format(self.curID))
        newPdf.save()

    def make_title2merge(self, cls):
        newPdf = canvas.Canvas('temp/pdf2merge.pdf')
        newPdf.drawImage(self.QRMaker.tempQRCodeFilename, 500, 750)
        newPdf.drawString(15, 720,"{}".format(self.curID))
        newPdf.drawString(350, 720,"{}".format(cls))
        newPdf.save()

    def add_work(self, cls):
        self.QRMaker.cls = cls
        self.curID = self.QRMaker.ID
        QRImage = self.QRMaker.make()
        self.make_pdf2merge()

        for filename in self.docsByCls[cls]:
            print(filename)
            task_stream = open(filename, 'rb')
            qrcode_stream = open('temp/pdf2merge.pdf', 'rb')
            taskPdf = PdfFileReader(task_stream)
            qrcodePdf = PdfFileReader(qrcode_stream)
            page_count = taskPdf.getNumPages()
            for page_num in range(page_count):
                curPage = taskPdf.getPage(page_num)
                curPage.mergePage(qrcodePdf.getPage(0))
                self.outputPdf.addPage(curPage)
                self.page_count += 1

        if self.page_count > self.max_count:
            self.newOutputDocument()
    
    def finish(self):
        self.newOutputDocument()


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
    pdf_ch = PdfHeaderChanger("cls_files.json")
    pdf_ch.add_work("5")
    pdf_ch.finish()