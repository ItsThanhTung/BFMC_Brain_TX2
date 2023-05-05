import  time
from src.perception.traffic_sign.GeneralHandler import GeneralHandler

class CarObjectHandler(GeneralHandler):
    def __init__(self, car_handler, logger, point_handler):
        super(CarObjectHandler, self).__init__(car_handler, logger)
        
        self.name = "CAR"
        self.time_stop = 2
        self.point_handler = point_handler
        self.car_handler = car_handler
    def handler(self, decision_maker, object_info):
        self.start_handler_log()
        
        self.point_handler.switch_to_sub_map()
        
        # print('handler switch to sub')
        self.car_handler.setSpeed(25,1)
        decision_maker.trafic_strategy ="GPS" 
        
        self.end_handler_log()
        return True
    
    
    def is_handle(self, object_info, is_tune=False):
        dist = object_info[1]
        if is_tune:
            print(dist)
            return False
        # center = object_info[0]
        # if dist > 0:
        #     return True
        lane_data = object_info[3]
        center = object_info[0]
        left_point, right_point = lane_data["left_point"][0] * 2, lane_data["right_point"][0] * 2
        left_bound = left_point + 80 
        right_bound = right_point - 30
    
        
        if center[1] < 300:
            return False
        if center[0] > left_bound and center[0] < right_bound:
            print('True  left_bound: ', left_bound, " right_bound: ", right_bound, "    ", center[0])
            return True
        
        # print('False  left_bound: ', left_bound, " right_bound: ", right_bound, "    ", center[0])
        return False
