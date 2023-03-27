from src.templates.threadwithstop import ThreadWithStop
from adafruit_extended_bus import ExtendedI2C as I2C
import adafruit_bno055
from numpy import linalg
from threading import Lock

import time
class IMUHandlerThread(ThreadWithStop):
    def __init__(self, outPs, readInterval = 0.1, dt = 0.01):
        """
    
    Car Handler Thread object

    Parameters
    -------------


    """
        self._outPs = outPs
        self._readInterval = readInterval
        self._dt = dt

        self._accelThres =  0.2

        i2c = I2C(0)  
        self._sensor = adafruit_bno055.BNO055_I2C(i2c, 0x29)
        print("IMU Init Done")

        iscalib = self._sensor.calibrated

        self._vel = 0
        self._velLock = Lock()

        if(iscalib):
            print("Calibrated")

        super(IMUHandlerThread,self).__init__()

    @property
    def _vel(self):
        vel = 0
        self._velLock.acquire()
        vel = self._vel
        self._velLock.release()
        return vel
    @_vel.setter
    def _vel(self, vel):
        self._velLock.acquire()
        self._vel  = vel
        self._velLock.release()

    def run(self):
        vel = 0
        for i in range(10):
            accel_axis = self._sensor.linear_acceleration
            accel = linalg.norm(accel_axis[:2]).round(2)
            if accel < self._accel_thres:
                accel = 0
            vel += accel*self._dt
            time.sleep(self._dt)
        # print("accel {} Velo: {}".format(accel, vel))
        self._vel = vel
        print("IMU Velo: ", vel)
        time.sleep(self._readInterval)
