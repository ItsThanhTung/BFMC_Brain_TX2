from src.perception.traffic_sign.StopSignHandler import StopSignHandler
import numpy as np

class TrafficSignHandler:
    def __init__(self, car_handler, logger):
        self.car_handler = car_handler
        self.logger = logger
        
        self.handler_dict = {"stop" : StopSignHandler(car_handler, self.logger)}
        
        # self.tracker = ByteTrack()
        
        self.handler_dict = {"stop" : StopSignHandler(car_handler)}
    
    def detect(self, object_result):
        if object_result is not None and len(object_result) > 0:       
            print(object_result)
        #     if object_result[0][1] > 0.9: 
        #         if self.counter == 0 :         
        #             self.handler_dict["stop"].handler()
        #             self.counter += 1
                    
        # if self.counter > 0:
        #     self.counter += 1
        # elif self.counter == 100:
        #     self.counter = 0

        
    
