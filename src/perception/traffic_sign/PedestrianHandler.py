import numpy as np
import  time
from src.perception.traffic_sign.GeneralHandler import GeneralHandler

aterisk_line = "*******************************************************************\n"

class PedestrianHandler(GeneralHandler):
    def __init__(self, car_handler, logger):
        super(PedestrianHandler,self).__init__(car_handler, logger)
        
        self.name = "PEDESTRIAN"
        self.time_stop = 0.5
        
        
    def handler(self, decision_maker, object_info):
        self.start_handler_log()
        status, mess_speed = self.car_handler.setSpeed(0, send_attempt= 100)
        
        time.sleep(self.time_stop)
        if status < 0:
            self.speed_log(status, mess_speed)
            
        self.end_handler_log()
        
        return False
    
    
    def is_handle(self, object_info, is_tune=False):
        dist = object_info[1]

        if is_tune:
            print(dist)
            return False
        # center = object_info[0]
        if dist < 250:
            return False

        lane_data = object_info[3]
        center = object_info[0]
        
        left_point, right_point = lane_data["left_point"][0] * 2, lane_data["right_point"][0] * 2
        left_bound = left_point + 80 
        right_bound = right_point - 30
    
        
        if center[1] < 350:
            return False
        if center[0] > left_bound and center[0] < right_bound:
            print('True  left_bound: ', left_bound, " right_bound: ", right_bound, "    ", center[0])
            return True
        
        # print('False  left_bound: ', left_bound, " right_bound: ", right_bound, "    ", center[0])
        return False
            