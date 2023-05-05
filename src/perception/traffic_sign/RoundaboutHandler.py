import  time
from src.perception.traffic_sign.GeneralHandler import GeneralHandler

class RoundaboutHandler(GeneralHandler):
    def __init__(self, car_handler, logger):
        super(RoundaboutHandler, self).__init__(car_handler, logger)
        
        self.name = "Roundabout"
        self.time_stop = 2
        self.car_handler = car_handler

    def handler(self, decision_maker, object_info):
        self.start_handler_log()
        
        
        self.car_handler.setSpeed(25,1)
        
        self.end_handler_log()
        return True
    
    
    def is_handle(self, object_info):
        dist = object_info[1]
        if dist > 270:
            return True

        return False

