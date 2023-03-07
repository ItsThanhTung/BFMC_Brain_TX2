import  time
from src.perception.traffic_sign.GeneralHandler import GeneralHandler

class StopSignHandler(GeneralHandler):
    def __init__(self, car_handler, logger):
        super(StopSignHandler,self).__init__(car_handler, logger)
        
        self.name = "STOP"
        self.time_stop = 2
        
        
    def handler(self):
        self.start_handler_log()
        status, mess_speed = self.car_handler.setSpeed(0, send_attempt= 100)
        
        time.sleep(self.time_stop)
        if status < 0:
            self.speed_log(status, mess_speed)
            
        self.end_handler_log()
        return True
    
    
    def is_handle(self, object_info):
        dist = object_info[1]
        if dist > 200:
            return True

        return False
