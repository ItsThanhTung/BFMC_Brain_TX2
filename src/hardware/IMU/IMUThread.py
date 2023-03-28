from src.templates.threadwithstop import ThreadWithStop
from adafruit_extended_bus import ExtendedI2C as I2C
import adafruit_bno055
from numpy import linalg
import numpy as np
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
        print("Before Vel")
        self.__velLock = Lock()
        self._vel = 0
        print("End vel")
        if(iscalib):
            print("Calibrated")

        super(IMUHandlerThread,self).__init__()

    def getVelo(self):
        vel = 0
        self.__velLock.acquire()
        vel = self._vel
        self.__velLock.release()
        return vel
    
    def _setVelo(self, newVelo):
        self.__velLock.acquire()
        self._vel = newVelo
        self.__velLock.release()

    def run(self):
        print("Haha")
        while self._running:
            vel = 0
            for i in range(10):
                accel_axis = self._sensor.linear_acceleration
                accel = linalg.norm(accel_axis[:2]).round(2)
                # if accel < self._accelThres:
                #     accel = 0
                vel += accel*self._dt
                time.sleep(self._dt)
            # print("accel {} Velo: {}".format(accel, vel))
            self._vel = vel
            # print("IMU Velo: ", np.round(vel,2))
            time.sleep(self._readInterval)
