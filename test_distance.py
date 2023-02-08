from src.utils.utils_function import MoveDistance, setAngle, EnablePID, GetDistanceStatus
from src.hardware.serialhandler.SerialHandlerProcess import SerialHandlerProcess
from multiprocessing import Pipe, Process, Event 
import time


if __name__ == '__main__':

    rcShR, rcShS = Pipe(duplex = False)                                               # laneKeeping  ->  Serial
    DistR, DistS = Pipe (duplex = False)     #Pipe Rcv Runned Data

    shProc = SerialHandlerProcess([rcShR], [])

    allProcesses = [shProc]

    shProc.SubscribeTopic('7', DistS)

    print("Starting the processes!",allProcesses)
    for proc in allProcesses:
        proc.daemon = True
        proc.start()

    time.sleep(5)

    EnablePID(rcShS)
    while True:
        angle = float(input("Please enter angle: "))
        Distance = float(input("Please enter distance: "))

        setAngle(rcShS , angle)
        time.sleep(0.05)
        MoveDistance(rcShS , Distance, 0.5)
        
        while True:
            Status, message = GetDistanceStatus(DistR)
            print("Status ", Status)
            print("Message ", message)
            if(Status == 2) : 
                break


