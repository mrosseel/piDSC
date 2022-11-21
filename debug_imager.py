import time
import logging
from shutil import copyfile
from imager import Imager
from pathlib import Path

class DebugImager(Imager):
    def __init__(self, tempDir = "/tmp"):
        self.testimage = "m13.jpg"
        self.tempdir = tempDir
        pass

    def capture(self, exptime, gain):  
        # capturefile = self.tempdir + "/" + time.strftime("%y%m%d-%h%m%s") + "-capture.jpg"
        capturefile = Path(self.tempdir, "capture.jpg")
        logging.info(f"Capturing fake image {capturefile}")
        copyfile(self.testimage, capturefile)
        return capturefile




