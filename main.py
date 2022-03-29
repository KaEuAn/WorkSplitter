import qrcode
from PIL import Image
import cv2 as cv

class QRCodeMaker:
    
    anonymousCount = 0
    
    def __init__(self, fullName=None, cls=None):
        if fullName is None:
            self._filename = "anonymous_{}".format(QRCodeMaker.anonymousCount)
            QRCodeMaker.anonymousCount += 1
        else:
            self._filename = "{}_{}".format(cls, fullName)
            
            
            
    def make(self, errorCorrect=qrcode.ERROR_CORRECT_H):
        QRCode = qrcode.QRCode(error_correction=errorCorrect)
        QRCode.add_data(self._filename)
        self._QRCodeImage = QRCode.make_image()
        return self._QRCodeImage

class QRCodeReader:

    def __init__(self):
        pass

