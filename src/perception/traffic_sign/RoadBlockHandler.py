import  time
from src.perception.traffic_sign.GeneralHandler import GeneralHandler

class RoadBlockHandler(GeneralHandler):
    def __init__(self, car_handler, logger):
        super(RoundaboutHandler, self).__init__(car_handler, logger)
        
        self.name = "RoadBlock"
        self.time_stop = 2
        self.car_handler = car_handler

    def handler(self, decision_maker, object_info):
        self.start_handler_log()    
        status, mess_angle = self.car_handler.setAngle(-1, send_attempt=100)
        error = self.car_handler.moveDistance_Block(0.42, 0.05)
        print("1: ", error)

        self.car_handler.setSpeed(0, send_attempt= 10)
        status, mess_angle = self.car_handler.setAngle(20, send_attempt=100)
        error = self.car_handler.moveDistance_Block(0.4, 0.05)
        print("2: ", error)

        self.end_handler_log()
        return True
    
    
    def is_handle(self, object_info, is_tune=False):
        dist = object_info[1]

        if is_tune:
            print(dist)
            return False

        if dist > 275:
            return True

        return False

