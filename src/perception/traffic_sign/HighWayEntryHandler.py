import  time
from src.perception.traffic_sign.GeneralHandler import GeneralHandler

class HighWayEntryHandler(GeneralHandler):
    def __init__(self, car_handler, logger):
        super(HighWayEntryHandler,self).__init__(car_handler, logger)
        
        self.name = "HighWay entry"
        self.time_stop = 2
        
        
    def handler(self, decision_maker, object_info):
        self.start_handler_log()
        
        decision_maker.speed_up(wait_time=None)
        
        self.end_handler_log()
        return True
    
    
    def is_handle(self, object_info, is_tune=False):
        dist = object_info[1]
        
        if is_tune:
            print(dist)
            return False

        if dist > 200:
            return True

        return False
