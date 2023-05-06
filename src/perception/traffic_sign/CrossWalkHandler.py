import  time
from src.perception.traffic_sign.GeneralHandler import GeneralHandler

class CrossWalkHandler(GeneralHandler):
    def __init__(self, car_handler, logger):
        super(CrossWalkHandler,self).__init__(car_handler, logger)
        
        self.name = "CROSS WALK"
        self.time_stop = 2
        
        
    def handler(self, decision_maker, object_info):
        self.start_handler_log()
        
        decision_maker.slow_down(wait_time=3)
        decision_maker.is_crosswalk = True
        self.end_handler_log()
        return True
    
    
    def is_handle(self, object_info, is_tune=False):
        dist = object_info[1]
        if is_tune:
            print(dist)
            return False

        if dist > 230:
            return True

        return False
