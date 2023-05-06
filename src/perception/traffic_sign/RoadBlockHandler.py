import  time
from src.perception.traffic_sign.GeneralHandler import GeneralHandler

class RoadBlockHandler(GeneralHandler):
    def __init__(self, car_handler, logger):
        super(RoadBlockHandler, self).__init__(car_handler, logger)
        
        self.name = "RoadBlock"
        self.time_stop = 2
        self.car_handler = car_handler

    def handler(self, decision_maker, object_info):
        self.start_handler_log()    
        status, mess_angle = self.__CarHandlerTh.setAngle(-23, send_attempt=100)
        error = self.__CarHandlerTh.moveDistance_Block(0.45, 0.05)

        status, mess_angle = self.__CarHandlerTh.setAngle(23, send_attempt=100)
        error = self.__CarHandlerTh.moveDistance_Block(0.6, 0.05)

        self.end_handler_log()
        return True
    
    
    def is_handle(self, object_info, is_tune=False):
        dist = object_info[1]

        if is_tune:
            print(dist)
            return False

        if dist > 255:
            return True

        return False

