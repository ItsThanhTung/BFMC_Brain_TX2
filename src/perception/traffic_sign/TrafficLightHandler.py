import  time
from src.perception.traffic_sign.GeneralHandler import GeneralHandler

class TrafficLightHandler(GeneralHandler):
    def __init__(self, car_handler, logger):
        super(TrafficLightHandler,self).__init__(car_handler, logger)
        
        self.name = "Traffic Light"
        self.time_stop = 2
        
        
    def handler(self, decision_maker, object_info):
        self.start_handler_log()
        print(object_info[4])
        if object_info[4] in ['yellow', 'red'] :
            status, mess_speed = self.car_handler.setSpeed(0, send_attempt= 100)
            
        else:
            status, mess_speed = self.car_handler.setSpeed(35, send_attempt= 100)
            

        self.end_handler_log()
        
        return False

    
    
    def is_handle(self, object_info):
        dist = object_info[1]
        if dist > 190:
            return True

        return False
