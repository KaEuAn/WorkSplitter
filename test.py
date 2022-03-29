from main import QRCodeMaker
from PIL import ImageChops
import unittest

class TestFunctionality(unittest.TestCase):

    def assertNotEqualImages(self, img1, img2):
        self.assertTrue(ImageChops.difference(img1, img2).getbbox())

    def assertEqualImages(self, img1, img2):
        self.assertFalse(ImageChops.difference(img1, img2).getbbox())

    def test_images_equal(self):
        qrm = QRCodeMaker()
        img1 = qrm.make()
        img1v2 = qrm.make()
        qrm.filename = None
        img2 = qrm.make()
        qrm.filename = ("Andrei YYY", 7)
        img3 = qrm.make()
        self.assertEqualImages(img1, img1v2)
        self.assertNotEqualImages(img1, img2)
        self.assertNotEqualImages(img3, img2)
        self.assertNotEqualImages(img1, img3)


    def test_add_anonymous(self):
        cntChecks = 10
        startedAnonymousCount = QRCodeMaker.anonymousCount
        qrm = QRCodeMaker()
        answers1 = []
        for i in range(cntChecks):
            answers1.append(qrm.make())
            qrm.filename = None
        
        QRCodeMaker.anonymousCount = startedAnonymousCount
        qrm = QRCodeMaker()
        for i, val in enumerate(answers1):
            self.assertEqualImages(qrm.make(), val)
            qrm.add_anonymous()
        


if __name__ == '__main__':
    unittest.main()