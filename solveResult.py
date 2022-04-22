import datetime

class SolveResult:
	def __init__(self, ra = 0, dec = 0, validSolve = False, captureTime = datetime.datetime.now()):
		self.validSolve = validSolve
		self.ra = ra
		self.dec = dec
		self.rotation = 0
		self.captureTime = captureTime

	def toString(self):
		return "RA: " + str(self.ra) + "\nDEC: " + str(self.dec) + "\nRotation: " + str(self.rotation)