from threading import Thread, Lock, Event
from src.templates.workerprocess import WorkerProcess
from src.hardware.serialhandler.filehandler import FileHandler
from src.perception.InterceptionHandler import InterceptionHandler
import sys
from src.hardware.IMU.imuHandler import IMUHandler
from src.perception.CarHandlerThread import CarHandlerThread
from src.perception.traffic_sign.TrafficSignHandler import TrafficSignHandler
from src.perception.DecisionMaking import DecisionMaking
from src.perception.PointProcess import Point
from src.perception.tracker.byte_tracker import BYTETracker

from src.perception.CarPoseHandlerThread import CarPoseThread
from src.perception.Planning import Planning

from datetime import datetime
import time
import numpy as np

class DecisionMakingProcess(WorkerProcess):
    # ===================================== INIT =========================================
    data_lane_keeping_lock = Lock()
    data_intercept_detection_lock = Lock()
    data_object_detection_lock = Lock()
    historyFile = FileHandler("carControlHistory.txt")

    def __init__(self, inPs, outPs, serInPs, opt, objectP, is_stop):
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
        

        super(DecisionMakingProcess,self).__init__(inPs, outPs)
        self.opt = opt
        self.speed_lane_keeping = 0 
        self.angle_lane_keeping = 0 
        self.lane_data = None
        self.objectP = objectP

        self.intercept_length = 0
        self.intercept_gap = float("inf")
        
        self.object_result = None
        self.is_intercept = False
        
        # self.imu_handler = IMUHandler()
        
        self.is_sign = False
        self.count_sign_step = 0

        self.__CarHandlerTh = CarHandlerThread(serInPs, self.outPs, enablePID= True)
        self.__CarHandlerTh.daemon = True
        self.threads.append(self.__CarHandlerTh)

        self.enableEKF = opt["ENABLE_EKF"]
        if self.enableEKF:
            self.CarPoseHandler = CarPoseThread(inPs["CarEstimate"])
            self.CarPoseHandler.daemon = True
            self.threads.append(self.CarPoseHandler)

        
        self.is_stop = is_stop
        
        
        self.point = Point()
        self.decision_maker = DecisionMaking(self.historyFile, self.point)
        self.tracker = BYTETracker()
        self.planer = Planning()

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
        self.threads.append(readDataObjectDetectionTh)
        self.threads.append(readDataLaneKeepingTh)
        self.threads.append(readDataInterceptDetectionTh)



    def _read_data_lane_keeping(self):
        while True:
            try:
                data = self.inPs["LANE_KEEPING"].recv()
                speed = data["speed"]
                angle = data["angle"]
                lane_data = data["lane_data"]
                self.data_lane_keeping_lock.acquire()
                self.speed_lane_keeping = speed
                self.angle_lane_keeping = angle
                self.lane_data = lane_data
                self.data_lane_keeping_lock.release()

            except Exception as e:
                print("Decision Making - read data lane keeping thread error:")
                print(e)

    def _read_data_object_detection(self):
        while True:
            try:
                results = self.inPs["OBJECT_DETECTION"].recv()["results"]
                # print("get objects :",results)
                object_result = self.tracker.update(results)
                self.data_object_detection_lock.acquire()
                self.object_result = object_result
                self.data_object_detection_lock.release()

            except Exception as e:
                print("Decision Making - read data object detection thread error:")
                print(e)

    def _read_data_intercept_detection(self):
        while True:
            try:
                intercept_length, intercept_gap = self.inPs["INTERCEPT_DETECTION"].recv()
                # print("Get Intercept ", intercept_length)
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
        lane_data = self.lane_data
        self.data_lane_keeping_lock.release()
        return speed_lane_keeping, angle_lane_keeping, lane_data
    
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
    
    def turn_off_rc_car(self):
        status, messSpd = self.__CarHandlerTh.setAngle(0,1)
        status, messSpd = self.__CarHandlerTh.setAngle(0,1)
        status, messSpd = self.__CarHandlerTh.setSpeed(0,1)
        status, messSpd = self.__CarHandlerTh.setSpeed(0,1)


        self.__CarHandlerTh.enListenSpeed(False)
        return 0

    
    def _run_decision_making(self):
        if not self.is_stop:
            status, messSpd = self.__CarHandlerTh.enablePID()

        if self.enableEKF:
            status, messSpd = self.__CarHandlerTh.enListenSpeed()
            time.sleep(0.01)
            status, messSpd = self.__CarHandlerTh.enListenSpeed()
            time.sleep(0.01)

            self.CarPoseHandler.waitInitDone()
            print("DM Wait EKF Done")
        status, messSpd = self.__CarHandlerTh.enListenVLX()
        time.sleep(0.01)

        status, messSpd = self.__CarHandlerTh.enListenVLX()
        time.sleep(0.01)

        
        trafficSignHanlder = TrafficSignHandler(self.__CarHandlerTh, self.historyFile, self.decision_maker, self.point,self.CarPoseHandler)

        prev_SendTime = time.time()
        local_node = None
        while True:
            if True:
                self.decision_maker.reiniate_speed()
                # skip_intecept_node = [29,30,10,11,12,13]
                pose = self.CarPoseHandler.GetCarPose()
                if pose['x'] == 0 and pose['y']==0:
                    continue
                    
                if self.decision_maker.start_switch_node is not None:
                    cur_pose = np.array([pose['x'],pose['y']])
                    dist_from_start = np.linalg.norm(cur_pose-self.decision_maker.start_switch_node)
                    print(f'end switch node: {self.decision_maker.end_switch_node}')
                    print('cur node ',current_node)
                    if dist_from_start > 1:
                        self.point.switch_to_main_map()
                        
                        if current_node >= self.decision_maker.end_switch_node:
                            self.decision_maker.trafic_strategy = 'LANE'
                            self.decision_maker.start_switch_node = None
                self.planer.update_point(pose)
                current_node, error_dist, local_node = self.point.get_closest_node(pose)
                if len(local_node) == 1:
                    self.__CarHandlerTh.setSpeed(0,send_attempt=100)
                    print("This is the end of the map")
                    time.sleep(100)
                    raise Exception("This is the end of the map")
                else:
                    next_node, next_point = local_node[1], self.point.get_point(local_node[1])
                

                if (self.decision_maker.strategy != "GPS" and error_dist > 1000.4) or self.decision_maker.trafic_strategy == 'GPS':
                    self.strategy = "GPS"
                    print("Switch to GPS strategy")

                elif self.decision_maker.strategy == "GPS" and not self.is_intercept and error_dist < 0.2  :
                    self.decision_maker.strategy = "LANE"
                    self.decision_maker.reiniate_map()
                    print("Switch to LANE strategy")
                    

                current_time = time.time()
                current_time = datetime.fromtimestamp(current_time)
                self.historyFile.write("\n" + str(current_time))

                
                speed_lane_keeping, angle_lane_keeping, lane_data = self.read_lane_keeping_data()
                
                intercept_length, intercept_gap = self.read_intercept_detection_data()
                object_result = self.read_object_detection_data()
            
                        
                if trafficSignHanlder.detect(object_result, lane_data,pose) and self.decision_maker.trafic_strategy == 'LANE':
                    continue

                
                if self.decision_maker.is_parking:
                    self.decision_maker.speed = 35
                    self.objectP.send(object_result)
                    data = self.__CarHandlerTh.GetVLXData()
                    print("VLXX data: ", data)
              
                    
                    if data[2] < 400:
                        print('cur node: ',current_node)
                        self.__CarHandlerTh.setSpeed(0, send_attempt=100) 
                        time.sleep(1)
                        if current_node == 30:
                            self.parking_2()
                        elif current_node == 31:
                            self.parking_1()

                    # send pipe object result 
                
                if not self.decision_maker.is_parking \
                        and not self.is_intercept \
                        and self.decision_maker.is_intercept(intercept_length, intercept_gap) \
                        and not self.is_stop: # and (current_node  not in skip_intecept_node):
                    # status, messSpd = self.__CarHandlerTh.setSpeed(0, send_attempt=100) 
                    # time.sleep(5)
                    # continue          for testing 

                    self.decision_maker.strategy = "GPS"
                    self.is_intercept = "True"
                    self.intercept_node = current_node
                    print("self.intercept_node: ", self.intercept_node)
                    self.__CarHandlerTh.setSpeed(25,1)
                    self.planer.reset_drive()
                    # direction = self.decision_maker.get_intercept_direction()
                    
                    # print(direction)
                    # interceptionHandler.handler(direction,angle_lane_keeping)
                    # continue
                
                if self.decision_maker.strategy == "LANE" and self.decision_maker.trafic_strategy == 'LANE':
                    self.historyFile.write("Lane keeping angle: {}   speed: {}\n".format(angle_lane_keeping, self.decision_maker.speed))
                    angle_lane_keeping = int(angle_lane_keeping)    
                    print('lane: ',angle_lane_keeping)
                    if not self.is_stop:
                        status, messSpd = self.__CarHandlerTh.setSpeed(self.decision_maker.speed, send_attempt=1) 
                        if status < 0:
                            log_message = "\nFail send speed: {} \t {}\n".format(status, messSpd)
                            self.historyFile.write(log_message)
                    else:
                        status, messSpd = 0, "OK"
                    if status < 0:
                            log_message = "\nFail send angle: {} \t {}\n".format(status, 1)
                            self.historyFile.write(log_message)
                    self.__CarHandlerTh.setAngle(angle_lane_keeping)
                    


                elif self.decision_maker.strategy == "GPS" or self.decision_maker.trafic_strategy == 'GPS': 
                    
                    # print(self.intercept_node, "---->", current_node, f"------ {self.planer.is_end_intercept(current_node, self.intercept_node)}")
                    if self.is_intercept and self.planer.is_end_intercept(current_node, self.intercept_node) and self.decision_maker.trafic_strategy == 'LANE':
                        self.decision_maker.strategy = "LANE"
                        self.is_intercept = False
                        continue
                    print('GPS')
                    angle = -self.planer.drive([next_point[0], next_point[1]])
                    # print('Angle gps: ',angle)
                    # print("angle gps: ", angle)
                    self.__CarHandlerTh.setSpeed(30)
                    self.__CarHandlerTh.setAngle(angle)
                    prev_SendTime = time.time()
                    
                    
            # print("end: ", time.time() - start_time)
            # except Exception as e:
            #     print("Decision Making - decision making thread error:")
            #     print(e)
            #     self.historyFile.write("Decision Making - decision making thread error:")
            #     self.historyFile.write(str(e))
                
        
    

             


    def _TestRun2(self):
        print("Test Run 2")
        self.__CarHandlerTh.moveDistance(-0.5)
        # time.sleep(0.1)
        # self.__CarHandlerTh.moveDistance(0.5)

        # time.sleep(1)
        while(True):
            time.sleep(0.2)
            Status, Mess = self.__CarHandlerTh.getDistanceStatus()
            print("Status {} Mess {}".format(Status, Mess))
        
    def _FakeRun(self):
        time.sleep(10)
        print("Start Run")
        self.__CarHandlerTh.setSpeed(35)
        self.__CarHandlerTh.setAngle(0)
        time.sleep(3)
        self.__CarHandlerTh.setSpeed(35)
        self.__CarHandlerTh.setAngle(-20)
        time.sleep(3)
        self.__CarHandlerTh.setSpeed(35)
        self.__CarHandlerTh.setAngle(15)
        time.sleep(3)
        self.__CarHandlerTh.setSpeed(35)
        self.__CarHandlerTh.setAngle(-25)
        time.sleep(3)
        self.__CarHandlerTh.setSpeed(35)
        self.__CarHandlerTh.setAngle(0)
        time.sleep(1)
        self.__CarHandlerTh.setSpeed(0)
        self.__CarHandlerTh.setAngle(0)
        self.__CarHandlerTh.enListenSpeed(False)
        print("Run Done")
        while(True):
            time.sleep(5)
            
    def parking_2(self):
        print('park slot 2')
        self.__CarHandlerTh.setAngle(0, send_attempt= 10)
        self.__CarHandlerTh.moveDistance_Block(0.7, 0.05)
        self.__CarHandlerTh.setSpeed(0)
        time.sleep(2)
        self.__CarHandlerTh.setAngle(0, send_attempt= 10)
        self.__CarHandlerTh.moveDistance_Block(0.4, 0.05)
        self.__CarHandlerTh.setSpeed(0)
        time.sleep(2)
        self.__CarHandlerTh.setAngle(-15, send_attempt= 10)
        self.__CarHandlerTh.moveDistance_Block(0.4, 0.05)
        self.__CarHandlerTh.setSpeed(0)
        time.sleep(2)
        self.__CarHandlerTh.setAngle(10, send_attempt= 10)
        self.__CarHandlerTh.moveDistance_Block(-0.4, 0.05)
        self.__CarHandlerTh.setSpeed(0)
        time.sleep(2)
        self.__CarHandlerTh.setAngle(-20, send_attempt= 10)
        self.__CarHandlerTh.moveDistance_Block(-0.4, 0.05)
        self.__CarHandlerTh.setSpeed(0)
        
        time.sleep(2)
        self.__CarHandlerTh.setAngle(-15, send_attempt= 10)
        self.__CarHandlerTh.moveDistance_Block(0.6, 0.05)
        self.__CarHandlerTh.setAngle(15, send_attempt= 10)
        self.__CarHandlerTh.moveDistance_Block(0.5, 0.05)
        time.sleep(2)
        
        
        print("End Move")
        time.sleep(100)
    def parking_1(self):
        print('park slot 1')
        self.__CarHandlerTh.setAngle(15, send_attempt= 10)
        self.__CarHandlerTh.moveDistance_Block(-0.5, 0.05)
        self.__CarHandlerTh.setSpeed(0)
        time.sleep(2)
        self.__CarHandlerTh.setAngle(-15, send_attempt= 10)
        self.__CarHandlerTh.moveDistance_Block(-0.5, 0.05)
        self.__CarHandlerTh.setSpeed(0)
        time.sleep(5)
        self.__CarHandlerTh.setAngle(-15, send_attempt= 10)
        self.__CarHandlerTh.moveDistance_Block(0.5, 0.05)
        self.__CarHandlerTh.setAngle(15, send_attempt= 10)
        self.__CarHandlerTh.moveDistance_Block(0.5, 0.05)
        time.sleep(2)
        self.__CarHandlerTh.setSpeed(0)
        time.sleep(100)