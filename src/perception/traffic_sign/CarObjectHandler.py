import  time
from src.perception.traffic_sign.GeneralHandler import GeneralHandler

class CarObjectHandler(GeneralHandler):
    def __init__(self, car_handler, logger, point_handler):
        super(CarObjectHandler, self).__init__(car_handler, logger)
        
        self.name = "CAR"
        self.time_stop = 2
        self.point_handler = point_handler
        self.car_handler = car_handler
    def handler(self, decision_maker, object_info):
        self.start_handler_log()
        
        self.point_handler.switch_to_sub_map()
        
        # print('handler switch to sub')
        self.car_handler.setSpeed(25,1)
        decision_maker.trafic_strategy ="GPS" 
        
        self.end_handler_log()
        return True
    
    
    def is_handle(self, object_info):
        dist = object_info[1]
        print(dist)
        if dist > 220:
            return True

        return False
