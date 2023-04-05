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
import json

from threading import Lock, Thread
import time
class CarEstimateProcess(WorkerProcess):
    #================================ VL53L0X PROCESS =====================================
    def __init__(self, inPs, outPs, daemon = True):
        """Process that start the raspicam and pipes it to the output pipe, to another process.

        Parameters
        ----------

        """

        super(CarEstimateProcess,self).__init__( inPs, outPs, daemon = True)
        self._LogInterval = 0.01

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

        self.LogFile = open("SensorLog.txt", "w")

    # ===================================== RUN ==========================================
    def run(self):
        """Apply the initializing methods and start the threads.
        """
        super(CarEstimateProcess,self).run()

    # ===================================== INIT TH ======================================
    def _init_threads(self):

       ListenDataTh =  Thread(target= self.RcvDataThread, daemon = True)
       self.threads.append(ListenDataTh)
       LogDataTh = Thread(target= self.LogDataThread, daemon = True)
       self.threads.append(LogDataTh)

    def LogDataThread(self):

        
        while(True):
            time.sleep(self._LogInterval)
            Data = {
                "IMU":self.IMU,
                "Encoder": self.Encoder,
                "GPS": self.GPS,
                "inSteer": self.Steering,
                "inVelocity": self.inVelocity,
                "timeStamp": time.time()
            }
            for Val in Data.values():
                if Val is None:
                    continue
            self.LogFile.writelines(json.dumps(Data))    
    

    def RcvDataThread(self):
        reader  = list()
        for key in self.inPs:
            reader.append(self.inPs[key])

        while(True):
            for inP in wait(reader):
                try:
                    Data = inP.recv()
                    # print("Pipe rcv ", Data)
                except:
                    print("Pipe Error ", inP)
                else:
                    if inP == self.inPs["IMU"]:
                        self.IMU = Data
                        # print("IMU Rcv", self.IMU)
                    elif inP == self.inPs["GPS"]:
                        self.GPS = Data["point"]
                        # print("Rcv GPS: ", self.GPS)
                    elif inP == self.inPs["Encoder"]:
                        self.Encoder = Data
                        print("Rcv Encoder ", self.Encoder)
                    elif inP == self.inPs["InSteer"]:
                        self.Steering = Data
                        print("Rcv Steer ", self.Steering)
                    elif inP == self.inPs["InSpeed"]:
                        self.inVelocity = Data
                        print("Velo ", self.inVelocity)
    
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
        SteerData = None
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