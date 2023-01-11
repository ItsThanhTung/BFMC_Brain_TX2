from src.utils.utils_function import MoveDistance, setAngle
from src.hardware.serialhandler.SerialHandlerProcess import SerialHandlerProcess
from multiprocessing import Pipe, Process, Event 

rcShR, rcShS   = Pipe(duplex = False)                                               # laneKeeping  ->  Serial


shProc = SerialHandlerProcess([rcShR], [])

allProcesses = [shProc]

print("Starting the processes!",allProcesses)
for proc in allProcesses:
    proc.daemon = True
    proc.start()

while True:
    angle = float(input("Please enter angle: "))
    Distance = int(input("Please enter distance: "))

    setAngle(rcShS , angle)
    MoveDistance(rcShS , Distance, 0.5)
