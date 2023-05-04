import time
from adafruit_extended_bus import ExtendedI2C as I2C
import adafruit_bno055
from ahrs.filters.ekf import EKF
from ahrs import Quaternion
from ahrs.common.orientation import acc2q, am2angles
from ahrs.utils.wmm import WMM

import numpy as np


readInterval = 0.001

i2c = I2C(1)  # Device is /dev/i2c-1
print("Not init")
time.sleep(1)
sensor = adafruit_bno055.BNO055_I2C(i2c,0x29)

last_val = 0xFFFF

iscalib = sensor.calibrated

if(iscalib):
    print("Calibrated")

MyBNO = adafruit_bno055.BNO055_I2C(I2C(1), 0x29)

while True:
    vel = 0
    for i in range(10):
        accel_axis = sensor.linear_acceleration
        accel = linalg.norm(accel_axis[:2]).round(2)
        if accel < accel_thres:
            accel = 0
        vel += accel*readInterval
        time.sleep(0.01)
    # print("accel {} Velo: {}".format(accel, vel))
    print("velo ", vel)
    time.sleep(readInterval)
    