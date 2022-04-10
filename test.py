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
        img2 = qrm.make()
        qrm.cls = 9
        img3 = qrm.make()
        self.assertNotEqualImages(img1, img2)
        self.assertNotEqualImages(img3, img2)
        self.assertNotEqualImages(img1, img3)

 
        


if __name__ == '__main__':
    unittest.main()