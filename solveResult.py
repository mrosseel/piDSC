import datetime
import math

class SolveResult:
	def __init__(self, validSolve = False, captureTime = datetime.datetime.now()):
		self.validSolve = validSolve
		self.ra_deg = 0
		self.dec_deg = 0
		self.ra_hms = None
		self.dec_dms = None
		self.rotation = 0
		self.captureTime = captureTime

	def toString(self):
		return "RA: " + str(self.ra_deg) + "\nDEC: " + str(self.dec_deg) + "\nRotation: " + str(self.rotation)

	def lx200ra(self, highPrecision = True):
		# HH:MM.T# or HH:MM:SS#
		ra_h, ra_m, ra_s = self.ra_hms.split(':')
		if (highPrecision):
			return ("{:02d}:{:02d}:{:02d}#").format(int(ra_h),int(ra_m),math.trunc(float(ra_s)))		
		else:
			## todo
			return ("{:02d}:{:02d}:{:02d}#").format(int(ra_h),int(ra_m),math.trunc(float(ra_s)))		

	def lx200dec(self, highPrecision = True):
		# sDD*MM# or sDD*MM’SS#
		dec_d, dec_m, dec_s = self.dec_dms.split(':')
		if (highPrecision):
			return ("{:+02d}*{:02d}’{:02d}#").format(int(dec_d),int(dec_m),math.trunc(float(dec_s)))		
		else:
			return ("{:+02d}*{:02d}#").format(int(dec_d),int(dec_m))