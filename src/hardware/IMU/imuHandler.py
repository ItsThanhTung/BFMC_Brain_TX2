import sys
sys.path.append('.')

import RTIMU
from smbus2 import SMBus

import os.path
import time
import math
import threading
from adafruit_extended_bus import ExtendedI2C as I2C
import adafruit_bno055
class IMUHandler(threading.Thread):
    def __init__(self): 
        threading.Thread.__init__(self,daemon=False)
        self.running = True

        i2c = I2C(0)  
        print("Not init")
        time.sleep(1)
        self.sensor = adafruit_bno055.BNO055_I2C(i2c,0x29)

        print("Inited")
        last_val = 0xFFFF

        iscalib = self.sensor.calibrated

        if(iscalib):
            print("Calibrated")
        self.yaw0 = 0
        self.yaw = 0
        self.euler =()
        
    def run(self):
        #read imu here
        while self.running == True:
            self.euler = self.sensor.euler
            time.sleep(0.01)
        
        
    def set_yaw(self):
        self.yaw0 = self.euler[0]
    def get_yaw(self):
        delta_yaw = self.euler[0]-self.yaw0
        return delta_yaw if delta_yaw <= 180 else delta_yaw -360
    def stop(self): 
        print('Killed IMU')
        self.running = False
        # self.stop()