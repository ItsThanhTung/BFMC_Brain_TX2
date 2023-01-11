from src.utils.utils_function import MoveDistance, setAngle, EnablePID
from src.hardware.serialhandler.SerialHandlerProcess import SerialHandlerProcess
from multiprocessing import Pipe, Process, Event 
import time
rcShR, rcShS   = Pipe(duplex = False)                                               # laneKeeping  ->  Serial


shProc = SerialHandlerProcess([rcShR], [])

allProcesses = [shProc]

print("Starting the processes!",allProcesses)
for proc in allProcesses:
    proc.daemon = True
    proc.start()

EnablePID(rcShS)
time.sleep(0.05)
setAngle(rcShS , float(-3-6))
time.sleep(0.1)
MoveDistance(rcShS , 0.07, 0.5)
time.sleep(1)

setAngle(rcShS , float(23-6))
time.sleep(0.05)
MoveDistance(rcShS , 0.8, 0.5)
time.sleep(5)
# while True:
#     # angle = float(input("Please enter angle: "))
#     Distance = float(input("Please enter distance: "))

#     # setAngle(rcShS , angle)
#     # time.sleep(0.5)
#     setAngle(rcShS , float(23-6))
#     MoveDistance(rcShS , Distance, 0.5)
