import  time
from src.perception.traffic_sign.GeneralHandler import GeneralHandler

class HighWayExitHandler(GeneralHandler):
    def __init__(self, car_handler, logger):
        super(HighWayExitHandler,self).__init__(car_handler, logger)
        
        self.name = "HighWay exit"
        self.time_stop = 2
        
        
    def handler(self, decision_maker, object_info):
        self.start_handler_log()
        
        decision_maker.start()
        
        self.end_handler_log()
        return True
    
    
    def is_handle(self, object_info):
        dist = object_info[1]
        if dist > 250:
            return True

        return False
