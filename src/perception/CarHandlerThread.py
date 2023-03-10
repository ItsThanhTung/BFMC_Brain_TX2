from src.templates.threadwithstop import ThreadWithStop
from multiprocessing.connection import wait
from threading import Lock
class CarHandlerThread(ThreadWithStop):
    def __init__(self, shInPs, shOutP, enablePID = True, AckTimeout = 0.05, sendAttempTimes:int = 2):
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
        self.__DistanceMess = 0
        self.__DistanceStatus = 0
        self.__DistanceLock = Lock()
        self.__CurrentState = 0
        if sendAttempTimes < 0:
            self.__sendAttemp = 1
        else:
            self.__sendAttemp = sendAttempTimes
        
        
        self.enablePID(enablePID)

        self.enListenVLX(False)
        self.enListenSpeed(False)
        self.enListenTravelled(False)
        

    
    def run(self):
        readers=[]
        readers.append(self.__shInPs["DIST"])
        while(self._running):
            for inP in wait(readers):
                try:
                    mess = inP.recv()
                    if mess['action'] =='7':
                        # print("Car Handler Mess", mess)
                        self._distanceProcess(mess['data'])
                except:
                    print("Pipe Error ", inP)

    def _distanceProcess(self, Data):
        self.__DistanceLock.acquire()
        try:
            self.__DistanceStatus, self.__DistanceMess = Data.split(";", 2)[:2]
        except:
            print("Split Error")
        self.__DistanceLock.release()
        
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

    def setSpeed(self, speed, send_attempt=None):
        if send_attempt is None:
            send_attempt = self.__sendAttemp 
            
        data = {
        "action": '1',
        "speed": float(speed/100)
        }
        Status = 0
        Mess = {
            "data":"OK"
        }
        for i in range(send_attempt):
            self._shSend(self.__shOutP, data)
            if self.__AckTimeout < 0:
                return 0, "OK"

            Status, Mess = self._shRecv(self.__shInPs["SETSPEED"])
            if Status == 0:
                if Mess["data"] == "ack;;":
                    return 0, "OK"

        return Status, Mess["data"]
            
    def setAngle(self, value, send_attempt=None):
        if send_attempt is None:
            send_attempt = self.__sendAttemp 
        # return 0, "OK"
        data = {
        "action": '2',
        "steerAngle": float(value)
        }
        Status = 0
        Mess = {
            "data":"OK"
        }
        for i in range(send_attempt):
            self._shSend(self.__shOutP, data)
            if self.__AckTimeout < 0:
                return 0, "OK"

            Status, Mess = self._shRecv(self.__shInPs["STEER"])
            if Status == 0:
                if Mess["data"] == "ack;;":
                    return 0, "OK"
        return Status, Mess["data"]

    def moveDistance(self, distance, speed, send_attempt = None):
        if send_attempt is None:
            send_attempt = self.__sendAttemp 
        data = {
        "action": '7',
        "distance": float(distance/100),
        "speed": float(speed/100)
        }
        Status = 0
        Mess = {
            "data":"OK"
        }
        # print("sh Pipe ", self.__shOutP)
        self._shSend(self.__shOutP, data)
        return 0, "OK"

            

    def getDistanceStatus(self):
        self.__DistanceLock.acquire()
        Status, mess = int(self.__DistanceStatus), self.__DistanceMess
        self.__DistanceLock.release()
        return Status, mess

    def getSpeed(self):
        return self.__CurrentSpeed

    def enListenTravelled(self, Enable = True):
        data = {
        "action": '9',
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

    def enListenVLX(self, Enable = True):
        data = {
        "action": '8',
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

    def enListenSpeed(self, Enable = True):
        data = {
        "action": '5',
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

    