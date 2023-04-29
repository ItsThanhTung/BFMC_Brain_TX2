import  time
from src.perception.traffic_sign.GeneralHandler import GeneralHandler

class ParkingHandler(GeneralHandler):
    def __init__(self, car_handler, logger,point_handler,CarPoseHandler):
        super(ParkingHandler,self).__init__(car_handler, logger)
        
        self.name = "PARKING"
        self.time_stop = 10
        self.obj_info=None
        self.point_handler = point_handler
        self.pose_handler = CarPoseHandler


    def handler(self, decision_maker, object_info):
        self.start_handler_log()  
        decision_maker.is_parking = True        
        self.end_handler_log()
        return False
    
    
    def is_handle(self, object_info):
        dist = object_info[1]
        self.obj_info = object_info
        if dist > 230:
            print('done parking')
            return True

        return False
