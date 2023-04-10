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
from src.hardware.NucleoListener.NucleoProcess              import NucleoProcess

from src.hardware.data_fusion.CarEstimateProcess import CarEstimateProcess

# V2X Listener
from src.data.localisationssystem.locsys                    import LocalisationSystem

# utility imports
from src.utils.camerastreamer.CameraStreamerProcess         import CameraStreamerProcess


# lane keeping imports
from src.image_processing.LaneKeepingProcess import LaneKeepingProcess
from src.image_processing.ImagePreprocessingProcess import ImagePreprocessingProcess
from src.perception.DecisionMakingProcess import DecisionMakingProcess
from src.utils.datastreamer.DataStreamerProcess import DataStreamerProcess
from src.image_processing.InterceptDetectionProcess import InterceptDetectionProcess
from src.data.localisationssystem.LocalizeProcess import LocalizeProcess
from src.utils.utils_function import load_config_file

from src.image_processing.traffic_sign.detection import Yolo
import multiprocessing
from threading import Thread

if __name__ == '__main__':
    
    # =============================== CONFIG =================================================
    enableStream             =  False
    enableLocalize           = True
    enableYolo              = False

    enableStreamObject       =  False
    enableLaneStream         =  False
    enableInterceptStream    =  False
    enableLocalizeStream       = True
    
    is_remote = False
    is_show = False
    is_stop = False
    
    opt = load_config_file("main_rc.json")
    cam_opt = opt["REMOTE"] if is_remote else opt["RC"]
    allProcesses = list()
    # =========================== Object Detection ===========================================
    camObjectStR, camObjectStS = None, None
    objectDecisionR, objectDecisionS = Pipe(duplex = False)                             # object detection    ->  Decision making
    
    camLaneStR, camLaneStS = Pipe(duplex = False)           # camera  ->  streamer
        
    if enableYolo:        
        camObjectStR, camObjectStS = Pipe(duplex = False)                                   # camera  ->  streamer
        
        if enableStreamObject:
            objectDebugStreamR, objectDebugStreamS = Pipe(duplex = False)    
        else:    
            objectDebugStreamR, objectDebugStreamS = None, None
        
        object_detector = Yolo(camObjectStR, objectDecisionS, objectDebugStreamS, \
                                debug=enableStreamObject, is_tensorRt = not is_remote)
    
    cameraSendP = {"PREPROCESS_IMAGE" : camLaneStS, "OBJECT_IMAGE" : camObjectStS}
    
    camProc = CameraProcess([], cameraSendP, cam_opt["CAM_PATH"])
    allProcesses.append(camProc)

        
    

    # =============================== INITIALIZING PROCESSES =================================
    

    # =============================== HARDWARE ===============================================
    
    
    LocStR, LocStS = Pipe(duplex = False)           # LocSys  ->  brain

    rcShR, rcShS   = Pipe(duplex = False)                                               # laneKeeping  ->  Serial

    imagePreprocessR, imagePreprocessS = Pipe(duplex = False)                           # preprocess   ->  LaneKeeping
    
    imagePreprocessInterceptR, imagePreprocessInterceptS = Pipe(duplex = False)         # preprocess   ->  Intercept detection

    laneKeepingDecisionR, laneKeepingDecisionS = Pipe(duplex = False)                   # lane keeping ->  Decision making

    interceptDecisionR, interceptDecisionS = Pipe(duplex = False)                       # Intercept detection ->  Decision making

    
    # Serial Handler Pipe Connection SerialHandler -> Decision ACK
    shSetSpdR, shSetSpdS = Pipe(duplex= False)
    shSteerR, shSteerS = Pipe(duplex= False)
    shEnPIDR, shEnPIDS = Pipe(duplex= False)
    shGetSpdR, shGetSpdS = Pipe(duplex= False)
    shDistR, shDistS = Pipe(duplex= False)

    # Serial Handler Pipe -> Nucleo Listener
    VLXListenerR, VLXListenerS = Pipe(duplex = False)
    encSpeedListenerR, encSpeedListenerS = Pipe(duplex = False)
    encTravelledListenerR, encTravelledListenerS = Pipe(duplex = False)

    # Nucleo Speed, Travelled Listner -> Data Fusion
    SpeedR, SpeedS = Pipe(duplex = False)
    TravelledR, TravelledS = Pipe(duplex = False)

    #IMU -> Data Fusion
    IMUDataR, IMUDataS = Pipe(duplex = False)

    # Set Speed Steer from DM -> Car Estimate Predict State
    SetStateR, SetStateS = Pipe(duplex = False)

    # VLX sensor Data -> ?
    VLXDataR, VLXDataS = Pipe(duplex = False)
    
    if enableStream:
        imagePreprocessStreamR, imagePreprocessStreamS = Pipe(duplex = False)               # preprocess   ->  Stream
    else:
        imagePreprocessStreamR, imagePreprocessStreamS = None, None
        
    if enableLaneStream:
        laneKeepingDebugR, laneKeepingDebugS = Pipe(duplex = False)                         # lane keeping ->  Decision making
    else:
        laneKeepingDebugR, laneKeepingDebugS = None, None
    
    if enableInterceptStream:
        interceptDebugR, interceptDebugS = Pipe(duplex = False)                             # lane keeping ->  Decision making
    else:
        interceptDebugR, interceptDebugS = None, None
        
        
    if enableLocalize:
        localizeDebugR, localizeDebugS = Pipe(duplex = False) 

        locSysR, locSysS = Pipe(duplex = False) 

        localizeProc = LocalizeProcess([locSysS],debugP=localizeDebugS,opt=opt ,debug=True)
        allProcesses.append(localizeProc)
    else:
        localizeDebugR, localizeDebugS = None, None
        localizeProc = None
    # =============================== Sensor Input Layer ===================================================
    
    # LocSys client process
    # LocsysOpt = opt["LOCSYS"]
    # LocSysProc = LocalisationSystem(LocsysOpt["LOCSYS_TAGID"], LocsysOpt["LOCSYS_BEACON"], LocsysOpt["PUBLIC_KEY"],LocStS)
    # allProcesses.append(LocSysProc)

    # NucListenerInPs ={
    #     "SPEED": encSpeedListenerR,
    #     "TRAVELLED": encTravelledListenerR,
    #     "VLX": VLXListenerR
    # }
    # NucOutPs = {
    #     "SPEED": SpeedS,
    #     "TRAVELLED": TravelledS,
    #     "VLX": VLXDataS,
    #     "IMU": IMUDataS
    # }
    # NucListenerProc = NucleoProcess(NucListenerInPs, NucOutPs)
    # allProcesses.append(NucListenerProc)


    # =============================== PreProcessing Layer ===================================================
    imagePreprocess = ImagePreprocessingProcess({"LANE_IMAGE" : camLaneStR}, {"LANE_KEEPING" : imagePreprocessS, "INTERCEPT_DETECTION" : imagePreprocessInterceptS},\
                                                                opt , is_show, debugP=imagePreprocessStreamS, debug=enableStream)
    allProcesses.append(imagePreprocess)

    laneKeepingProcess = LaneKeepingProcess([imagePreprocessR], [laneKeepingDecisionS], opt, debugP=laneKeepingDebugS, debug=enableLaneStream, is_remote=is_remote)
    allProcesses.append(laneKeepingProcess)

    interceptDetectionProcess = InterceptDetectionProcess({"IMAGE_PREPROCESSING" : imagePreprocessInterceptR}, {"DECISION_MAKING" : interceptDecisionS}, \
                                                            opt, debugP=interceptDebugS, debug=enableInterceptStream, is_remote=is_remote)           
    allProcesses.append(interceptDetectionProcess)


    CarEstimateInPs = {
        "GPS": locSysR,
        "IMU":  IMUDataR,
        "Encoder": SpeedR,
        "DM": SetStateR,
    }
    CarEstimateOutPs = {

    }
    CarEstimateProc = CarEstimateProcess(CarEstimateInPs, CarEstimateOutPs)
    allProcesses.append(CarEstimateProc)

    # =============================== Perception Layer ===================================================

    shInps = {                      #Inps for ack command
        "SETSPEED": shSetSpdR,
        "STEER": shSteerR,
        "ENPID": shEnPIDR,
        "GETSPEED": shGetSpdR,
        "DIST": shDistR,
        "TRAVELLED": TravelledR 
    }
    dmInps = {"LANE_KEEPING" : laneKeepingDecisionR, 
              "INTERCEPT_DETECTION" : interceptDecisionR, 
              "OBJECT_DETECTION" : objectDecisionR, 
            }
    
    dmOutPs = {
        "SERIAL" : rcShS,
        "StateEstimate": SetStateS
    }
    if not is_remote:
        decisionMakingProcess = DecisionMakingProcess(dmInps, dmOutPs, shInps, opt, is_stop=is_stop)
        allProcesses.append(decisionMakingProcess)
        
    # SerialHandler Process
    

    # =============================== Actuator Output Layer ===================================================
    shOutPs = {
        "1": [shSetSpdS],
        "2": [shSteerS],
        "4": [shEnPIDS], 
        "5": [encSpeedListenerS],
        "7": [shDistS],
        "8": [VLXListenerS],
        "9": [encTravelledListenerS]
    }
    shProc = SerialHandlerProcess([rcShR], shOutPs)
    allProcesses.append(shProc)



    # =============================== Streamer Layer ===================================================
    if enableStream:
        streamProc = CameraStreamerProcess([imagePreprocessStreamR], [], cam_opt["IP_ADDRESS"], 2244)
        allProcesses.append(streamProc)
    
    if enableLaneStream:
        dataLaneStreamerProcess = DataStreamerProcess([laneKeepingDebugR], [], cam_opt["IP_ADDRESS"], 2255)
        allProcesses.append(dataLaneStreamerProcess)
    
    if enableInterceptStream:
        dataInterceptStreamerProcess = DataStreamerProcess([interceptDebugR], [], cam_opt["IP_ADDRESS"], 2266)
        allProcesses.append(dataInterceptStreamerProcess)
        
    if enableStreamObject:
        streamProc = CameraStreamerProcess([objectDebugStreamR], [], cam_opt["IP_ADDRESS"], 2233)
        allProcesses.append(streamProc)
        
    if enableLocalizeStream:
        dataLocalizeStreamerProcess = DataStreamerProcess([localizeDebugR], [], cam_opt["IP_ADDRESS"], 2277)
        allProcesses.append(dataLocalizeStreamerProcess)

    # ===================================== START PROCESSES ==================================
    print("Starting the processes!",allProcesses)
    for proc in allProcesses:
        proc.daemon = True
        proc.start()


    # ===================================== STAYING ALIVE ====================================
    blocker = Event()  
    if enableYolo:
        object_cam_read_th = Thread(target = object_detector.read_image)
        stream_image_th = Thread(target = object_detector.stream_image_th)
        object_detector_th = Thread(target = object_detector.detection_loop)
        
        object_cam_read_th.start()
        object_detector_th.start()
        stream_image_th.start()

    try:
        blocker.wait()
    except KeyboardInterrupt:
        print("\nCatching a KeyboardInterruption exception! Shutdown all processes.\n")
        if enableYolo:
            del object_cam_read_th  
            del object_detector_th  
            del stream_image_th
        
        decisionMakingProcess.stop()
        decisionMakingProcess.join()
        decisionMakingProcess.turn_off_rc_car()
        for proc in allProcesses:
            if hasattr(proc,'stop') and callable(getattr(proc,'stop')):
                print("Process with stop",proc)
                proc.stop()
                proc.join()
            else:
                print("Process witouth stop",proc)
                proc.terminate()
                proc.join()
                