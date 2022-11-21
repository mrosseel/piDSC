import os
import time
import threading
from zwoImager import ZWOImager
from plateSolver import PlateSolver
from solveResult import SolveResult
from lx200Server import LX200Server
from skyFiAutoDetect import skyFiAutoDetect
import logging
import argparse
from debug_imager import DebugImager


#### Config

# temp dir for writing any files
# note that for highest speed, setup your fstab so that /tmp is all in RAM. Example entry: 
#       tmpfs /tmp tmpfs defaults,noatime,nosuid 0 0
tempDir = "/dev/shm/images"

# Autodetect name used by SkySafari
skyFiName = "pidsc"

# port used by LX200 server. 4030 is standard
lx200Port = 4030

# the exposure time and gain for our camera
exptime = 150 # ms
gain = 95

# create a default position until we get an initial fix
polarisPosition = SolveResult(validSolve = True);
polarisPosition.ra_hms = "02:59:31.82"
polarisPosition.dec_dms = "+89:21:26.1"

global currentPosition
currentPosition = polarisPosition

# create a lock to use when updating the position from with a thread
positionUpdateLock = threading.Lock()

# method used by our LX200 server to get the current ra/dec, as a tuple
def getCurrentRADEC():
	# use the lock
	with positionUpdateLock:
		pos = [currentPosition.lx200ra(), currentPosition.lx200dec()]
	return pos


def main(fakecamera, debug):
    t0,t1,t2 = 0,0,0
    camera = ZWOImager(tempDir) if not fakecamera else DebugImager(tempDir)

    # instantiate the camera and platesolver
    # plateSolver = PlateSolver(astrometry_cmd='/usr/local/astrometry/bin/solve-field', tempDir=tempDir)
    plateSolver = PlateSolver(astrometry_cmd='/dev/shm/astrometry/bin/solve-field', tempDir=tempDir)

    # instantiate the lx200Server, passing in the method to get the current ra/dec
    lx200Server = LX200Server(getCurrentRADEC, '',lx200Port)
    # and start it on its own thread
    lx200Thread = threading.Thread(target=lx200Server.listen)
    lx200Thread.start()

    # instantiate and start the skyFi auto detect thread
    ssad = skyFiAutoDetect()
    ssadThread = threading.Thread(target=ssad.listenForSkyFiAutoDetect, args=(skyFiName,))
    ssadThread.start()

    # main loop
    while(True):

        if (debug):
            t0 = time.time()

        # capture the image
        captureFile = camera.capture(exptime,gain)

        if (debug):
            t1 = time.time()
            logging.debug("Capture time: " + str(t1-t0))

        # solve for the result
        solveResult = plateSolver.solveImage(captureFile)
        logging.debug(f"Solve result = {solveResult.toString()}")

        if (debug):
            # logging.debug(solveResult.toString())
            t2 = time.time()

        if (solveResult.validSolve and solveResult.ra_deg != 0): 
            print("New position")
            # update the current position with the solve result
            with positionUpdateLock:
                currentPosition = solveResult
        

        if (debug):
            logging.debug("Solve time:   " + str(t2-t1))
            logging.debug("Capture + solve time:   " + str(t2-t0))

        # cleanup our captured image
        if os.path.exists(captureFile):
            os.remove(captureFile)

        if (debug):
            print()


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logging.basicConfig(format="%(asctime)s %(name)s: %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="piDSC push-to")
    parser.add_argument(
        "-fc", "--fakecamera", help="Use a fake camera", default=False, action='store_true', required=False)
    parser.add_argument(
        "-x", "--verbose", help="Set logging to debug mode", action="store_true"
    )
    args = parser.parse_args()
    # add the handlers to the logger
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    main(args.fakecamera, args.verbose)

