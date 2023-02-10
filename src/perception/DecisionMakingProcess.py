from threading import Thread, Lock
from src.templates.workerprocess import WorkerProcess
from src.utils.utils_function import setSpeed, setAngle, EnablePID, MoveDistance
from src.hardware.serialhandler.filehandler import FileHandler
from src.perception.InterceptionHandler import InterceptionHandler

from src.hardware.IMU.imuHandler import IMUHandler
from src.perception.CarHandlerThread import CarHandlerThread

import time
import numpy as np

class DecisionMakingProcess(WorkerProcess):
    # ===================================== INIT =========================================
    data_lane_keeping_lock = Lock()
    data_intercept_detection_lock = Lock()
    data_object_detection_lock = Lock()
    historyFile = FileHandler("carControlHistory.txt")

    def __init__(self, inPs, outPs, serInPs, opt, debug):
        """Process used for sending images over the network to a targeted IP via UDP protocol 
        (no feedback required). The image is compressed before sending it. 

        Used for visualizing your raspicam images on remote PC.
        
        Parameters
        ----------
        inPs : list(Pipe) 
            List of input pipes, only the first pipe is used to transfer the captured frames. 
        outPs : list(Pipe) 
            List of output pipes (not used at the moment)
        """
        

        super(DecisionMakingProcess,self).__init__( inPs, outPs)
        self.opt = opt
        self.speed_lane_keeping = 0 
        self.angle_lane_keeping = 0 

        self.intercept_length = 0
        self.intercept_gap = float("inf")

        self.object_result = None

        self.debug = debug
        self.prev_angle = 0
        self.is_intercept = False
        
        self.imu_handler = IMUHandler()
        
 

        self.__CarHandlerTh = CarHandlerThread(serInPs, self.outPs["SERIAL"], enablePID= False)
        self.__CarHandlerTh.daemon = True
        self.threads.append(self.__CarHandlerTh)

    # ===================================== RUN ==========================================
    def run(self):
        """Apply the initializing methods and start the threads.
        """
        super(DecisionMakingProcess,self).run()
        self.historyFile.close()

    # ===================================== INIT THREADS =================================
    def _init_threads(self):
        """Initialize the sending thread.
        """
        if self._blocker.is_set():
            return
        
        readDataLaneKeepingTh = Thread(name='ReadDataLaneKeeping',target = self._read_data_lane_keeping)            
        readDataInterceptDetectionTh = Thread(name='ReadDataInterceptDetection',target = self._read_data_intercept_detection)     
        readDataObjectDetectionTh = Thread(name='ReadDataObjectDetection',target = self._read_data_object_detection)     
        decisionMakingTh = Thread(name='DecisionMaking',target = self._run_decision_making)     

        decisionMakingTh.daemon = True
        readDataLaneKeepingTh.daemon = True
        readDataInterceptDetectionTh.daemon = True
        readDataObjectDetectionTh.daemon = True


        self.threads.append(decisionMakingTh)
        self.threads.append(readDataLaneKeepingTh)
        self.threads.append(readDataInterceptDetectionTh)
        self.threads.append(readDataObjectDetectionTh)



    def _read_data_lane_keeping(self):
        while True:
            try:
                data = self.inPs["LANE_KEEPING"].recv()
                speed = data["speed"]
                angle = data["angle"]
                self.data_lane_keeping_lock.acquire()
                self.speed_lane_keeping = speed
                self.angle_lane_keeping = angle
                self.data_lane_keeping_lock.release()

            except Exception as e:
                print("Decision Making - read data lane keeping thread error:")
                print(e)

    def _read_data_object_detection(self):
        while True:
            try:
                results = self.inPs["OBJECT_DETECTION"].recv()["results"]
                self.data_object_detection_lock.acquire()
                self.object_result = results
                self.data_object_detection_lock.release()

            except Exception as e:
                print("Decision Making - read data object detection thread error:")
                print(e)

    def _read_data_intercept_detection(self):
        while True:
            try:
                intercept_length, intercept_gap = self.inPs["INTERCEPT_DETECTION"].recv()
                self.data_intercept_detection_lock.acquire()
                self.intercept_length = intercept_length
                self.intercept_gap = intercept_gap
                self.data_intercept_detection_lock.release()

            except Exception as e:
                print("Decision Making - read data intercept detection thread error:")
                print(e)

    def read_lane_keeping_data(self):
        self.data_lane_keeping_lock.acquire()
        speed_lane_keeping = self.speed_lane_keeping
        angle_lane_keeping = self.angle_lane_keeping
        self.data_lane_keeping_lock.release()
        return speed_lane_keeping, angle_lane_keeping
    
    def read_intercept_detection_data(self):
        self.data_intercept_detection_lock.acquire()
        intercept_length = self.intercept_length
        intercept_gap = self.intercept_gap
        self.data_intercept_detection_lock.release()
        return intercept_length, intercept_gap
    
    
    def read_object_detection_data(self):
        self.data_object_detection_lock.acquire()
        object_result = self.object_result
        self.data_object_detection_lock.release()
        return object_result

    def _run_decision_making(self):
        if not self.debug:
            status, messSpd = self.__CarHandlerTh.enablePID()

        interceptionHandler = InterceptionHandler()
        while True:
            if True:
                speed_lane_keeping, angle_lane_keeping = self.read_lane_keeping_data()
                intercept_length, intercept_gap = self.read_intercept_detection_data()
                object_result = self.read_object_detection_data()

                print(object_result)
                is_intercept, intercept_log = interceptionHandler.is_intercept(intercept_length, intercept_gap)                
                self.historyFile.write(intercept_log)
                
                if is_intercept:
                    self.historyFile.write("IMU START\n")
                    self.imu_handler.set_yaw()
                    self.is_intercept = True

                if self.is_intercept :                            
                    if not self.debug:
                        imu_angle = self.imu_handler.get_yaw()
                        intercept_handler_log, isFinish = interceptionHandler.turn_right(imu_angle, self.debug, self.__CarHandlerTh)
                        self.is_intercept = not isFinish
                    else:
                        intercept_handler_log, isFinish = interceptionHandler.turn_right(imu_angle, self.debug)
                        self.is_intercept = not isFinish
                        self.historyFile.write(intercept_handler_log)
                
                if not self.is_intercept: # and self.prev_angle != angle_lane_keeping:
                    if not self.debug:
                        angle_lane_keeping = int(angle_lane_keeping)    
                        
                        if np.abs(self.prev_angle - angle_lane_keeping) > 10:
                            self.historyFile.write("******************* OFF ANGLE ***************************\n")

                        status, messSpd = self.__CarHandlerTh.setSpeed(50)
                        status, messAng = self.__CarHandlerTh.setAngle(angle_lane_keeping)
                        self.historyFile.write("LANE KEEPING - speed: " + str(speed_lane_keeping) + " " + messSpd\
                                                        + " - angle: " + str(int(angle_lane_keeping)) + " " + messAng + "\n")
                        
                        self.prev_angle = angle_lane_keeping

                time.sleep(0.05)

            # except Exception as e:
            #     print("Decision Making - decision making thread error:")
            #     print(e)
            #     self.historyFile.write("Decision Making - decision making thread error:")
            #     self.historyFile.write(str(e))
                
        
    


            
