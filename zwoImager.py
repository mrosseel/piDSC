import time
import logging
import zwoasi as asi
from imager import Imager

class ZWOImager(Imager):
    def __init__(self, tempDir = "/tmp"):
        try:
            asi.init("/lib/zwoasi/armv7/libASICamera2.so")
        except:
            logging.error("Could not find ASI drivers")
            pass
        logging.info("Searching for cameras...")
        num_cameras = asi.get_num_cameras()
        if num_cameras == 0:
            logging.error("No cameras found")
            exit()
        else:
            print(str(num_cameras) + " camera(s) found")
            camera_id = 0

        self.tempDir = tempDir

        global camera

        # Perform as much of the camera init now, since this adds a fair amount of time
        camera = asi.Camera(camera_id)
        camera.set_control_value(asi.ASI_BANDWIDTHOVERLOAD, camera.get_controls()['BandWidth']['MinValue'])
        camera.disable_dark_subtract()
        camera.set_control_value(asi.ASI_WB_B, 99)
        camera.set_control_value(asi.ASI_WB_R, 75)
        camera.set_control_value(asi.ASI_GAMMA, 50)
        camera.set_control_value(asi.ASI_BRIGHTNESS, 50)
        camera.set_control_value(asi.ASI_FLIP, 0)
        camera.set_image_type(asi.ASI_IMG_RAW8)


    def capture(self, expTime, gain):  
        capturefile = self.tempdir + "/" + time.strftime("%y%m%d-%h%m%s") + "-capture.jpg"
        logging.debug("capturing " + capturefile)
        camera.set_control_value(asi.asi_gain, gain * 5)
        camera.set_control_value(asi.asi_exposure, exptime * 1000)# microseconds    
        camera.capture(filename=capturefile)
        return capturefile




