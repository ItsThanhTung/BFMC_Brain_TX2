import json
import matplotlib.pyplot as plt
from src.hardware.data_fusion.CarEKF import CarEKF
import numpy as np
from src.utils.SensorProcess.utils import *

Delta_t = 0.01
CarFilter = CarEKF(Delta_t, 0.26)
# CarFilter.InitialState()

DataFile = open("SensorLog.txt","r")

Coor_fig, Coor_ax = plt.subplots()


img = plt.imread("Track_Test.png")
img = np.fliplr(img)
Coor_ax.imshow(img, extent=[0, 600, 0, 600])
Xcoor = [0]
YCoor = [0]

Data = DataFile.readline()
DataJson = json.loads(Data)
pX, pY, Velo, heading = GetInitalData(DataJson)
CarFilter.InitialState(pX, pY, Velo, heading)
initTime = GetTimeStamp(DataJson)
CarState = {
    "pX":[],
    "pY": [],
    "Velocity": [],
    "Heading":[]
}
rawCarStateList = []
FilteredCarStateList = []

timeStamp = []
rawVelocity = []

line = 0
prev_Coor = [0,0]
IMU_Velo = []

PrevVelo = np.array([0,0,0], dtype = float)

updateGPSTimes = 0

while True:
    Data = DataFile.readline()
    if not Data:
        break
    line+=1
    print("Line ", line)
    # GPS Running Reference
    CurrentTime = GetTimeStamp(DataJson)
    timeStamp.append(CurrentTime)
    
    DataJson = json.loads(Data)

    Accel = np.array(GetAccel(DataJson))
    Speed = GetEncoderSpeed(DataJson)
    if Speed < 0.15:
        PrevVelo = 0

    Accel[np.abs(Accel) < 1] = 0
    VeloVector = PrevVelo + Delta_t* Accel
    PrevVelo = VeloVector
    Velo = np.linalg.norm(VeloVector[:2])
    
    IMU_Velo.append(Velo)
    # print("Velo {} VeloVector {}, accel {}".format( Velo, VeloVector, Accel))

    x = DataJson["GPS"][0]*100
    y = DataJson["GPS"][1]*100
    Heading = GetIMUHeading(DataJson)
    Speed = GetEncoderSpeed(DataJson)
    Coor_ax.plot(x, y, marker = (3, 0, np.rad2deg(Heading) - 90), linestyle = 'None', color = "red")
    rawVelocity.append(Speed)
    # VeloRaw_ax.step(CurrentTime, Speed,   linewidth = 0.001, color = "red")
    # Xcoor.append(x)
    # YCoor.append(y)
    # continue
    # Predict Car State
    inputMat = {}
    inputMat["Velo"], inputMat["Angle"] = GetCommandData(DataJson)
    # inputMat["Velo"]*=1
    CarFilter.predict(inputMat)

    Coor = GetGPS(DataJson)
    if(Coor[0] != prev_Coor[0] or Coor[1] != prev_Coor[1]):
        CarFilter.GPS_Update(Coor[0], Coor[1])
        prev_Coor = Coor
        updateGPSTimes+=1

    CarFilter.IMU_Update(GetIMUHeading(DataJson))

    Speed = GetEncoderSpeed(DataJson)*1.2
    CarFilter.Encoder_Update(Speed)
    CurrentState = CarFilter.GetCarState()
    CurrentState["TimeStamp"]= GetTimeStamp(DataJson) - initTime

    CarState["Velocity"].append(CurrentState["Velo"])

    Coor_ax.plot(CurrentState['x']*100, CurrentState['y']*100, marker = (3, 0, np.rad2deg(CurrentState["Heading"]) - 90), 
                 linestyle = 'None', color = "yellow")
    print(CurrentState)

    plt.pause(0.001)

print("Processed Line {} ")

timeStamp = np.array(timeStamp)
timeStamp = timeStamp - timeStamp[0]

Velo_fig, Velo_ax = plt.subplots()
VeloRaw_fig, VeloRaw_ax = plt.subplots()

Velo_ax.set_title("Filtered Velo")
VeloRaw_ax.set_title("Raw Velocity")

# Velo_ax.plot(timeStamp, IMU_Velo, color = "red",  linewidth = 0.1)
Velo_ax.plot(timeStamp, CarState["Velocity"], color = "red",  linewidth = 0.1)
VeloRaw_ax.plot(timeStamp, rawVelocity, color="blue" , linewidth = 0.1)

# for State in CarStateListDict:
#     Coor_ax

plt.show()
    
