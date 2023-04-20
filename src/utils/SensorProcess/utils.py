import numpy as np
def GetIMUHeading(DataJson):
<<<<<<< HEAD
    return np.deg2rad(DataJson["IMU"]["Euler"][0] - 110)*1.005
=======
    return np.deg2rad(DataJson["IMU"]["Euler"][0] - 2)
>>>>>>> master


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
<<<<<<< HEAD
    return DataJson["Encoder"]*1.5
=======
    return DataJson["Encoder"]*1.1
>>>>>>> master


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
