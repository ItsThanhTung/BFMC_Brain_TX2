from threading import Thread, Lock
from src.templates.workerprocess import WorkerProcess
from src.utils.utils_function import setSpeed, setAngle, EnablePID

import time
class DecisionMakingProcess(WorkerProcess):
    # ===================================== INIT =========================================
    data_lane_keeping_lock = Lock()
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

        self.debug = debug
        self.prev_angle = 0

        
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
        decisionMakingTh = Thread(name='DecisionMaking',target = self._run_decision_making)     

        decisionMakingTh.daemon = True
        readDataLaneKeepingTh.daemon = True
        self.threads.append(decisionMakingTh)
        self.threads.append(readDataLaneKeepingTh)
        
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

    def _run_decision_making(self):
        # if not self.debug:
        #     EnablePID(self.outPs["SERIAL"])
        while True:
            try:
                self.data_lane_keeping_lock.acquire()
                speed_lane_keeping = self.speed_lane_keeping
                angle_lane_keeping = self.angle_lane_keeping
                self.data_lane_keeping_lock.release()

                if self.prev_angle != angle_lane_keeping:
                    if not self.debug:
                        # setSpeed(self.outPs["SERIAL"], float(35))
                        setAngle(self.outPs["SERIAL"] , float(angle_lane_keeping))
                        self.prev_angle = angle_lane_keeping


            except Exception as e:
                print("Decision Making - decision making thread error:")
                print(e)
        
    


            
