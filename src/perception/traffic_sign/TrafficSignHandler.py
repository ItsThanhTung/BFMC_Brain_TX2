from src.perception.traffic_sign.StopSignHandler import StopSignHandler
from src.perception.traffic_sign.PedestrianHandler import PedestrianHandler

from src.perception.tracker.byte_tracker import BYTETracker


import numpy as np


def mapping_distance(center_location):
    # 30 - 321, 179    520 - 184
    # 20 - 309, 198    542 - 192
    # 10 - 292, 232    
    return center_location[1]

class TrafficSignHandler:
    def __init__(self, car_handler, logger):
        self.car_handler = car_handler
        self.logger = logger
        
        self.handler_dict = {"stop" : StopSignHandler(car_handler, self.logger), "pedestrian" : PedestrianHandler(car_handler, self.logger)}
        self.tracker = BYTETracker()
    
    def detect(self, results):
        
        object_result = self.tracker.update(results)
        print(object_result)
        if object_result is None:
            return 
        
        for object in object_result:
            is_handle = object.is_handle
            if is_handle:
                continue
            
            cls = object.cls
            
            if cls in self.handler_dict:
            
                center = object.center
                dist = mapping_distance(center)
                
                object_info = [center, dist]  # still missing
                
                if self.handler_dict[cls].is_handle(object_info):
                    is_done = self.handler_dict[cls].handler()
                    object.is_handle = is_done
                    

        
    
