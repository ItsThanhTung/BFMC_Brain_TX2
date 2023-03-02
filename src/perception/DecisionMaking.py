
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
        return 'left'

    