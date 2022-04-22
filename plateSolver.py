import os
import subprocess
import re
from solveResult import SolveResult


debug = False


class PlateSolver:
	def __init__(self, tempDir = "/tmp"):
		self.tempDir = tempDir

	def solveImage(self, captureFile):

		limitOptions = 		["--no-plots","--overwrite","--skip-solved","--cpulimit","7"]
		optimizedOptions = 	["--downsample","4","--cpulimit","10","--no-remove-lines","--uniformize","0"]
		scaleOptions = 		["--scale-units","arcsecperpix","--scale-low","14.85","--scale-high","15.85"]
		fileOptions = 		["--dir",self.tempDir,"--new-fits","none","--solved","none","--match","none","--wcs","none","--corr","none","--rdls","none","--wcs","none","--temp-axy"]

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
		xylsFile = self.tempDir + "/" + os.path.splitext(os.path.basename(captureFile))[0] + "-indx.xyls"
		if os.path.exists(xylsFile):
			if (debug):
				print("Cleaning up " + xylsFile)	
			os.remove(xylsFile)

		return self.__parseSolvedOutput(result.stdout)

	def __parseSolvedOutput(self, result):
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


