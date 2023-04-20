from src.templates.threadwithstop import ThreadWithStop
from adafruit_extended_bus import ExtendedI2C as I2C
import adafruit_bno055
from numpy import linalg
import numpy as np
from threading import Lock

import time
class IMUHandlerThread(ThreadWithStop):
    def __init__(self, outPs, readInterval = 0.01, dt = 0.01):
        """
    
    Car Handler Thread object

    Parameters
    -------------


    """
        self._outPs = outPs
        self._readInterval = readInterval
        self._dt = dt

        self._accelThres =  0.2

        self._sensor = adafruit_bno055.BNO055_I2C(I2C(1), 0x29)
        print("IMU Init Done")

        iscalib = self._sensor.calibrated
        self.__velLock = Lock()
        self._vel = 0
        self._prevVelo = 0
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
    
    def _getAccel(self):
        accel_axis = self._sensor.linear_acceleration
        return linalg.norm(accel_axis[:2]).round(2)
    def run(self):
        self._prevVelo = 0
        while self._running:
            time.sleep(self._readInterval)
            Data = {
                "Accelerometer": self._sensor.acceleration,
                "Magnetometer": self._sensor.magnetic,
                "Gyroscope": self._sensor.gyro,
                "Euler": self._sensor.euler,
                "Quaternion": self._sensor.quaternion,
                "Linear Accel":self._sensor.linear_acceleration,
                "Gravity": self._sensor.gravity
            }
            self._outPs.send(Data)
