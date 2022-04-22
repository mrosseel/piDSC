import os
import time
import threading
from zwoImager import ZWOImager
from plateSolver import PlateSolver
from solveResult import SolveResult
from lx200Server import LX200Server
from skyFiAutoDetect import skyFiAutoDetect

tempDir = "/tmp"
debug = True

skyFiName = "pidsc"
lx200Port = 4030

testImage = None # "/home/pi/astrometry_test/example.jpg" # full file name or None


def getCurrentRADEC():
	return [solveResult.lx200ra(), solveResult.lx200dec()]


camera = ZWOImager(tempDir)
plateSolver = PlateSolver(tempDir)

lx200Server = LX200Server(getCurrentRADEC, '',lx200Port)
lx200Thread = threading.Thread(target=lx200Server.listen)
lx200Thread.start()

ssad = skyFiAutoDetect()
ssadThread = threading.Thread(target=ssad.listenForSkyFiAutoDetect, args=(skyFiName,))
ssadThread.start()


expTime = 150 # ms
gain = 95


while(True):
	global currentPosition

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

	if (solveResult.validSolve): 
		currentPosition = solveResult
	

	if (debug):
		print("Solve time:   " + str(t2-t1))
		print("Total time:   " + str(t2-t0))

	# cleanup our captured image
	if os.path.exists(captureFile):
		os.remove(captureFile)


	if (debug):
		print()