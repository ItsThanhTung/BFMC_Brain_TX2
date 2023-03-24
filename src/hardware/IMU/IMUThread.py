from src.templates.threadwithstop import ThreadWithStop
from adafruit_extended_bus import ExtendedI2C as I2C
import adafruit_bno055

import time
class IMUHandlerThread(ThreadWithStop):
    def __init__(self, outPs, readInterval = 0.1):
        """
    
    Car Handler Thread object

    Parameters
    -------------


    """
        self._outPs = outPs
        self._readInterval = readInterval

        i2c = I2C(0)  
        self.sensor = adafruit_bno055.BNO055_I2C(i2c, 0x29)
        print("IMU Init Done")

        iscalib = self.sensor.calibrated

        self._vel = 0
        if(iscalib):
            print("Calibrated")

        super(IMUHandlerThread,self).__init__()
    
    def run(self):
        while True:
            accel = self.sensor.linear_acceleration
            self._vel += self._readInterval.acc* self._readInterval
            time.sleep(self._readInterval)
