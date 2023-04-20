from ahrs.filters.ekf import EKF as ahrsEKF
from ahrs import Quaternion
from ahrs.common.orientation import acc2q, am2angles,ecompass
from ahrs.utils.wmm import WMM

from adafruit_extended_bus import ExtendedI2C as I2C
import adafruit_bno055

import numpy as np
import time

MyBNO = adafruit_bno055.BNO055_I2C(I2C(1), 0x29)
MyBNO.mode = adafruit_bno055.NDOF_MODE

# wmmModel = WMM(latitude = 10.8697511, longitude = 106.8025341)
wmmModel = WMM(longitude = 10.8697511, latitude = 106.8025341)


imuEKF = ahrsEKF(frequency = 100, magnetic_ref = [wmmModel.X, wmmModel.Y, wmmModel.Z])

Accel= np.array(MyBNO.acceleration)
Gyro = np.array(MyBNO.gyro) 
Magnet = np.array(MyBNO.magnetic)
PrevVal = ecompass(Accel, Magnet, representation="quaternion")
# PrevVal = acc2q(Accel)
Norm = np.linalg.norm(PrevVal)

line = 0
while True:
    Accel= np.array(MyBNO.acceleration)
    Gyro = np.array(MyBNO.gyro) 
    Magnet = np.array(MyBNO.magnetic)
    Angle = imuEKF.update(PrevVal, Accel, Gyro, Magnet)
    PrevVal = Angle
    AngleDeg = Quaternion(Angle).to_angles()
    print("Compute Angle {} Euler {} ".format(AngleDeg, MyBNO.euler))
    time.sleep(0.001)