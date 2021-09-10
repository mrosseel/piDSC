import time
import math
import board
import busio
from dms2dec.dms_convert import dms2dec
from adafruit_bno08x import (
    BNO_REPORT_ACCELEROMETER,
    BNO_REPORT_GYROSCOPE,
    BNO_REPORT_MAGNETOMETER,
    BNO_REPORT_ROTATION_VECTOR,
)
from adafruit_bno08x.i2c import BNO08X_I2C

print("Loading astropy")
from astropy import units as u
from astropy.coordinates import EarthLocation
from astropy.coordinates import SkyCoord
from astropy.time import Time
from time import perf_counter

def decdeg2dms(dd):
   is_positive = dd >= 0
   dd = abs(dd)
   minutes,seconds = divmod(dd*3600,60)
   degrees,minutes = divmod(minutes,60)
   degrees = degrees if is_positive else -degrees
   return (degrees,minutes,seconds)

# from https://automaticaddison.com/how-to-convert-a-quaternion-into-euler-angles-in-python/
# output is touple in radians
def quaternion_to_euler(x, y, z, w):
    """
    Convert a quaternion into euler angles (roll, pitch, yaw)
    roll is rotation around x in radians (counterclockwise)
    pitch is rotation around y in radians (counterclockwise)
    yaw is rotation around z in radians (counterclockwise)
    """
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll_x = math.atan2(t0, t1)
 
    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    pitch_y = math.asin(t2)
 
    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    yaw_z = math.atan2(t3, t4)
 
    return roll_x, pitch_y, yaw_z # in radians

# def euler_to_alt_az1(roll_x, pitch_y, yaw_z):
#     alt = yaw_z * 180 / math.pi * 100
#     az = -roll_x * 180 / math.pi * 100

#     return alt, az 

# # https://answers.ros.org/question/229797/calculate-azimuth-and-elevation-angles/
# def euler_to_alt_az2(roll_x, pitch_y, yaw_z):
#     magnitude = math.sqrt((roll_x*roll_x) + (pitch_y*pitch_y) + (yaw_z*yaw_z));
#     azimuth   = math.atan2(pitch_y, roll_x);
#     elevation = math.asin(yaw_z / magnitude);
#     return elevation, azimuth 

# https://www.euclideanspace.com/maths/geometry/rotations/euler/
# x = psi / bank / tilt / ψ / roll
# y = theta / heading / azimuth / θ / yaw
# z = phi / attitude / elevation / φ / pitch

# https://gist.github.com/telegraphic/841212e8ab3252f5cffe
#def euler_to_alt_az(theta, phi, psi):
def euler_to_alt_az(psi, theta, phi):
    """ Az-El to Theta-Phi conversion.
  
    Args:
        theta (float or np.array): Theta angle, in radians
        phi (float or np.array): Phi angle, in radians
  
    Returns:
      (az, el): Tuple of corresponding (azimuth, elevation) angles, in radians
    """
    sin_el = math.sin(phi) * math.sin(theta)
    tan_az = math.cos(phi) * math.tan(theta)
    el = math.asin(sin_el)
    az = math.atan(tan_az)

    return el, az

def initBNO(i2c):
    bno = BNO08X_I2C(i2c)

    bno.enable_feature(BNO_REPORT_ACCELEROMETER)
    bno.enable_feature(BNO_REPORT_GYROSCOPE)
    bno.enable_feature(BNO_REPORT_MAGNETOMETER)
    bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)

    return bno;

def getCurrentAltAz(bno):
    """ Fetches the current rotation coordinates from the bno08x sensor
        and return them as Alt/Az degrees

    Args: 
        bno: BNO08X_I2C object

    Returns:
        (alt, az): Tuple of current position, in degrees
    """
    # Get the rotation vector quaternion from the bno08x device
    qx, qy, qz, qw = bno.quaternion 
    #print("Quaternion I: %0.6f  J: %0.6f K: %0.6f  Real: %0.6f" % (qx, qy, qz, qw))

    # convert the quaternion values to euler angles
    roll_x, pitch_y, yaw_z = quaternion_to_euler(qx, qy, qz, qw);
    #print("Euler: roll: %0.6f, pitch: %0.6f, yaw: %0.6f" % (roll_x, pitch_y, yaw_z))

    # convert euler to alz/az (radians)
    alt_rad, az_rad = euler_to_alt_az(roll_x, pitch_y, yaw_z)

    # convert radians to degrees
    alt = alt_rad * 180 / math.pi
    az = -az_rad * 180 / math.pi

    # #print("Alt: %0.6f radians / Az: %0.6f radians" % (alt, az))

    return alt, az

def getCurentRaDec(bno, earthLocation):
    """ Fetches the current Alt/Az from the bno008x sensor
        Using the astropy.coordinates.EarthLocation and the current system time, 
        compute and return the current RA and Dec
    """

    # Get the current Alt/Az (in degrees) from the bno008x sensor
    alt, az = getCurrentAltAz(bno)

    # Generate the current sky coordinates based on alt, az, curret time, and current location
    c = SkyCoord(alt = alt*u.deg, az = az*u.deg, obstime = Time.now(), frame = 'altaz', location = earthLocation)
    radec = c.transform_to('icrs')

    # https://docs.astropy.org/en/stable/coordinates/angles.html#representation
    # print("RA: " + radec.ra.to_string(u.hour))
    # print("DEC: " + radec.dec.to_string(u.degree, alwayssign=True))
    return radec


print("Init BNO")
i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
bno = initBNO(i2c)

print("Setting up location")
lat_dec = dms2dec("34°00'17.60 N")
lng_dec = dms2dec("84°22'03.5 W")
loc = EarthLocation(lat = lat_dec*u.deg, lon = lng_dec*u.deg, height = 300*u.m)

print("Starting loop")

while True:

    # Get the current Alt/Az (in degrees) from the bno008x sensor
    # alt, az = getCurrentAltAz(bno)

    # alt_d, alt_m, alt_s = decdeg2dms(alt)
    # az_d, az_m, az_s = decdeg2dms(az)

    # print("Alt: %i°%i'%0.2f" % (alt_d, alt_m, alt_s))
    # print("Az: %i°%i'%0.2f" % (az_d, az_m, az_s))

    t0 = perf_counter()
    radec = getCurentRaDec(bno, loc)

    print(f'RA/DEC took {perf_counter() - t0:.2f} s')

    print("RA: " + radec.ra.to_string(u.hour))
    print("DEC: " + radec.dec.to_string(u.degree, alwayssign=True))

    time.sleep(2)


