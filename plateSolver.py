import os
import subprocess
import re
from solveResult import SolveResult
import logging


class PlateSolver:
# The scale is calculated from previous processed images from this camera / lens combo
# For the test ASI120mm with a 50mm f/1.4 lens, this came out to ~15.35 arcsec/pix
# thus the following low/high scale is set +/- 0.5 arcsec from there:
    def __init__(self, astrometry_cmd='/usr/local/astrometry/solve-field', tempDir = "/dev/shm/images", scalelow="14.85", scalehigh="15.85"):
        self.cmd = [astrometry_cmd]
        self.temp_dir = tempDir
        self.scale_low = scalelow
        self.scale_high = scalehigh
        limitOptions = 		(["--no-plots",		# don't generate plots - this takes a ton of time
                             "--overwrite", 	# overwrite any existing files
                             "--skip-solved", 	# skip any files we've already solved
                             "--cpulimit","5"	# limit to 7 seconds(!). We use a fast timeout here because this code is supposed to be fast
                             ]) 
        optimizedOptions = 	(["--downsample","4",	# downsample 4x. 2 = faster by about 1.0 second; 4 = faster by 1.3 seconds
                              "--no-remove-lines",	# Saves ~1.25 sec. Don't bother trying to remove spurious lines from the image
                              "--uniformize","0",	# Saves ~1.25 sec. Just process the image as-is
                              "-d", "20,30,40" # only look at the 20 brightest stars in the image
                             ])
        scaleOptions = 		(["--scale-units","arcsecperpix",	# next two params are in arcsecs. Supplying this saves ~0.5 sec
                              "--scale-low",self.scale_low,			# See config above
                              "--scale-high",self.scale_high			# See config above
                              ])
        fileOptions = 		(["--dir",self.temp_dir,	# for any files created, put them in the temp dir
                              "-m", self.temp_dir,
                              "--new-fits","none",	# Don't create a new fits
                              "--solved","none",	# Don't generate the solved output
                              "--match","none",		# Don't generate matched output
                              "--wcs","none",		# Don't generate wcs files
                              "--corr","none",		# Don't generate .corr files
                              "--rdls","none",		# Don't generate the point list
                              "--wcs","none",		# Don't generate wcs
                              "--temp-axy"			# We can't specify not to create the axy list, but we can write it to /tmp
                              ])
        options = limitOptions + optimizedOptions + scaleOptions + fileOptions
        self.cmd = self.cmd + options

    def solveImage(self, captureFile):

        cmd = self.cmd + [captureFile]

        logging.debug(f"Executing: {cmd}")

        # Note that the result of this command is sent to STDOUT
        result = subprocess.run(cmd, cwd=self.temp_dir,capture_output=True, shell=False, text=True)

        logging.debug(result.stdout)
        logging.debug(result.stderr)

        # All files were either specified not to be created. The only one that seems to be forced is the %sindx.xyls file. Clean it up now
        xylsFile = self.temp_dir + "/" + os.path.splitext(os.path.basename(captureFile))[0] + "-indx.xyls"
        if os.path.exists(xylsFile):
            logging.debug("Cleaning up " + xylsFile)	
            os.remove(xylsFile)
             
        # parse the results of STDOUT
        return self.__parseSolvedOutput(result.stdout)

    def __parseSolvedOutput(self, result):
        #success:
        # Field center: (RA,Dec) = (165.113684, 33.228524) deg.
        # Field center: (RA H:M:S, Dec D:M:S) = (11:00:27.284, +33:13:42.686).
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
                solveResult.ra_deg = ra
                solveResult.dec_deg = dec
            if (line.startswith("Field center: (RA H:M:S, Dec D:M:S)")):
                label,radecstr = line.split('=')
                radecstr = radecstr.replace(').','')
                radecstr = radecstr.replace('(','')
                ra, dec = radecstr.split(',')
                solveResult.ra_hms = ra.strip()
                solveResult.dec_dms = dec.strip()	  			
            if (line.startswith("Field rotation angle:")):
                label,rotation = line.split(':')
                [rotdegrees] = re.findall("[-,+]?\d+\.\d+",rotation)
                solveResult.rotation = rotdegrees
        return solveResult


