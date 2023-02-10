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

from multiprocessing import Pipe, Process, Event 

# hardware imports
from src.hardware.camera.CameraProcess                      import CameraProcess
from src.hardware.serialhandler.SerialHandlerProcess        import SerialHandlerProcess

# utility imports
from src.utils.camerastreamer.CameraStreamerProcess         import CameraStreamerProcess


# lane keeping imports
from src.image_processing.LaneKeepingProcess import LaneKeepingProcess
from src.image_processing.ImagePreprocessingProcess import ImagePreprocessingProcess
from src.perception.DecisionMakingProcess import DecisionMakingProcess

from src.image_processing.InterceptDetectionProcess import InterceptDetectionProcess

from src.utils.utils_function import load_config_file

from src.image_processing.traffic_sign.detection import Yolo
import multiprocessing

if __name__ == '__main__':
    # =========================== Object Detection ===========================================
    object_detector = Yolo(True)
    object_image_queue = multiprocessing.Queue(maxsize=3)
    object_condition = multiprocessing.Condition()

    # =============================== CONFIG =================================================
    enableStream        =  False
    enableRc            =  False

    opt = load_config_file("main_rc.json")

    # =============================== INITIALIZING PROCESSES =================================
    allProcesses = list()

    # =============================== HARDWARE ===============================================
    camLaneStR, camLaneStS = Pipe(duplex = False)           # camera  ->  streamer
    camObjectStR, camObjectStS = Pipe(duplex = False)           # camera  ->  streamer
    camProc = CameraProcess(object_image_queue, object_condition, \
                            [],{"PREPROCESS_IMAGE" : camLaneStS, "OBJECT_IMAGE" : camObjectStS}, opt["CAM_PATH"])
    allProcesses.append(camProc)

    
    rcShR, rcShS   = Pipe(duplex = False)                                               # laneKeeping  ->  Serial
    distSerialR, distSerialS  = Pipe(duplex = False)                                    # laneKeeping  ->  Serial

    imagePreprocessR, imagePreprocessS = Pipe(duplex = False)                           # preprocess   ->  LaneKeeping
    imagePreprocessStreamR, imagePreprocessStreamS = Pipe(duplex = False)               # preprocess   ->  Stream
    imagePreprocessInterceptR, imagePreprocessInterceptS = Pipe(duplex = False)         # preprocess   ->  Intercept detection

    laneKeepingDecisionR, laneKeepingDecisionS = Pipe(duplex = False)                   # lane keeping ->  Decision making

    interceptDecisionR, interceptDecisionS = Pipe(duplex = False)                       # Intercept detection ->  Decision making

    objectDecisionR, objectDecisionS = Pipe(duplex = False)                             # object detection    ->  Decision making
    # Serial Handler Pipe Connection SerialHandler -> Decision ACK
    shSetSpdR, shSetSpdS = Pipe(duplex= False)
    shSteerR, shSteerS = Pipe(duplex= False)
    shEnPIDR, shEnPIDS = Pipe(duplex= False)
    shGetSpdR, shGetSpdS = Pipe(duplex= False)
    shDistR, shDistS = Pipe(duplex= False)
    shInps = {
        "SETSPEED": shSetSpdR,
        "STEER": shSteerR,
        "ENPID": shEnPIDR,
        "GETSPEED": shGetSpdR,
        "DIST": shDistR
    }



    # objectDetectionProcess = ObjectDetectionProcess({"OBJECT_IMAGE" : camObjectStR}, {"DECISION_MAKING" : objectDecisionS})
    imagePreprocess = ImagePreprocessingProcess({"LANE_IMAGE" : camLaneStR}, {"LANE_KEEPING" : imagePreprocessS, "INTERCEPT_DETECTION" : imagePreprocessInterceptS},\
                                                                opt , False, imagePreprocessStreamS, enableStream)
                                             
    laneKeepingProcess = LaneKeepingProcess([imagePreprocessR], [laneKeepingDecisionS], opt, None, False)
    decisionMakingProcess = DecisionMakingProcess({"LANE_KEEPING" : laneKeepingDecisionR, "INTERCEPT_DETECTION" : interceptDecisionR, "OBJECT_DETECTION" : objectDecisionR}, \
                                                                                                    {"SERIAL" : rcShS, "SERIAL_DISTANCE": distSerialR}, shInps, opt, debug=False)


    interceptDetectionProcess = InterceptDetectionProcess({"IMAGE_PREPROCESSING" : imagePreprocessInterceptR}, {"DECISION_MAKING" : interceptDecisionS}, \
                                                            opt, debugP=None, debug=False)           

    #SerialHandler Process
    shOutPs = {
        "1": shSetSpdS,
        "2": shSteerS,
        "4": shEnPIDS, 
        "5": shGetSpdS,
        "7": shDistS
    }

    shProc = SerialHandlerProcess([rcShR], shOutPs)
    
    allProcesses.append(imagePreprocess)
    allProcesses.append(laneKeepingProcess)
    allProcesses.append(decisionMakingProcess)
    allProcesses.append(interceptDetectionProcess)
    allProcesses.append(shProc)


    if enableStream:
        streamProc = CameraStreamerProcess([imagePreprocessStreamR], [], opt["IP_ADDRESS"])
        allProcesses.append(streamProc)



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
    
    object_detector.detection_loop(object_image_queue, object_condition, \
                            objectDecisionS, False, None)

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
