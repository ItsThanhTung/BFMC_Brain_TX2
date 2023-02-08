import sys
sys.path.append('.')
import RTIMU
import os.path
import time
import math
import threading
class IMUHandler(threading.Thread):
    def __init__(self): 
        threading.Thread.__init__(self,daemon=False)
        self.running = True

        self.SETTINGS_FILE = "RTIMULib"
        print("Using settings file " + self.SETTINGS_FILE + ".ini")
        if not os.path.exists(self.SETTINGS_FILE + ".ini"):
            print("Settings file does not exist, will be created")
        self.s = RTIMU.Settings(self.SETTINGS_FILE)
        self.imu = RTIMU.RTIMU(self.s)
        print(help(self.imu))
        print("IMU Name: " + self.imu.IMUName())
        if (not self.imu.IMUInit()):
            print("IMU Init Failed")
            self.stop()
            sys.exit(1)
        else:
            print("IMU Init Succeeded")
        # print(help(self.imu))
        self.imu.setSlerpPower(0.02)
        self.imu.setGyroEnable(True)
        self.imu.setAccelEnable(True)
        self.imu.setCompassEnable(True)
        self.yaw0 = 0
        self.yaw = 0
        self.poll_interval = self.imu.IMUGetPollInterval()
        print("Recommended Poll Interval: %dmS\n" % self.poll_interval)
        
    def run(self):
        while self.running == True:
            if self.imu.IMURead():
                self.data = self.imu.getIMUData()
                self.fusionPose = self.data["fusionPose"]
                self.accel = self.data["accel"]
                self.roll  =  math.degrees(self.fusionPose[0])
                self.pitch =  math.degrees(self.fusionPose[1])
                self.yaw   =  math.degrees(self.fusionPose[2])
                self.accelx =  self.accel[0]
                self.accely =  self.accel[1]
                self.accelz =  self.accel[2]


                # print("roll = %f pitch = %f yaw = %f" % (self.roll,self.pitch,self.yaw))
                time.sleep(self.poll_interval*1.0/1000.0)
    def set_yaw(self):
        self.yaw0 = self.yaw
    def get_yaw(self):
        return self.yaw-self.yaw0
    def stop(self): 
        print('Killed IMU')
        self.running = False
        # self.stop()