import numpy as np
def GetIMUHeading(DataJson):
    return np.deg2rad(DataJson["IMU"]["Euler"][0] + 165)*0.998


def GetInitalData(DataJson):
    pX = DataJson["GPS"][0]
    pY = DataJson["GPS"][1]
    # Velo = DataJson["Encoder"]
    Velo = DataJson["inVelocity"]
    # Velo = 0

    Heading = GetIMUHeading(DataJson)
    return pX, pY, Velo, Heading

def GetCommandData(DataJson):
    Velo = DataJson["inVelocity"]*1.1
    Steer = np.deg2rad(DataJson["inSteer"])*0.998
    return Velo, Steer

def GetEncoderSpeed(DataJson):
    return DataJson["Encoder"]*1


def GetGPS(DataJson):
    return DataJson["GPS"]

def GetTimeStamp(DataJson):
    return DataJson["timeStamp"]

def GetAccel(DataJson):
    return DataJson["IMU"]["Linear Accel"]


def GetGyro(DataJson):
    return np.array(DataJson["IMU"]["Gyroscope"])

def GetAccel(DataJson):
    return np.array(DataJson["IMU"]["Accelerometer"])

def GetMagnet(DataJson):
    return np.array(DataJson["IMU"]["Magnetometer"])

def GetRawIMU(DataJson):
    return {
        "Gyro":GetGyro(DataJson),
        "Accel": GetAccel(DataJson),
        "Magnet": GetMagnet(DataJson),
    }

def GetEuler(DataJson):
    return DataJson["IMU"]["Euler"]