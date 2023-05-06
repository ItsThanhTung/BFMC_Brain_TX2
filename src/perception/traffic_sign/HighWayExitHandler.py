import  time
from src.perception.traffic_sign.GeneralHandler import GeneralHandler

class HighWayExitHandler(GeneralHandler):
    def __init__(self, car_handler, logger):
        super(HighWayExitHandler,self).__init__(car_handler, logger)
        
        self.name = "HighWay exit"
        self.time_stop = 2
        self.car_handler = car_handler
        
        
    def handler(self, decision_maker, object_info):
        self.start_handler_log()
        
        decision_maker.start()
        

        status, mess_angle = self.car_handler.setAngle(-3, send_attempt=100)
        self.car_handler.moveDistance_Block(1.5, 0.04)

        self.end_handler_log()
        return True
    
    
    def is_handle(self, object_info, is_tune=False):
        dist = object_info[1]

        if is_tune:
            print(dist)
            return False

        if dist > 240:
            return True

        return False
