from threading import Thread, Lock
from src.templates.workerprocess import WorkerProcess
from src.utils.utils_function import setSpeed, setAngle, EnablePID, MoveDistance

import time
class DecisionMakingProcess(WorkerProcess):
    # ===================================== INIT =========================================
    data_lane_keeping_lock = Lock()
    data_intercept_detection_lock = Lock()
    def __init__(self, inPs, outPs, opt, debug):
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

        self.max_intercept_length = 0
        self.intercept_gap = float("inf")

        self.debug = debug
        self.prev_angle = 0
        self.is_stop = False

        
    # ===================================== RUN ==========================================
    def run(self):
        """Apply the initializing methods and start the threads.
        """
        super(DecisionMakingProcess,self).run()

    # ===================================== INIT THREADS =================================
    def _init_threads(self):
        """Initialize the sending thread.
        """
        if self._blocker.is_set():
            return
        
        readDataLaneKeepingTh = Thread(name='ReadDataLaneKeeping',target = self._read_data_lane_keeping)            
        readDataInterceptDetectionTh = Thread(name='ReadDataInterceptDetection',target = self._read_data_intercept_detection)     
        decisionMakingTh = Thread(name='DecisionMaking',target = self._run_decision_making)     

        decisionMakingTh.daemon = True
        readDataLaneKeepingTh.daemon = True
        readDataInterceptDetectionTh.daemon = True
        self.threads.append(decisionMakingTh)
        self.threads.append(readDataLaneKeepingTh)
        self.threads.append(readDataInterceptDetectionTh)
        
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

    def _read_data_intercept_detection(self):
         while True:
            try:
                max_intercept_length, intercept_gap = self.inPs["INTERCEPT_DETECTION"].recv()
                self.data_intercept_detection_lock.acquire()
                self.max_intercept_length = max_intercept_length
                self.intercept_gap = intercept_gap
                self.data_intercept_detection_lock.release()

            except Exception as e:
                print("Decision Making - read data intercept detection thread error:")
                print(e)

    def _run_decision_making(self):
        if not self.debug:
            EnablePID(self.outPs["SERIAL"])
        while True:
            try:
                self.data_lane_keeping_lock.acquire()
                speed_lane_keeping = self.speed_lane_keeping
                angle_lane_keeping = self.angle_lane_keeping
                self.data_lane_keeping_lock.release()

                self.data_intercept_detection_lock.acquire()
                max_intercept_length = self.max_intercept_length
                intercept_gap = self.intercept_gap
                self.data_intercept_detection_lock.release()

                # print("max_intercept_length: ", max_intercept_length, " intercept_gap: ", intercept_gap)
                if (max_intercept_length >= 150 and intercept_gap < 40) or self.is_stop:
                    if not self.is_stop:
                        print('stop')
                        self.is_stop = True
                        setSpeed(self.outPs["SERIAL"], float(0))
                        setAngle(self.outPs["SERIAL"] , float(22))
                        
                        # MoveDistance(self.outPs["SERIAL"] , 0.5, 0.5)
                    # print("max_intercept_length: ", max_intercept_length, " intercept_gap: ", intercept_gap)
                    
                if not self.is_stop: # and self.prev_angle != angle_lane_keeping:
                    if not self.debug:
                        angle_lane_keeping = int(angle_lane_keeping)
                        print(angle_lane_keeping)
                        setSpeed(self.outPs["SERIAL"], float(0.5*speed_lane_keeping))
                        setAngle(self.outPs["SERIAL"] , float(angle_lane_keeping))
                        self.prev_angle = angle_lane_keeping
                time.sleep(0.1)


            except Exception as e:
                print("Decision Making - decision making thread error:")
                print(e)
        
    


            
