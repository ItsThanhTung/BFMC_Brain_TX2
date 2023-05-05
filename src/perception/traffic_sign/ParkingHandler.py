import  time
from src.perception.traffic_sign.GeneralHandler import GeneralHandler

class ParkingHandler(GeneralHandler):
    def __init__(self, car_handler, logger):
        super(ParkingHandler,self).__init__(car_handler, logger)
        
        self.name = "PARKING"
        self.time_stop = 10
        self.obj_info = None


    def handler(self, decision_maker, object_info):
        self.start_handler_log()  
        decision_maker.is_parking = True        
        self.end_handler_log()
        return False
    
    
    def is_handle(self, object_info, is_tune=False):
        dist = object_info[1]
        self.obj_info = object_info
        
        if is_tune:
            print(dist)
            return False

        if dist > 230:
            print('start parking')
            return True

        return False
