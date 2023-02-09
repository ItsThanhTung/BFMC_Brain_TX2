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
from src.perception.DecisionMakingProcess import DecisionMakingProcess
from src.image_processing.InterceptDetectionProcess import InterceptDetectionProcess
from src.image_processing.ObjectDetectionProcess import ObjectDetectionProcess

# opt import
from src.utils.utils_function import load_config_file
import torch

torch.multiprocessing.set_start_method('spawn', force=True)
if __name__ == '__main__':
    opt = load_config_file("main_remote.json")
    # =============================== CONFIG =================================================
    enableCameraSpoof   =  True 

    # =============================== INITIALIZING PROCESSES =================================
    allProcesses = list()

    # =============================== HARDWARE ===============================================
    camLaneStR, camLaneStS = Pipe(duplex = False)           # camera  ->  streamer
    camObjectStR, camObjectStS = Pipe(duplex = False)           # camera  ->  streamer
    if enableCameraSpoof:
        # camProc = CameraProcess([],[camStS], opt["CAM_PATH"])
        camProc = CameraSpooferProcess([], {"PREPROCESS_IMAGE" : camLaneStS, "OBJECT_IMAGE" : camObjectStS}, [opt["CAM_PATH"]])
        allProcesses.append(camProc)

    else:
        camProc = CameraReceiverProcess([],[camLaneStS])
        allProcesses.append(camProc)
    

    imagePreprocessShowR, imagePreprocessShowS = Pipe(duplex = False)                   # preprocess          ->  ImageShow
    imagePreprocessR, imagePreprocessS = Pipe(duplex = False)                           # preprocess          ->  LaneKeeping
    imagePreprocessInterceptR, imagePreprocessInterceptS = Pipe(duplex = False)         # preprocess          ->  Intercept detection

    laneDebugR, laneDebugS = Pipe(duplex = False)                                       # laneKeeping         ->  LaneDebug
    laneKeepingDecisionR, laneKeepingDecisionS = Pipe(duplex = False)                   # lane keeping        ->  Decision making

    laneDebugShowR, laneDebugShowS = Pipe(duplex = False)                               # laneDebug           ->  ImageShow
    interceptDecisionR, interceptDecisionS = Pipe(duplex = False)                       # Intercept detection ->  Decision making
    interceptDecisionDebugR, interceptDecisionDebugS = Pipe(duplex = False)             # Intercept detection ->  LaneDebug

    imageObjectShowR, imageObjectShowS = Pipe(duplex = False)                           # object detection    ->  ImageShow
    objectDecisionR, objectDecisionS = Pipe(duplex = False)                             # object detection    ->  Decision making

    objectDetectionProcess = ObjectDetectionProcess({"OBJECT_IMAGE" : camObjectStR}, {"IMAGE_SHOW" : imageObjectShowS, "DECISION_MAKING" : objectDecisionS}, True)

    imagePreprocess = ImagePreprocessingProcess({"LANE_IMAGE" : camLaneStR}, {"IMAGE_SHOW" : imagePreprocessShowS, "LANE_KEEPING" : imagePreprocessS, \
                                                        "INTERCEPT_DETECTION" : imagePreprocessInterceptS}, opt, True)
    laneKeepingProcess = LaneKeepingProcess([imagePreprocessR], [laneKeepingDecisionS], opt, laneDebugS, debug=True)

    decisionMakingProcess = DecisionMakingProcess({"LANE_KEEPING" : laneKeepingDecisionR, "INTERCEPT_DETECTION" : interceptDecisionR, \
                                                                "OBJECT_DETECTION" : objectDecisionR}, [], opt, debug=True)

    interceptDetectionProcess = InterceptDetectionProcess({"IMAGE_PREPROCESSING" : imagePreprocessInterceptR}, {"DECISION_MAKING" : interceptDecisionS}, \
                                                            opt, debugP = interceptDecisionDebugS, debug=True)


    laneDebugProcess = LaneDebuginggProcess({"LANE_KEEPING" : laneDebugR, "INTERCEPT_DETECTION" : interceptDecisionDebugR}, [laneDebugShowS])

    imageShow = imageShowProcess([imagePreprocessShowR, laneDebugShowR, imageObjectShowR], [])
    

    allProcesses.append(imagePreprocess)
    allProcesses.append(laneKeepingProcess)
    allProcesses.append(laneDebugProcess)
    allProcesses.append(imageShow)
    allProcesses.append(decisionMakingProcess)
    allProcesses.append(interceptDetectionProcess)
    allProcesses.append(objectDetectionProcess)



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
