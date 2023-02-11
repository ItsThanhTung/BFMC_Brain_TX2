import time

from adafruit_extended_bus import ExtendedI2C as I2C
import adafruit_bno055

class IMUHandler:
    def __init__(self): 
        i2c = I2C(0)  
        print("Not init")
        time.sleep(0.5)
        self.sensor = adafruit_bno055.BNO055_I2C(i2c, 0x29)

        print("Inited")
        last_val = 0xFFFF

        iscalib = self.sensor.calibrated

        if(iscalib):
            print("Calibrated")
            
        self.yaw0 = 0
        self.yaw = 0
        self.euler = None
              
    def set_yaw(self):
        self.yaw0 = self.sensor.euler[0]
    
    def get_yaw(self):
        delta_yaw = self.sensor.euler[0] - self.yaw0
        return delta_yaw if delta_yaw <= 180 else delta_yaw -360
