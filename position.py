import time
import math
import board
import busio


from adafruit_bno08x import (
    BNO_REPORT_ACCELEROMETER,
    BNO_REPORT_GYROSCOPE,
    BNO_REPORT_MAGNETOMETER,
    BNO_REPORT_ROTATION_VECTOR,
)
from adafruit_bno08x.i2c import BNO08X_I2C

i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
bno = BNO08X_I2C(i2c)

bno.enable_feature(BNO_REPORT_ACCELEROMETER)
bno.enable_feature(BNO_REPORT_GYROSCOPE)
bno.enable_feature(BNO_REPORT_MAGNETOMETER)
bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)


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

def euler_to_alt_az1(roll_x, pitch_y, yaw_z):
    alt = yaw_z * 180 / math.pi * 100
    az = -roll_x * 180 / math.pi * 100

    return alt, az 

# https://answers.ros.org/question/229797/calculate-azimuth-and-elevation-angles/
def euler_to_alt_az2(roll_x, pitch_y, yaw_z):
    magnitude = math.sqrt((roll_x*roll_x) + (pitch_y*pitch_y) + (yaw_z*yaw_z));
    azimuth   = math.atan2(pitch_y, roll_x);
    elevation = math.asin(yaw_z / magnitude);
    return elevation, azimuth 

# https://www.euclideanspace.com/maths/geometry/rotations/euler/


# x = psi / bank / tilt / ψ / roll
# y = theta / heading / azimuth / θ / yaw
# z = phi / attitude / elevation / φ / pitch

# https://gist.github.com/telegraphic/841212e8ab3252f5cffe
def euler_to_alt_az(theta, phi, psi):
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

while True:

    time.sleep(2)
#    print("Acceleration:")
#    accel_x, accel_y, accel_z = bno.acceleration  # pylint:disable=no-member
#    print("X: %0.6f  Y: %0.6f Z: %0.6f  m/s^2" % (accel_x, accel_y, accel_z))
#    print("")

#    print("Gyro:")
#    gyro_x, gyro_y, gyro_z = bno.gyro  # pylint:disable=no-member
#    print("X: %0.6f  Y: %0.6f Z: %0.6f rads/s" % (gyro_x, gyro_y, gyro_z))
#    print("")

#    print("Magnetometer:")
#    mag_x, mag_y, mag_z = bno.magnetic  # pylint:disable=no-member
#    print("X: %0.6f  Y: %0.6f Z: %0.6f uT" % (mag_x, mag_y, mag_z))
#    print("")

#    print("Rotation Vector Quaternion:")
    qx, qy, qz, qw = bno.quaternion  # pylint:disable=no-member
    print("Quaternion I: %0.6f  J: %0.6f K: %0.6f  Real: %0.6f" % (qx, qy, qz, qw))
#    print("")

    # https://www.euclideanspace.com/maths/geometry/rotations/conversions/quaternionToEuler/
    # heading = atan2(2*qy*qw-2*qx*qz , 1 - 2*qy2 - 2*qz2)
    # attitude = asin(2*qx*qy + 2*qz*qw)
    # bank = atan2(2*qx*qw-2*qy*qz , 1 - 2*qx2 - 2*qz2)

    # # first convert quaterion coordinates to euler coordinates
    # yaw   = math.atan2(2.0 * (qy *qzk + qx * qw), qx * qx + qy *qz -qzk * q_k - qw * qw);
    # pitch = -math.asin(2.0 * (qy *qzreal - qx * q_k));
    # roll  = math.atan2(2.0 * (qx * qy +qzk * qw), qx * qx - qy *qz -qzk * q_k + qw * qw);

    roll_x, pitch_y, yaw_z = quaternion_to_euler(qx, qy, qz, qw);


    print("Euler: roll: %0.6f, pitch: %0.6f, yaw: %0.6f" % (roll_x, pitch_y, yaw_z))
    print("")

    # euler to alz/az
    alt, az = euler_to_alt_az(roll_x, pitch_y, yaw_z)

    # convert radians to degrees
    alt = alt * 180 / math.pi
    az = -az * 180 / math.pi

    print("alt: %0.6f  az: %0.6f" % (alt, az))
    print("")

    # https://answers.ros.org/question/229797/calculate-azimuth-and-elevation-angles/


    alt_d, alt_m, alt_s = decdeg2dms(alt)
    az_d, az_m, az_s = decdeg2dms(az)

    print("alt: %i°%i'%0.2f" % (alt_d, alt_m, alt_s))
    print("az: %i°%i'%0.2f" % (az_d, az_m, az_s))






