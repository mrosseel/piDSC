import os
import time
from zwoImager import ZWOImager
from plateSolver import PlateSolver
from solveResult import SolveResult

tempDir = "/tmp"
debug = True

testImage = "/home/pi/astrometry_test/example.jpg" # full file name or None

camera = ZWOImager(tempDir)
plateSolver = PlateSolver(tempDir)

expTime = 150 # ms
gain = 95
while(True):
	if (debug):
		t0 = time.time()

	captureFile = camera.capture(expTime,gain)

	if (debug):
		t1 = time.time()
		print("Capture time: " + str(t1-t0))

	cf = captureFile if testImage is None else testImage
	solveResult = plateSolver.solveImage(cf)

	if (debug):
		print(solveResult.toString())
		t2 = time.time()

	if (debug):
		print("Solve time:   " + str(t2-t1))
		print("Total time:   " + str(t2-t0))

	# cleanup our captured image
	if os.path.exists(captureFile):
		os.remove(captureFile)


	if (debug):
		print()