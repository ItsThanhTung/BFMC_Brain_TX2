import numpy as np
from threading import Lock, Event
from src.templates.threadwithstop import ThreadWithStop

class CarPoseThread(ThreadWithStop):
    def __init__(self, inP):
        super(CarPoseThread,self).__init__(name="CarPoseThread")

        self.inP = inP
        self.InitDoneEvent = Event()
        self.__CarPoseLock = Lock()
        self._CarPose = None

    def waitInitDone(self):
        self.InitDoneEvent.wait()

    def run(self):
        Data = self.inP.recv()
        self.CarPose = Data
        self.InitDoneEvent.set()

        while self._running:
            Data = self.inP.recv()
            self.CarPose = Data
    def GetCarPose(self):
        return self.CarPose
    
    @property
    def CarPose(self):
        with self.__CarPoseLock:
            CarPose = self._CarPose
        return CarPose
    @CarPose.setter
    def CarPose(self, newData):
        with self.__CarPoseLock:
            self._CarPose = newData