from src.templates.threadwithstop import ThreadWithStop
from multiprocessing.connection import wait
class CarHandlerThread(ThreadWithStop):
    def __init__(self, shInPs, shOutP, enablePID = True, AckTimeout = 0.1, sendAttempTimes:int = 2):
        """
    
    Car Handler Thread object

    Parameters
    -------------

    shInPs: Connection Serial Input Pipes List
    type: Connection InPipe Lists
    values: Pipes of action 1,2,4,5,7

    shOutP: SerialHandler OutPipe
    values: Connection OutPipe

    enablePID: Enbale PID control of Speed
    values: Bool

    AckTimeout: Time wait for Ack Command
    values: if None wait forever. Other number wait time in second
    
    sendAttempTimes: Attemp to send when not receive Ack or receive error
    values: int, minimum attemp times = 1
    """
        super(CarHandlerThread,self).__init__()
        self.__shOutP = shOutP
        self.__shInPs = shInPs
        self.__AckTimeout = AckTimeout
        self.__RunnedDistance = 0
        self.__CurrentState = 0
        if sendAttempTimes < 0:
            self.__sendAttemp = 1
        else:
            self.__sendAttemp = sendAttempTimes
        
        if enablePID: 
            self.enablePID()
        else:
            self.enablePID(False)


    
    def run(self):
        readers=[]
        readers.append(self.__shInPs["DIST"])
        readers.append(self.__shInPs["GETSPEED"])
        while(self._running):
            for inP in wait(readers):
                try:
                    mess = inP.recv()
                except:
                    print("Pipe Error ", inP)
                else:
                    if mess["action"] == "7":
                        print(mess["data"])
                    elif mess["action"] == "5":
                        print(mess["data"])
    
    def enablePID(self, Enable = True):
        data = {
        "action": '4',
        "activate": Enable
        }
        Status = 0
        Mess = {
            "data":"OK"
        }
        for i in range(self.__sendAttemp):
            self._shSend(self.__shOutP, data)
            if self.__AckTimeout < 0:
                return 0, "OK"

            Status, Mess = self._shRecv(self.__shInPs["ENPID"])
            if Status == 0:
                if Mess == "ack;;":
                    return 0, "OK"
        return Status, Mess["data"]

    def _shSend(self, outP, Data):
        outP.send(Data)

    def _shRecv(self, inP, timeout = 0.1):
        if inP.poll(timeout) :
            Data = inP.recv()
            return 0, Data
        else:
            return -1, {"data":"Receive Timeout"}

    def setSpeed(self, speed):
        data = {
        "action": '1',
        "speed": float(speed/100)
        }
        Status = 0
        Mess = {
            "data":"OK"
        }
        for i in range(self.__sendAttemp):
            self._shSend(self.__shOutP, data)
            if self.__AckTimeout < 0:
                return 0, "OK"

            Status, Mess = self._shRecv(self.__shInPs["SETSPEED"])
            if Status == 0:
                if Mess["data"] == "ack;;":
                    return 0, "OK"

        return Status, Mess["data"]
            
    def setAngle(self, value):
        value = 0
        data = {
        "action": '2',
        "steerAngle": float(value)
        }
        Status = 0
        Mess = {
            "data":"OK"
        }
        for i in range(self.__sendAttemp):
            self._shSend(self.__shOutP, data)
            if self.__AckTimeout < 0:
                return 0, "OK"

            Status, Mess = self._shRecv(self.__shInPs["STEER"])
            if Status == 0:
                if Mess["data"] == "ack;;":
                    return 0, "OK"
        return Status, Mess["data"]

    def moveDistance(self, distance, speed):
        data = {
        "action": '7',
        "distance": distance,
        "speed": speed
        }
        Status = 0
        Mess = {
            "data":"OK"
        }
        for i in range(self.__sendAttemp):
            self._shSend(self.__shOutP, data)
            if self.__AckTimeout < 0:
                return 0, "OK"

            Status, Mess = self._shRecv(self.__shInPs["STEER"])
            if Status == 0:
                if Mess["data"] == "ack;;":
                    return 0, "OK"
        return Status, Mess["data"]

    def getDistanceStatus(self):
        return self.__RunnedDistance

    def getSpeed(self):
        return self.__CurrentSpeed

    