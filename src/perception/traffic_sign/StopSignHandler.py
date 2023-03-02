
aterisk_line = "*******************************************************************\n"

class StopSignHandler:
    def __init__(self, car_handler, logger):
        self.time_stop = 2
        self.car_handler = car_handler
        self.logger = logger
        
        self.name = "STOP"
        
        
    def handler(self):
        self.start_handler_log()
        status, mess_speed = self.car_handler.setSpeed(0, send_attempt= 100)
        
        if status < 0:
            self.speed_log(status, mess_speed)
            
        self.end_handler_log()
            

    def speed_log(self, status, message):
        log_message = "\nFail send speed: {} \t {}\n".format(status, message)
        self.logger.write(log_message)
        
    
    def start_handler_log(self):
        self.logger.write(aterisk_line)
        log_message = "\nSTART HANDLER {}\n".format(self.name)
        self.logger.write(log_message)
        
        
    def end_handler_log(self):
        log_message = "\nEND HANDLER {}\n".format(self.name)
        self.logger.write(log_message)
        self.logger.write(aterisk_line)
        