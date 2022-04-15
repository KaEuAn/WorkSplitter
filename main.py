import qrcode
from PIL import Image
import cv2 as cv
from wand.image import Image as wandImage
from collections import defaultdict
from reportlab.pdfgen import canvas
from PyPDF2 import PdfFileReader, PdfFileWriter
import os, docx, json
from docx.shared import Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

def fullname_convert(name):
    return name.replace(' ', '_')

class QRCodeMaker:
    
    def __init__(self, errorCorrect=qrcode.ERROR_CORRECT_H, cls=None, size=(100, 100)):
        self._QRCode = qrcode.QRCode(error_correction=errorCorrect)
        self.size = size
        self._QRCodeImage = None
        self.tempFilenameTemplate = "temp/QRcode{}_{}.png"

    def make(self, page):
        self._QRCode.add_data("ID:{}:class:{}:page:{}".format(self.ID, self.cls, page))
        self._QRCodeImage = self._QRCode.make_image()
        self._QRCode.clear()
        self._QRCodeImage = self._QRCodeImage.resize(self.size)
        filename = self.tempFilenameTemplate.format(self.ID, page)
        self._QRCodeImage.save(filename)
        return filename

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
        doc.add_picture(self.QRMaker.tempFilenameTemplate, width=Cm(3))
    
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
    def __init__(self, desc_filename, output_filename="output/to_print{}.pdf", max_count=100, startingID=1):
        self.docs_count = 0
        self.page_count = 0
        self.workID = startingID
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
            for file in self.toClose:
                file.close()
        self.toClose = []
        self.outputPdf = PdfFileWriter()
        self.docs_count += 1
        self.page_count = 0

    def make_pdf2merge(self):
        QRfilename = self.QRMaker.make(self.page_count)
        filename = 'temp/pdf2merge{}_{}.pdf'.format(self.docs_count, self.page_count)
        newPdf = canvas.Canvas(filename)
        newPdf.setFont("Times-Roman", 12)
        newPdf.drawImage(QRfilename, 490, 740)
        newPdf.drawString(50, 816,"ID: {}".format(self.workID))
        newPdf.save()
        return filename

    def make_title2merge(self, cls):
        QRfilename = self.QRMaker.make(self.page_count)
        filename = 'temp/title2merge{}_{}.pdf'.format(self.docs_count, self.page_count)
        newPdf = canvas.Canvas(filename)
        newPdf.setFont("Times-Roman", 12)
        newPdf.drawImage(QRfilename, 500, 750)
        newPdf.drawString(15, 720,"ID: {}".format(self.workID))
        newPdf.drawString(350, 720,"{}".format(cls))
        newPdf.save()
        return filename

    def add_work(self, cls):
        self.QRMaker.cls = cls
        self.QRMaker.ID = self.workID
        for cls_filename in self.docsByCls[cls]:
            
            task_stream = open(cls_filename, 'rb')
            taskPdf = PdfFileReader(task_stream)
            self.toClose.append(task_stream)

            page_count = taskPdf.getNumPages()
            for page_num in range(page_count):
                #make QRCode
                pdf2merge_filename = self.make_pdf2merge()
                qrcode_stream = open(pdf2merge_filename, 'rb')
                qrcodePdf = PdfFileReader(qrcode_stream)
                self.toClose.append(qrcode_stream)
                # merge current page
                curPage = taskPdf.getPage(page_num)
                curPage.mergePage(qrcodePdf.getPage(0))
                self.outputPdf.addPage(curPage)
                self.page_count += 1

        self.workID += 1
        if self.page_count > self.max_count:
            self.newOutputDocument()
    
    def finish(self):
        self.newOutputDocument()


class QRCodeScanner:

    def __init__(self, black_list_path="black_list.json", works_dict_path="works_dict.json"):
        self._detector = cv.QRCodeDetector()
        self._image = None
        self._works_dict = defaultdict(list)
        self._works_dict_path = works_dict_path
        self._image_type = 'png'
        self._output_filename = "output_works/{}.pdf"
        self._black_list = []
        self._black_list_path = black_list_path

    def tryParse(self, source, pdf_filename):
        for i, image in enumerate(source.sequence):
            image_filename = 'temp/scan{}.jpeg'.format(i)
            wandImage(image).save(filename=image_filename)
            image = cv.imread(image_filename)
            qr_string, points, straight_qrcode = self._detector.detectAndDecode(image)
            print(qr_string)
            if not qr_string:
                return False
            parsed_string = qr_string.split(":")
            ID, cls, page = parsed_string[1], parsed_string[3], parsed_string[5]
            #first index is index of page to print, last one is index of page on current pdf
            self._works_dict[ID].append((page, cls, pdf_filename, i))
        return True
        
    def scanPdf(self, pdf_filename):
        for resolution in [400, 800]:
            with(wandImage(filename=pdf_filename, resolution=resolution)) as source: 
                if self.tryParse(source, pdf_filename):
                    break
        else:
            self._black_list.append(pdf_filename)

    
    def collectWorks(self):
        for id in self._works_dict:
            self._works_dict[id].sort()

    def printWorks(self):
        for ID, list_parameters in self._works_dict.items():
            outputPdf = PdfFileWriter()
            listToClose = []
            for page, cls, pdf_filename, pdf_page in list_parameters:
                input_stream = open(pdf_filename, 'rb')
                inputPdf = PdfFileReader(input_stream)
                listToClose.append(input_stream)
                outputPdf.addPage(inputPdf.getPage(pdf_page))
            with open(self._output_filename.format(ID), 'wb') as output_steam:
                outputPdf.write(output_steam)
            for file in listToClose:
                file.close()

    def save_logs(self):
        with open(self._works_dict_path, "w") as fw:
            json.dump(self._works_dict, fw)
        with open(self._black_list_path, "w") as fw:
            json.dump(self._black_list, fw)
    
        
if __name__ == "__main__":
    pdf_ch = PdfHeaderChanger("cls_files.json")
    pdf_ch.add_work("5")
    pdf_ch.add_work("7")
    pdf_ch.add_work("8")
    pdf_ch.add_work("9")
    pdf_ch.finish()
    '''scanner = QRCodeScanner()
    scanner.scanPdf("output/to_print1.pdf")
    scanner.collectWorks()
    scanner.printWorks()'''