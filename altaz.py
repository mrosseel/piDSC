# Sept 8, 2021 10:30:00 AM
# loc 34 00' 17.6" N
#     084 22' 03.5" W

# 34.004889, -84.367639

#Alt +60 39' 22.4"
#AZ 192 02' 58.6"

# = 
# RA 07h 40m 26.26s
# DEC +05°10'33.1"



#from datetime import datetime

from dms2dec.dms_convert import dms2dec

from astropy import units as u
from astropy.coordinates import EarthLocation
from astropy.coordinates import SkyCoord
from astropy.time import Time


lat_dec = dms2dec("34°00'17.60 N")
lng_dec = dms2dec("84°22'03.5 W")

print("lat_dec: %f" % lat_dec)
print("lng_dec: %f" % lng_dec)

alt_dec = dms2dec("+60°39'22.4")
az_dec = dms2dec("192°02'58.6")

print("alt_dec: %f" % alt_dec)
print("az_dec: %f" % az_dec)

loc = EarthLocation(lat = lat_dec*u.deg, lon = lng_dec*u.deg, height = 300*u.m)

t = Time('2021-9-8 14:30:00')

c = SkyCoord(alt = alt_dec*u.deg, az = az_dec*u.deg, obstime = t, frame = 'altaz', location = loc)
radec = c.transform_to('icrs')

print("RA: " + radec.ra.to_string(u.hour))
print("DEC: " + radec.dec.to_string(u.degree, alwayssign=True))
