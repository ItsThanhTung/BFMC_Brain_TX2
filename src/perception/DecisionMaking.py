import time

aterisk_line = "*******************************************************************"
class CarState:

    traffic_sign = 1
    lane_keeping = 2
    intercept = 3
    
class DecisionMaking:
    def __init__(self, logger):
        
        self.state = CarState.lane_keeping
    
        # intercep parameter
        self.min_intercept_length = 100
        self.max_intercept_gap = 40
        
        self.logger = logger
        
        self.count = 0
        self.speed = 50
    
        self.default_speed = 50
        
        self.start_time = None
        self.wait_time = None
        
    def stop(self):
        print('set stop')
        self.speed = 0
        
    def start(self):
        print('set start')
        self.speed = self.default_speed

        
    def slow_down(self, wait_time=None):
        print('set slow_down')
        self.speed = 25
        self.start_time = time.time()
        self.wait_time = wait_time
        
    def speed_up(self, wait_time=None):
        print('set speed_up')
        self.speed = 45
        self.start_time = time.time()
        self.wait_time = wait_time
        
    def reiniate(self):
        if self.start_time and self.wait_time:
            print("reinitiate")
            if time.time() - self.start_time > self.wait_time:
                self.speed = self.default_speed
                self.start_time = None
                
    
    def is_intercept(self, intercept_length, intercept_gap):        
        if intercept_length >= self.min_intercept_length and intercept_gap < self.max_intercept_gap:
            log_message = self.is_intercept_log(intercept_length, intercept_gap)
            self.logger.write(log_message)
            return True
        
        log_message = self.not_intercept_log(intercept_length, intercept_gap)
        self.logger.write(log_message)
        return False
    
    
    def is_intercept_log(self, intercept_length, intercept_gap):
        return "\n \n" + aterisk_line + "\n" +\
            "INTERCEPT with intercept_length = {} \t intercept_gap = {} \n \n".format(intercept_length, intercept_gap) \
            + aterisk_line
    
    
    def not_intercept_log(self, intercept_length, intercept_gap):
        return "\n intercept_length = {} \t intercept_gap = {} \n".format(intercept_length, intercept_gap)
    
    
    def get_intercept_direction(self):
        # return 'right'
        if self.count == 0:
            self.count += 1
            return 'left'
        
        elif self.count == 1:
            self.count += 1
            return 'straight'
        
        elif self.count == 2:
            self.count += 1
            return 'left'
        
        elif self.count == 3:
            self.count += 1
            return 'right'
        
        elif self.count == 4:
            self.count += 1
            return 'special_turn_left'
        
        elif self.count == 5:
            self.count += 1
            return 'special_turn_right'
        
        else:
            return 'right' #left,right,straight

    