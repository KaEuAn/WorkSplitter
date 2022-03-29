import qrcode
from PIL import Image
import cv2 as cv


def fullname_convert(name):
    return name.replace(' ', '_')

class QRCodeMaker:
    
    anonymousCount = 0

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value):
        if type(value) is tuple:
            self._filename = "{}_{}".format(value[1], fullname_convert(value[0]))
        else:
            self._filename = "anonymous_{}".format(QRCodeMaker.anonymousCount)
            QRCodeMaker.anonymousCount += 1

    
    def __init__(self, errorCorrect=qrcode.ERROR_CORRECT_H):
        self._QRCode = qrcode.QRCode(error_correction=errorCorrect)
        self.filename = None
            
    def make(self):
        self._QRCode.add_data(self._filename)
        self._QRCodeImage = self._QRCode.make_image()
        self._QRCode.clear()
        return self._QRCodeImage

    def add_anonymous(self):
        self.filename = None

class QRCodeReader:

    def __init__(self):
        pass

