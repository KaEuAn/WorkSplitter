import qrcode
from PIL import Image
import cv2 as cv
from wand.image import Image as wandImage
from collections import defaultdict
from reportlab.pdfgen import canvas
from PyPDF2 import PdfFileReader, PdfFileWriter
import os, docx, json
from docx.shared import Cm
import shutil
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
        self._QRCode.add_data("{}:{}:{}".format(self.ID, self.cls, page))
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
    def __init__(self, desc_filename, output_path="output", max_count=100, startingDocsId=1, startingStudentId=1, double_sided_print=True):
        self.docs_count = startingDocsId - 1
        self.page_count = 0
        self.workID = startingStudentId
        self.max_count = max_count
        self.output_filename = '{}/to_print'.format(output_path) + '{}.pdf'
        self.outputPdf = None
        self.QRMaker = QRCodeMaker()
        self.ds_print = double_sided_print
        with open(desc_filename, 'r') as desc_file:
            self.docsByCls = json.load(desc_file)
        self.newOutputDocument()
        
        if not os.path.isdir('temp'):
            os.mkdir('temp')

    def newOutputDocument(self):
        if self.outputPdf:
            if self.outputPdf.getNumPages() > 0:
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
        filename = 'temp/title2merge{}_{}.pdf'.format(self.docs_count, self.page_count)
        newPdf = canvas.Canvas(filename)
        newPdf.setFont("Times-Roman", 12)
        newPdf.drawString(206, 743,"{}".format(self.workID))
        newPdf.drawString(321, 624,"{}".format(cls))
        newPdf.drawString(206, 261,"{}".format(self.workID))
        newPdf.drawString(321, 142,"{}".format(cls))
        newPdf.save()
        return filename

    def openPdfReader(self, filename):
        stream = open(filename, 'rb')
        self.toClose.append(stream)
        return PdfFileReader(stream)

    def mergeAddPages(self, pdfs, pages):
        curPage = pdfs[0].getPage(pages[0])
        for i in range(1, len(pdfs)):
            curPage.mergePage(pdfs[i].getPage(pages[i]))
        self.outputPdf.addPage(curPage)


    def add_work(self, cls):
        self.QRMaker.cls = cls
        self.QRMaker.ID = self.workID

        title_filename = self.make_title2merge(cls)
        titleText = self.openPdfReader(title_filename)
        titlePdf = self.openPdfReader(self.docsByCls['title'])

        self.mergeAddPages((titlePdf, titleText), (0, 0))
        self.outputPdf.addBlankPage()

        for cls_filename in self.docsByCls[cls]:
            
            taskPdf = self.openPdfReader(cls_filename)

            page_count = taskPdf.getNumPages()
            for page_num in range(page_count):
                #make QRCode
                pdf2merge_filename = self.make_pdf2merge()
                qrcodePdf = self.openPdfReader(pdf2merge_filename)
                # merge current page
                self.mergeAddPages((taskPdf, qrcodePdf), (page_num, 0))
                self.page_count += 1
            if self.ds_print and page_count % 2 == 1:
                self.outputPdf.addBlankPage()

        self.workID += 1
        if self.page_count > self.max_count:
            self.newOutputDocument()
    
    def finish(self):
        self.newOutputDocument()
        
        if os.path.isdir('temp'):
            try:
                shutil.rmtree('temp')
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))


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
                print("bad parse")
                return False
            student_id, cls, page = qr_string.split(":")
            #first index is index of page to print, last one is index of page on current pdf
            self._works_dict[student_id].append((page, cls, pdf_filename, i))
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
    pdf_ch.finish()
    '''pdf_ch.add_work("7")
    pdf_ch.add_work("8")
    pdf_ch.add_work("9")
    scanner = QRCodeScanner()
    scanner.scanPdf("output/to_print1.pdf")
    scanner.collectWorks()
    scanner.printWorks()'''