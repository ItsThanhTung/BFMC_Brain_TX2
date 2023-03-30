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
from src.data.localisationssystem.LocalizeDebugProcess import LocalizeDebugProcess
# opt import
from src.utils.utils_function import load_config_file

# object detection import
# from src.image_processing.traffic_sign_remote.detection import Yolo
import multiprocessing
from threading import Thread


if __name__ == '__main__':
    
    # =========================== Object Detection ===========================================
    camObjectStR, camObjectStS = Pipe(duplex = False)                                   # camera  ->  streamer
    imageObjectShowR, imageObjectShowS = Pipe(duplex = False)                           # object detection    ->  ImageShow
    # object_detector = Yolo(camObjectStR, imageObjectShowS, False)

    is_remote = False
    is_show = False
    
    
    opt = load_config_file("main_rc.json")
    cam_opt = opt["REMOTE"] if is_remote else opt["RC"]
    
    # =============================== CONFIG =================================================
    enableCameraSpoof   =  False 
    enableLocalizeStream = False
    # =============================== INITIALIZING PROCESSES =================================
    allProcesses = list()

    # =============================== HARDWARE ===============================================
    camLaneStR, camLaneStS = Pipe(duplex = False)           # camera  ->  streamer
    
    
    if enableCameraSpoof:
        # camProc = CameraProcess(object_image_queue, object_condition, \
        #                     [],{"PREPROCESS_IMAGE" : camLaneStS, "OBJECT_IMAGE" : camObjectStS}, opt["CAM_PATH"])
        camProc = CameraSpooferProcess([], {"PREPROCESS_IMAGE" : camLaneStS, "OBJECT_IMAGE" : camObjectStS}, [opt["CAM_PATH"]])
        allProcesses.append(camProc)

    else:
        camProc = CameraReceiverProcess([],[camLaneStS], (240, 320, 3), 2244)
        camObjectProc = CameraReceiverProcess([],[camObjectStS], (480, 640, 3), 2233)
        allProcesses.append(camProc)
        allProcesses.append(camObjectProc)
    
    if enableLocalizeStream:
        localizeDebugR, localizeDebugS = Pipe(duplex = False)                                       # laneKeeping         ->  LaneDebug
        dataLocalizeProc = DataReceiverProcess([], [localizeDebugS], port=2277)
        localizeDebugProcR, localizeDebugProcS = Pipe(duplex = False)                               # laneDebug           ->  ImageShow
        localizeDebugProc = LocalizeDebugProcess([localizeDebugR], [localizeDebugProcS])
        allProcesses.append(dataLocalizeProc)
    else:
        localizeDebugR, localizeDebugS = None, None
        localizeDebugProcR, localizeDebugProcS = None, None
    imagePreprocessShowR, imagePreprocessShowS = Pipe(duplex = False)                   # preprocess          ->  ImageShow
    imagePreprocessR, imagePreprocessS = Pipe(duplex = False)                           # preprocess          ->  LaneKeeping
    imagePreprocessInterceptR, imagePreprocessInterceptS = Pipe(duplex = False)         # preprocess          ->  Intercept detection

    laneDebugR, laneDebugS = Pipe(duplex = False)                                       # laneKeeping         ->  LaneDebug

    laneDebugShowR, laneDebugShowS = Pipe(duplex = False)                               # laneDebug           ->  ImageShow
    interceptDebugShowR, interceptDebugShowS = Pipe(duplex = False)                               # laneDebug           ->  ImageShow
    
    interceptDecisionDebugR, interceptDecisionDebugS = Pipe(duplex = False)             # Intercept detection ->  LaneDebug


    # imagePreprocess = ImagePreprocessingProcess({"LANE_IMAGE" : camLaneStR}, {"IMAGE_SHOW" : imagePreprocessShowS, "LANE_KEEPING" : imagePreprocessS, \
    #                                                     "INTERCEPT_DETECTION" : imagePreprocessInterceptS}, opt, is_show=is_show)
    # laneKeepingProcess = LaneKeepingProcess([imagePreprocessR], [None], opt, laneDebugS, debug=True, is_remote=is_remote)

    # interceptDetectionProcess = InterceptDetectionProcess({"IMAGE_PREPROCESSING" : imagePreprocessInterceptR}, {}, \
    #                                                         opt, debugP = interceptDecisionDebugS, debug=True, is_remote=is_remote)

    # laneDebugProcess = LaneDebuginggProcess({"LANE_KEEPING" : laneDebugR, "INTERCEPT_DETECTION" : interceptDecisionDebugR}, \
    #                                     {"LANE_KEEPING" :laneDebugShowS, "INTERCEPT_DETECTION" :interceptDebugShowS}, )

    # imageShow = imageShowProcess([imagePreprocessShowR, laneDebugShowR, interceptDebugShowR, imageObjectShowR], [])
    

    # allProcesses.append(imagePreprocess)
    # allProcesses.append(laneKeepingProcess)
    # allProcesses.append(laneDebugProcess)
    # allProcesses.append(imageShow)
    # allProcesses.append(interceptDetectionProcess)
 
 
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
  
    object_cam_read_th = Thread(target = object_detector.read_image)
    object_detector_th = Thread(target = object_detector.detection_loop)
    
    object_cam_read_th.start()
    object_detector_th.start()
    
    try:
        blocker.wait()

    except KeyboardInterrupt:
        print("\nCatching a KeyboardInterruption exception! Shutdown all processes.\n")
        for proc in allProcesses:
            if hasattr(proc,'stop') and callable(getattr(proc,'stop')):
                print("Process with stop",proc)
                proc.stop()
                proc.join()
                object_cam_read_th.join()
                object_detector_th.join()
            else:
                print("Process witouth stop",proc)
                proc.terminate()
                proc.join()
                object_cam_read_th.join()
                object_detector_th.join()


    
