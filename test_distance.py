from src.utils.utils_function import MoveDistance, setAngle, EnablePID, GetDistanceStatus
from src.hardware.serialhandler.SerialHandlerProcess import SerialHandlerProcess
from multiprocessing import Pipe, Process, Event 
import time
rcShR, rcShS = Pipe(duplex = False)                                               # laneKeeping  ->  Serial
DistR, DistS = Pipe (duplex = False)     #Pipe Rcv Runned Data

shProc = SerialHandlerProcess([rcShR], [])

allProcesses = [shProc]

shProc.SubscribeTopic('7', DistS)

print("Starting the processes!",allProcesses)
for proc in allProcesses:
    proc.daemon = True
    proc.start()

time.sleep(1)


EnablePID(rcShS)
# time.sleep(0.05)
# setAngle(rcShS , float(-3-6))
# time.sleep(0.1)
# MoveDistance(rcShS , 0.07, 0.5)
# time.sleep(1)

# setAngle(rcShS , float(23-6))
# time.sleep(0.05)
# MoveDistance(rcShS , 0.8, 0.5)
# time.sleep(5)
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
