from src.perception.traffic_sign.StopSignHandler import StopSignHandler
from src.perception.traffic_sign.PedestrianHandler import PedestrianHandler
from src.perception.traffic_sign.ParkingHandler import ParkingHandler
from src.perception.traffic_sign.CrossWalkHandler import CrossWalkHandler
from src.perception.traffic_sign.TrafficLightHandler import TrafficLightHandler
from src.perception.traffic_sign.HighWayEntryHandler import HighWayEntryHandler
from src.perception.traffic_sign.HighWayExitHandler import HighWayExitHandler

from src.perception.tracker.byte_tracker import BYTETracker


import numpy as np


def mapping_distance(center_location):
    # 30 - 321, 179    520 - 184
    # 20 - 309, 198    542 - 192
    # 10 - 292, 232    
    return center_location[1]

class TrafficSignHandler:
    def __init__(self, car_handler, logger, decision_maker):
        self.car_handler = car_handler
        self.logger = logger
        
        self.handler_dict = {"stop" : StopSignHandler(car_handler, self.logger), "pedestrian" : PedestrianHandler(car_handler, self.logger),
                             "parking" : ParkingHandler(car_handler, self.logger), "crosswalk" :CrossWalkHandler(car_handler, logger),
                             "highway_entry" : HighWayEntryHandler(car_handler, self.logger), "highway_exit" : HighWayExitHandler(car_handler, self.logger),
                             "traffic_light" : TrafficLightHandler(car_handler, self.logger)}
        self.tracker = BYTETracker()
        
        self.decision_maker = decision_maker
    
    def detect(self, object_result, lane_data):
        if object_result is None:
            return 
        
        is_run = False
        
        for object in object_result:
            is_handle = object.is_handle
            if is_handle:
                continue

            cls = object.clss_max
            new_cls = object.new_cls

            # print("cls: ", new_cls)
            
            if cls in ['red', 'green', 'yellow']:
                cls = "traffic_light"
            
            if cls in self.handler_dict:
            
                center = object.center
                dist = mapping_distance(center)
                
                object_info = [center, dist, object, lane_data, object.new_cls]   # still missing

                if self.handler_dict[cls].is_handle(object_info):
                    is_done = self.handler_dict[cls].handler(self.decision_maker, object_info)
                    object.is_handle = is_done
                    is_run = True
                    
        return is_run
                    

        
    
