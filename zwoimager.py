import time
import zwoasi as asi
import subprocess
import re
import datetime
import time
import os

tempDir = "/tmp"
debug = False

class SolveResult:
	def __init__(self, ra = 0, dec = 0, validSolve = False, captureTime = datetime.datetime.now()):
		self.validSolve = validSolve
		self.ra = ra
		self.dec = dec
		self.rotation = 0
		self.captureTime = captureTime

	def toString(self):
		return "RA: " + str(self.ra) + "\nDEC: " + str(self.dec) + "\nRotation: " + str(self.rotation)

def initCamera():
	asi.init("/lib/zwoasi/armv7/libASICamera2.so")
	print("Searching for cameras...")
	num_cameras = asi.get_num_cameras()
	if num_cameras == 0:
	    camType = "No cameras found"
	    exit()
	else:
		print(str(num_cameras) + " camera(s) found")
		camera_id = 0

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


def zwoCapture(expTime,gain):  
    captureFile = "/tmp/" + time.strftime("%Y%m%d-%H%M%S") + "-capture.jpg"
    if (debug):
    	print("Capturing " + captureFile)
    camera.set_control_value(asi.ASI_GAIN, gain * 5)
    camera.set_control_value(asi.ASI_EXPOSURE, expTime * 1000)# microseconds    
    camera.capture(filename=captureFile)
    return captureFile

def solveImage(captureFile):

	limitOptions = 		["--no-plots","--overwrite","--skip-solved","--cpulimit","7"]
	optimizedOptions = 	["--downsample","4","--cpulimit","10","--no-remove-lines","--uniformize","0"]
	scaleOptions = 		["--scale-units","arcsecperpix","--scale-low","14.85","--scale-high","15.85"]
	fileOptions = 		["--dir",tempDir,"--new-fits","none","--solved","none","--match","none","--wcs","none","--corr","none","--rdls","none","--wcs","none","--temp-axy"]

	cmd = ["/usr/bin/solve-field"]
	options = limitOptions + optimizedOptions + scaleOptions + fileOptions + [captureFile]
	if (debug):
		print("Executing:")
		print(cmd + options)
	result = subprocess.run(cmd + options, cwd="/tmp",capture_output=True, text=True)

	if (debug):
		print(result.stdout)
		print(result.stderr)

	# All files were either specified not to be created. The only one that seems to be forced is the %sindx.xyls file. Clean it up now
	xylsFile = tempDir + "/" + os.path.splitext(os.path.basename(captureFile))[0] + "-indx.xyls"
	if os.path.exists(xylsFile):
		if (debug):
			print("Cleaning up " + xylsFile)	
		os.remove(xylsFile)

	return parseSolvedOutput(result.stdout)

def parseSolvedOutput(result):
	#success:
	# Field center: (RA,Dec) = (165.113684, 33.228524) deg.
	# Field size: 5.46861 x 4.10503 degrees
	# Field rotation angle: up is -37.1309 degrees E of N

	solveResult = SolveResult(validSolve = False)

	if ("Did not solve" in result):
		return solveResult

	solveResult.validSolve = True

	lines = result.split('\n')
	for line in lines:
  		if (line.startswith("Field center: (RA,Dec)")):
  			label,radecstr = line.split('=')
  			ra, dec = re.findall("[-,+]?\d+\.\d+",radecstr)
  			solveResult.ra = ra
  			solveResult.dec = dec
  		if (line.startswith("Field rotation angle:")):
  			label,rotation = line.split(':')
  			[rotdegrees] = re.findall("[-,+]?\d+\.\d+",rotation)
  			solveResult.rotation = rotdegrees
	return solveResult

initCamera()

expTime = 150 # ms
gain = 9
while(True):
	t0 = time.time()
	captureFile = zwoCapture(expTime,gain)
	t1 = time.time()
	print("Capture time: " + str(t1-t0))
	#captureFile = "/home/pi/astrometry_test/example.jpg"
	solveResult = solveImage(captureFile)
	print(solveResult.toString())
	t2 = time.time()
	print("Solve time:   " + str(t2-t1))
	print("Total time:   " + str(t2-t0))

	if os.path.exists(captureFile):
		os.remove(captureFile)

	print()
