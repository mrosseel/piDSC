import os
import subprocess
import re
from solveResult import SolveResult


debug = False

# these should be configurable somewhere...
# The scale is calculated from previous processed images from this camera / lens combo
# For the test ASI120mm with a 50mm f/1.4 lens, this came out to ~15.35 arcsec/pix
# thus the following low/high scale is set +/- 0.5 arcsec from there:
scaleLow = "14.85"
scaleHigh = "15.85"

class PlateSolver:
	def __init__(self, tempDir = "/tmp"):
		self.tempDir = tempDir

	def solveImage(self, captureFile):

		limitOptions = 		(["--no-plots",		# don't generate plots - this takes a ton of time
							 "--overwrite", 	# overwrite any existing files
							 "--skip-solved", 	# skip any files we've already solved
							 "--cpulimit","7"	# limit to 7 seconds(!). We use a fast timeout here because this code is supposed to be fast
							 ]) 
		optimizedOptions = 	(["--downsample","4",	# downsample 4x. 2 = faster by about 1.0 second; 4 = faster by 1.3 seconds
							  "--no-remove-lines",	# Saves ~1.25 sec. Don't bother trying to remove surious lines from the image
							  "--uniformize","0"	# Saves ~1.25 sec. Just process the image as-is
							 ])
		scaleOptions = 		(["--scale-units","arcsecperpix",	# next two params are in arcsecs. Supplying this saves ~0.5 sec
							  "--scale-low",scaleLow,			# See config above
							  "--scale-high",scaleHigh			# See config above
							  ])
		fileOptions = 		(["--dir",self.tempDir,	# for any files created, put them in the temp dir
							  "--new-fits","none",	# Don't create a new fits
							  "--solved","none",	# Don't generate the solved output
							  "--match","none",		# Don't generate matched output
							  "--wcs","none",		# Don't generate wcs files
							  "--corr","none",		# Don't generate .corr files
							  "--rdls","none",		# Don't generate the point list
							  "--wcs","none",		# Don't generate wcs
							  "--temp-axy"			# We can't specify not to create the axy list, but we can write it to /tmp
							  ])

		cmd = ["/usr/bin/solve-field"]
		options = limitOptions + optimizedOptions + scaleOptions + fileOptions + [captureFile]

		if (debug):
			print("Executing:")
			print(cmd + options)

		# Note that the result of this command is sent to STDOUT
		result = subprocess.run(cmd + options, cwd="/tmp",capture_output=True, text=True)

		if (debug):
			print(result.stdout)
			print(result.stderr)

		# All files were either specified not to be created. The only one that seems to be forced is the %sindx.xyls file. Clean it up now
		xylsFile = self.tempDir + "/" + os.path.splitext(os.path.basename(captureFile))[0] + "-indx.xyls"
		if os.path.exists(xylsFile):
			if (debug):
				print("Cleaning up " + xylsFile)	
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


