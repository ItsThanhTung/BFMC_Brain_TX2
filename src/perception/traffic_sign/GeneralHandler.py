aterisk_line = "*******************************************************************\n"

class GeneralHandler:
    def __init__(self, car_handler, logger):
        self.car_handler = car_handler
        self.logger = logger
        self.name = "None"
        
        
    def handler(self):
        pass
    
    
    def is_handle(self):
        pass
            
            
    def speed_log(self, status, message):
        log_message = "\nFail send speed: {} \t {}\n".format(status, message)
        self.logger.write(log_message)
        
        
    def start_handler_log(self):
        self.logger.write("\n" + aterisk_line)
        log_message = "\nSTART HANDLER {}\n".format(self.name)
        self.logger.write(log_message)
        
        
    def end_handler_log(self):
        log_message = "\nEND HANDLER {}\n".format(self.name)
        self.logger.write(log_message)
        self.logger.write(aterisk_line)
        