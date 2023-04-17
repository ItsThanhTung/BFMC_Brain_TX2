import numpy as np
def GetIMUHeading(DataJson):
    return np.deg2rad(DataJson["IMU"]["Euler"][0] +18)


def GetInitalData(DataJson):
    pX = DataJson["GPS"][0]
    pY = DataJson["GPS"][1]
    # Velo = DataJson["Encoder"]
    Velo = DataJson["inVelocity"]
    Velo = 0

    Heading = GetIMUHeading(DataJson)
    return pX, pY, Velo, Heading

def GetCommandData(DataJson):
    Velo = DataJson["inVelocity"]
    Steer = np.deg2rad(DataJson["inSteer"])
    return Velo, Steer

def GetEncoderSpeed(DataJson):
    return DataJson["Encoder"]*1.1


def GetGPS(DataJson):
    return DataJson["GPS"]

def GetTimeStamp(DataJson):
    return DataJson["timeStamp"]

def GetAccel(DataJson):
    return DataJson["IMU"]["Linear Accel"]