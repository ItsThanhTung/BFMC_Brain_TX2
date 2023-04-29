import  time
from src.perception.traffic_sign.GeneralHandler import GeneralHandler

class ParkingHandler(GeneralHandler):
    def __init__(self, car_handler, logger):
        super(ParkingHandler,self).__init__(car_handler, logger)
        
        self.name = "PARKING"
        self.time_stop = 10
        self.obj_info=None
        
        
    def handler(self, decision_maker, object_info):
        self.start_handler_log()
        # status, mess_speed = self.car_handler.setSpeed(0, send_attempt= 100)
        # print('start parking')
        
        decision_maker.is_parking = True
        # self.car_handler.setSpeed(0, send_attempt=100)
        # time.sleep(0.5)
        
        # self.car_handler.setSpeed(20, send_attempt=100)
        # time.sleep(3.7)
        
        # self.car_handler.setSpeed(0, send_attempt=100)
        # time.sleep(0.5)
        
        # self.car_handler.setAngle(23,send_attempt=100)
        # self.car_handler.setSpeed(-30, send_attempt=100)
        # time.sleep(4.3)
        
        # self.car_handler.setSpeed(0, send_attempt=100)
        # time.sleep(0.5)

        # self.car_handler.setAngle(-23, send_attempt=100)
        # self.car_handler.setSpeed(-30, send_attempt=100)
        # time.sleep(2.2)
               
        # self.car_handler.setSpeed(0, send_attempt=100)
        # time.sleep(1)
        
        # self.car_handler.setSpeed(20, send_attempt=100)
        # self.car_handler.setAngle(5,send_attempt=100)
        # time.sleep(1)
        
        # self.car_handler.setSpeed(0, send_attempt=100)
        # self.car_handler.setAngle(0,send_attempt=100)
        # time.sleep(10)
        
        # exit()
        
        # DistStatus, DistMess = self.car_handler.getDistanceStatus()
        # while DistStatus != 1:
        #     time.sleep(0.1)
        #     DistStatus, DistMess = self.car_handler.getDistanceStatus()      
            # print("Status {} Mess  {}".format(DistStatus, DistMess))
            
        
        # time.sleep(self.time_stop)
        #     DistStatus, DistMess = self.car_handler.getDistanceStatus()
        #     print("Status {} Mess  {}".format(DistStatus, DistMess))
        # if status < 0:
        #     self.speed_log(status, mess_speed)
            
        self.end_handler_log()
        return True
    
    
    def is_handle(self, object_info):
        dist = object_info[1]
        self.obj_info = object_info
        print(dist)
        if dist > 270:
            print('done parking')
            return True

        return False
