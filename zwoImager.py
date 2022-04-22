import time
import datetime
import os
import zwoasi as asi


debug = False


class ZWOImager:
	def __init__(self, tempDir = "/tmp"):
		asi.init("/lib/zwoasi/armv7/libASICamera2.so")
		print("Searching for cameras...")
		num_cameras = asi.get_num_cameras()
		if num_cameras == 0:
		    camType = "No cameras found"
		    exit()
		else:
			print(str(num_cameras) + " camera(s) found")
			camera_id = 0

		self.tempDir = tempDir

		global camera
		camera = asi.Camera(camera_id)
		camera.set_control_value(asi.ASI_BANDWIDTHOVERLOAD, camera.get_controls()['BandWidth']['MinValue'])
		camera.disable_dark_subtract()
		camera.set_control_value(asi.ASI_WB_B, 99)
		camera.set_control_value(asi.ASI_WB_R, 75)
		camera.set_control_value(asi.ASI_GAMMA, 50)
		camera.set_control_value(asi.ASI_BRIGHTNESS, 50)
		camera.set_control_value(asi.ASI_FLIP, 0)
		camera.set_image_type(asi.ASI_IMG_RAW8)


	def capture(self, expTime,gain):  
	    captureFile = self.tempDir + "/" + time.strftime("%Y%m%d-%H%M%S") + "-capture.jpg"
	    if (debug):
	    	print("Capturing " + captureFile)
	    camera.set_control_value(asi.ASI_GAIN, gain * 5)
	    camera.set_control_value(asi.ASI_EXPOSURE, expTime * 1000)# microseconds    
	    camera.capture(filename=captureFile)
	    return captureFile




