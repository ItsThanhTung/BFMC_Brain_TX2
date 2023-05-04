import json
import matplotlib.pyplot as plt
from src.hardware.data_fusion.CarEKF import CarEKF
import numpy as np
from src.utils.SensorProcess.utils import *
from matplotlib.markers import MarkerStyle

Delta_t = 0.01
CarFilter = CarEKF(Delta_t, 0.26)
# CarFilter.InitialState()

DataFile = open("log/SensorLog_Lane.txt","r")

Coor_fig, Coor_ax = plt.subplots()


img = plt.imread("gray_not.jpg")
img = np.flipud(img)
Coor_ax.imshow(img, extent=[0, 14.65, 0, 15])
Xcoor = [0]
YCoor = [0]

Data = DataFile.readline()
DataJson = json.loads(Data)
pX, pY, Velo, heading = GetInitalData(DataJson)
CarFilter.InitialState(pX, pY, Velo, heading)
initTime = GetTimeStamp(DataJson)
prevTime = initTime
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

EulerRoll = []

print("Initialise ", CarFilter.GetCarState())
ProcessLog = open("ProcessLog.txt", "w")


while True:
    Data = DataFile.readline()
    if not Data:
        break
    line+=1

    # print("Line ", line)
    # GPS Running Reference
    CurrentTime = GetTimeStamp(DataJson)
    timeStamp.append(CurrentTime)
    
    DataJson = json.loads(Data)

    euler = GetEuler(DataJson)
    EulerRoll.append(euler[2])

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

    x = DataJson["GPS"][0]
    y = DataJson["GPS"][1]
    Heading = GetIMUHeading(DataJson)
    Speed = GetEncoderSpeed(DataJson)
    marker_raw = MarkerStyle("$>$")
    marker_raw._transform.rotate_deg(np.rad2deg(Heading))
    Coor_ax.plot(x, y, marker = marker_raw, linestyle = 'None', color = "red")
    rawVelocity.append(Speed)
    # VeloRaw_ax.step(CurrentTime, Speed,   linewidth = 0.001, color = "red")
    # Xcoor.append(x)
    # YCoor.append(y)
    # continue
    # Predict Car State
    inputMat = {}
    inputMat["Velo"], inputMat["Angle"] = GetCommandData(DataJson)
    # inputMat["Velo"]*=1
    time = GetTimeStamp(DataJson) 
    CarFilter.predict(inputMat,time - prevTime)
    prevTime = time

    Coor = GetGPS(DataJson)
    
    if(Coor[0] != prev_Coor[0] or Coor[1] != prev_Coor[1]):
        CarFilter.GPS_Update(Coor[0], Coor[1])
        prev_Coor = Coor
        updateGPSTimes+=1

    CarFilter.IMU_Update(GetIMUHeading(DataJson))

    Speed = GetEncoderSpeed(DataJson)
    CarFilter.Encoder_Update(Speed)
    CurrentState = CarFilter.GetCarState()
    # CurrentState["TimeStamp"]= GetTimeStamp(DataJson) - initTime

    CarState["Velocity"].append(CurrentState["Velo"])

    marker = MarkerStyle("$>$")
    marker._transform.rotate_deg(np.rad2deg(CurrentState["Heading"]))
    Coor_ax.plot(CurrentState['x'], CurrentState['y'], marker = marker, 
                 linestyle = 'None', color = "yellow")
    # print(CurrentState)
    ProcessLog.write(json.dumps(CurrentState)+"\n")
    # plt.pause(0.0001)

print("Processed Line {} ")

timeStamp = np.array(timeStamp)
timeStamp = timeStamp - timeStamp[0]

Velo_fig, Velo_ax = plt.subplots()
VeloRaw_fig, VeloRaw_ax = plt.subplots()

Roll_fig, Roll_ax = plt.subplots()


Velo_ax.set_title("Filtered Velo")
VeloRaw_ax.set_title("Raw Velocity")

Roll_ax.set_title("Euler")


# Velo_ax.plot(timeStamp, IMU_Velo, color = "red",  linewidth = 0.1)
Velo_ax.plot(timeStamp, CarState["Velocity"], color = "red",  linewidth = 0.1)
VeloRaw_ax.plot(timeStamp, rawVelocity, color="blue" , linewidth = 0.1)

Roll_ax.plot(timeStamp, EulerRoll, color="brown" , linewidth = 0.5)


plt.show()
    
