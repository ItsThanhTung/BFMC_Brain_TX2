# Copyright (c) 2019, Bosch Engineering Center Cluj and BFMC orginazers
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
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#========================================================================
# SCRIPT USED FOR WIRING ALL COMPONENTS
#========================================================================
import sys
sys.path.append('.')

import time
import signal
from multiprocessing import Pipe, Process, Event 

# hardware imports
from src.hardware.camera.CameraProcess                      import CameraProcess
from src.hardware.camera.CameraSpooferProcess               import CameraSpooferProcess
from src.utils.camerastreamer.CameraReceiverProcess         import CameraReceiverProcess

# utility imports
from src.utils.camerastreamer.CameraStreamerProcess         import CameraStreamerProcess


# lane keeping imports
from src.image_processing.LaneKeepingProcess import LaneKeepingProcess
from src.image_processing.imageShowProcess import imageShowProcess
from src.image_processing.ImagePreprocessingProcess import ImagePreprocessingProcess
from src.image_processing.LaneDebuggingProcess import LaneDebuginggProcess
# from src.perception.DecisionMakingProcess import DecisionMakingProcess
from src.image_processing.InterceptDetectionProcess import InterceptDetectionProcess
from src.utils.datastreamer.DataReceiverProcess import DataReceiverProcess

# opt import
from src.utils.utils_function import load_config_file

# object detection import
from src.image_processing.traffic_sign.detection import Yolo
import multiprocessing

# def detection(camObjectStR,detector):
#     print("loading.......................................")
    
    
#     while True:
#         with c_object:
#             c_object.wait()
#         with c_object:
#             while object_image.qsize()>0:
#                 image=object_image.get()
#                 _= detector.detect(image)
#                 # print(".",image.shape)  


if __name__ == '__main__':
    
    enableStream             =  True
    enableLaneStream         =  True
    enableInterceptStream    =  True


    # =============================== INITIALIZING PROCESSES =================================
    allProcesses = list()

    # =============================== HARDWARE ===============================================


    if enableStream:
        camLaneStR, camLaneStS = Pipe(duplex = False)                                       # camera  ->  streamer
        camProc = CameraReceiverProcess([],[camLaneStS])
        allProcesses.append(camProc)
    else:
        camLaneStR, camLaneStS = None, None
    
    if enableLaneStream:
        laneDebugR, laneDebugS = Pipe(duplex = False)                                       # laneKeeping         ->  LaneDebug
        dataLaneProc = DataReceiverProcess([], [laneDebugS], port=2255)
        laneDebugShowR, laneDebugShowS = Pipe(duplex = False)                               # laneDebug           ->  ImageShow
        allProcesses.append(dataLaneProc)
    else:
        laneDebugR, laneDebugS = None, None
        laneDebugShowR, laneDebugShowS = None, None
    
    if enableInterceptStream:
        interceptDebugR, interceptDebugS = Pipe(duplex = False)                             # laneKeeping         ->  LaneDebug
        dataInterceptProc = DataReceiverProcess([], [interceptDebugS], port=2266)
        interceptDebugShowR, interceptDebugShowS = Pipe(duplex = False)                               # laneDebug           ->  ImageShow
        allProcesses.append(dataInterceptProc)
    else:
        interceptDebugR, interceptDebugS = None, None
        interceptDebugShowR, interceptDebugShowS = None, None

    
    laneDebugProcess = LaneDebuginggProcess({"LANE_KEEPING" : laneDebugR, "INTERCEPT_DETECTION" : interceptDebugR},\
                                                {"LANE_KEEPING": laneDebugShowS, "INTERCEPT_DETECTION" : interceptDebugShowS})
    
    imageShow = imageShowProcess([camLaneStR, laneDebugShowR, interceptDebugShowR], [])
    
    allProcesses.append(imageShow)
    allProcesses.append(laneDebugProcess)

 
    # =============================== DATA ===================================================
    #LocSys client process
    # LocStR, LocStS = Pipe(duplex = False)           # LocSys  ->  brain
    # from data.localisationsystem.locsys import LocalisationSystemProcess
    # LocSysProc = LocalisationSystemProcess([], [LocStS])
    # allProcesses.append(LocSysProc)



    # ===================================== START PROCESSES ==================================
    print("Starting the processes!",allProcesses)
    for proc in allProcesses:
        proc.daemon = True
        proc.start()


    # ===================================== STAYING ALIVE ====================================
    blocker = Event()  

    try:
        blocker.wait()

    except KeyboardInterrupt:
        print("\nCatching a KeyboardInterruption exception! Shutdown all processes.\n")
        for proc in allProcesses:
            if hasattr(proc,'stop') and callable(getattr(proc,'stop')):
                print("Process with stop",proc)
                proc.stop()
                proc.join()
            else:
                print("Process witouth stop",proc)
                proc.terminate()
                proc.join()

    
