from src.perception.traffic_sign import StopSignHandler


class TrafficSignHandler:
    def __init__(self, car_handler):
        self.car_handler = car_handler
        
        self.handler_dict = {"stop" : StopSignHandler(car_handler)}
    
    def detect(self, object_result):
        print(object_result)   
        if object_result is not None and len(object_result) > 0:         
            if object_result[0][1] > 0.9:          
                self.handler_dict["stop"].handler(0.9)
    
    

