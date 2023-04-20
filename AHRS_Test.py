import json
import matplotlib.pyplot as plt
from src.hardware.data_fusion.CarEKF import CarEKF
import numpy as np
from src.utils.SensorProcess.utils import *
from matplotlib.markers import MarkerStyle

from ahrs.filters.ekf import EKF
from ahrs import Quaternion
from ahrs.common.orientation import acc2q, am2angles
from ahrs.utils.wmm import WMM
DataFile = open("log/SensorLog.txt","r")
ProcessLog = open("log/ProcessLog.txt", "w")

line = 0
# exit()
imuEKF = EKF(frequency=10)

Data = DataFile.readline()
DataJson = json.loads(Data)
rawIMU = GetRawIMU(DataJson)

FilteredValue = []
FilteredValue.append(acc2q(rawIMU["Accel"]))
print("Init Value ", FilteredValue)
print("Init Angle ",am2angles(rawIMU["Accel"], rawIMU["Magnet"], in_deg=True))
print("Heading ", GetIMUHeading(DataJson))
while True:
    Data = DataFile.readline()
    if not Data:
        break
    line+=1
    DataJson = json.loads(Data)
    rawIMU = GetRawIMU(DataJson)
    FilteredQuat = imuEKF.update(FilteredValue[-1], rawIMU["Gyro"], rawIMU["Accel"], rawIMU["Magnet"])
    FilteredValue.append(FilteredQuat)
    euler = Quaternion(FilteredQuat).to_angles()
    # print("Euler Val", euler)
    # print(Data)
