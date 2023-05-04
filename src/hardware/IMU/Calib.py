# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

from imuHandler import IMUHandler
import matplotlib.pyplot as plt
import json
from time import sleep
import numpy as np
import time

from adafruit_extended_bus import ExtendedI2C as I2C
import adafruit_bno055


CALIBRATED = True
WRITECALIB = False

MyBNO = adafruit_bno055.BNO055_I2C(I2C(1), 0x29)
# a,b,c,d,e,f = remap 
# print(a+b+c+d+e+f)
# MyBNO.axis_remap = 2,0,1,0,0,0

MyBNO.offsets_accelerometer
def GetCabliOffset(Sensor: adafruit_bno055.BNO055):
	return {
		"AccelOffset" : Sensor.offsets_accelerometer,
		"GyroOffset" : Sensor.offsets_gyroscope,
		"MagnetOffset": Sensor.offsets_magnetometer,
		"AccelRad": Sensor.radius_accelerometer,
		"MagnetRad": Sensor.radius_magnetometer
	}

def SetCalibOffset(Sensor: adafruit_bno055.BNO055, CalibOffset):
		Sensor.offsets_accelerometer = tuple(CalibOffset["AccelOffset"])		
		Sensor.offsets_gyroscope = tuple(CalibOffset["GyroOffset"]) 
		Sensor.offsets_magnetometer = tuple(CalibOffset["MagnetOffset"])
		Sensor.radius_accelerometer = CalibOffset["AccelRad"]
		Sensor.radius_magnetometer = CalibOffset["MagnetRad"]

def main():
	if CALIBRATED == False:
		print("Store Calib Data")
		CalibData = GetCabliOffset(MyBNO)
		with open("CalibData.json", 'w') as file:
			file.write(json.dumps(CalibData))
	
	if WRITECALIB == True:
		print("Write old calib data")
		with open("CalibData.json", 'r') as file:
			Calib = json.load(file)
			SetCalibOffset(MyBNO, Calib)
			print(Calib["AccelOffset"])

	MyBNO.mode = adafruit_bno055.NDOF_MODE
	time.sleep(3)
	while True:
		calib = MyBNO.calibration_status
		print("Sys {} gyro {} accel {} magnet {}".format(calib[0], calib[1], calib[2], calib[3]))
		print("Euler ",MyBNO.euler)
		# print("AccelRad {} MagnetRad {} ".format(MyBNO.radius_accelerometer, MyBNO.radius_magnetometer))
		sleep(0.05)
 


if __name__ == "__main__":
	main()


