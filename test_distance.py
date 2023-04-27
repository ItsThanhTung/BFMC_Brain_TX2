from src.utils.utils_function import MoveDistance, setAngle, EnablePID, GetDistanceStatus, setSpeed
from src.hardware.serialhandler.SerialHandlerProcess import SerialHandlerProcess
from multiprocessing import Pipe, Process, Event 
import time


if __name__ == '__main__':

    rcShR, rcShS = Pipe(duplex = False)                                               # laneKeeping  ->  Serial
    DistR, DistS = Pipe (duplex = False)     #Pipe Rcv Runned Data

    shProc = SerialHandlerProcess([rcShR], {})

    allProcesses = [shProc]

    shProc.SubscribeTopic('7', [DistS])

    print("Starting the processes!",allProcesses)
    for proc in allProcesses:
        proc.daemon = True
        proc.start()

    # time.sleep(0.05)

    setSpeed(rcShS,0)
    time.sleep(0.05)
    setSpeed(rcShS,0)
    time.sleep(0.05)
    setSpeed(rcShS,0)
    # EnablePID(rcShS)
    # setAngle(rcShS , 0)
    # time.sleep(1)
