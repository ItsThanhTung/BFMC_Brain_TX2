# Copyright (c) 2019, Bosch Engineering Center Cluj and BFMC organizers
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE

from src.templates.workerprocess                import WorkerProcess
from multiprocessing.connection import wait
from src.hardware.data_fusion.CarEKF import CarEKF
import json
import numpy as np
from threading import Lock, Thread, Event
import time
class CarEstimateProcess(WorkerProcess):
    #================================ VL53L0X PROCESS =====================================
    def __init__(self, inPs, outPs,debugPs, debug = False, enableLog = True, daemon = True):
        """Process that start the raspicam and pipes it to the output pipe, to another process.

        Parameters
        ----------

        """

        super(CarEstimateProcess,self).__init__( inPs, outPs, daemon = True)

        
        self._dt = 0.01
        self._LogInterval = self._dt
        self._debugSendInterval = 0.1

        self._IMU_Data = None
        self.__IMU_Lock = Lock()
        
        self._Encoder_Data = None
        self.__Encoder_Lock = Lock()

        self._GPS_Data = None
        self.__GPS_Lock = Lock()

        self._inSteer_Data = None
        self.__inSteer_Lock = Lock()

        self._inVelocity_Data = None
        self.__inVelocity_Lock = Lock()

        self.CarFilter = CarEKF(self._dt, 0.26)
        self._CarFilterLock = Lock()
        self._FilterInitEvent = Event()
        
        self._enableLog = enableLog
        if enableLog:
            self.LogFile = open("SensorLog.txt", "w")

        self.debugPs = debugPs
        self.debug = debug
        
    # ===================================== RUN ==========================================
    def run(self):
        """Apply the initializing methods and start the threads.
        """
        super(CarEstimateProcess,self).run()

    # ===================================== INIT TH ======================================
    def _init_threads(self):

        ListenDataTh = Thread(name= "ListenDataThread",target= self.RcvDataThread, daemon = True)
        self.threads.append(ListenDataTh)
        EKFPredictTh = Thread(name= "EKF PredictThread",target= self.EKF_PredictThread, daemon = True)
        self.threads.append(EKFPredictTh)
        SendTh = Thread(name="SendDataThread", target= self.DM_SendThread, daemon = True)
        self.threads.append(SendTh)

        if self._enableLog:
            LogDataTh = Thread(name="LogDataThread",target= self.LogDataThread, daemon = True)
            self.threads.append(LogDataTh)
        if self.debug:
            DebugTh = Thread(name="SendDebugThread",target = self.Debug_SendThread, daemon = True)
            self.threads.append(DebugTh)

    def EKF_PredictThread(self):
        self._FilterInitEvent.wait()
        print("Start EKF Predict")
        u={}
        while(True):
            u["Velo"] = self.inVelocity + 0.3
            u["Angle"] = self.Steering
            with self._CarFilterLock:
                # print("Predict Input", u)
                self.CarFilter.predict(u)
                # self.CarFilter.Encoder_Update(self.Encoder+0.1)
                # Heading = self.IMU_GetHeading()
                # self.CarFilter.IMU_Update(Heading)
            # print(Result)
            time.sleep(self._dt)
    
    def Debug_SendThread(self):
        self._FilterInitEvent.wait()
        while(True):
            time.sleep(self._debugSendInterval)
            with self._CarFilterLock:
                Result = self.CarFilter.GetCarState()
            # print("SendGPS: ", Result["x"], Result["y"])
            self.debugPs.send(Result)
    
    def DM_SendThread(self):
        self._FilterInitEvent.wait()
        print("Start send to DM")
        while(True):
            with self._CarFilterLock:
                Result = self.CarFilter.GetCarState()
            self.outPs["DM"].send(Result)


    def GetAllData(self):
        return {
                "IMU":self.IMU,
                "Encoder": self.Encoder,
                "GPS": self.GPS,
                "inSteer": self.Steering,
                "inVelocity": self.inVelocity,
                "timeStamp": time.time()
            }

    def LogDataThread(self):
        self._FilterInitEvent.wait()
        print("EKF Start Log Data")
        while(True):
            time.sleep(self._LogInterval)
            Data = self.GetAllData()
            self.LogFile.write(json.dumps(Data)+ "\r\n")    
    
    def _haveNone(self, Data):
        for Key in Data:
            if Data[Key] is None:
                # print("Dont have: ", Key)
                return True
        return False
    
    def RcvDataThread(self):
        reader  = list()
        for key in self.inPs:
            reader.append(self.inPs[key])
        print("Start EKF Rcv Data")
        while(True):
            for inP in wait(reader):
                if not self._FilterInitEvent.is_set():         
                    AllData = self.GetAllData()
                    if not self._haveNone(AllData):
                        GPS = self.GPS
                        Velo = self.Encoder
                        Heading = self.IMU_GetHeading()
                        self.CarFilter.InitialState(GPS[0], GPS[1], Velo, Heading)
                        self._FilterInitEvent.set()
                        # print("Have all Data Initialise Filter")
                        # print("Init Filter With ", AllData)

                try:
                    Data = inP.recv()
                    # print("Pipe rcv ", Data)
                except:
                    print("Pipe Error ", inP)
                else:
                    if inP == self.inPs["IMU"]:
                        self.IMU = Data
                        # print("IMU Rcv", self.IMU)
                        angle = self.IMU_GetHeading()
                        with self._CarFilterLock:
                            self.CarFilter.IMU_Update(angle)

                    elif inP == self.inPs["GPS"]:
                        self.GPS = Data["point"]
                        gpsX, gpsY = Data["point"][0], Data["point"][1]
                        with self._CarFilterLock:
                            self.CarFilter.GPS_Update(gpsX, gpsY)
                        # print("Rcv GPS: ", self.GPS)

                    elif inP == self.inPs["Encoder"]:
                        self.Encoder = Data
                        with self._CarFilterLock:
                            self.CarFilter.Encoder_Update(Data)
                        # print("Rcv Encoder ", self.Encoder)
                    
                    elif inP == self.inPs["DM"]:
                        if Data["type"] == "SPEED":
                            self.inVelocity = Data["value"]
                        elif Data["type"] == "STEER":
                            self.Steering = Data["value"]
                            # print("Steer Value ", self.Steering)
    def IMU_GetHeading(self):
        return np.deg2rad(self.IMU["Euler"][0] + 30)
    @property
    def IMU(self):
        IMUData = None
        with self.__IMU_Lock:
            IMUData = self._IMU_Data
        return IMUData
    @IMU.setter
    def IMU(self, newData):
        with self.__IMU_Lock:
            self._IMU_Data = newData

    @property
    def GPS(self):
        GPSData = None
        with self.__GPS_Lock:
            GPSData = self._GPS_Data
        return GPSData
    
    @GPS.setter
    def GPS(self, newData):
        with self.__GPS_Lock:
            self._GPS_Data = newData

    @property
    def Encoder(self):
        with self.__Encoder_Lock:
            EncData = self._Encoder_Data
        return EncData
    @Encoder.setter
    def Encoder(self, newData):
        with self.__Encoder_Lock:
            self._Encoder_Data = newData

    @property
    def Steering(self):
        with self.__inSteer_Lock:
            SteerData = self._inSteer_Data
        return SteerData
    
    @Steering.setter
    def Steering(self, newData):
        with self.__inSteer_Lock:
            self._inSteer_Data = newData

    @property
    def inVelocity(self):
        Data = None
        with self.__inVelocity_Lock:
            Data = self._inVelocity_Data
        return Data
    
    @inVelocity.setter
    def inVelocity(self, newData):
        with self.__inVelocity_Lock:
            self._inVelocity_Data = newData