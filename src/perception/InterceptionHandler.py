from src.utils.utils_function import setSpeed, setAngle, EnablePID, MoveDistance
import time


aterisk_line = "*******************************************************************"
class InterceptionHandler:
    def __init__(self, imu_handler, car_handler, logger):
        self.min_intercept_length = 100
        self.max_intercept_gap = 40

        self.imu_handler = imu_handler
        self.car_handler = car_handler
        
        self.logger = logger
        
    def handler(self, direction):
        self.send_speed(0)
        time.sleep(1)
        
        self.start_handler_log(direction)
        
        self.imu_handler.set_yaw()
        if direction == 'right':
            self.turn_right()
        
        else:
            self.turn_left()
            
        self.end_handler_log()


    def turn_right(self):
        imu_angle = self.imu_handler.get_yaw()   
               
        while imu_angle < 75:
            if imu_angle < 5:
                status, mess_speed = self.car_handler.setSpeed(30)
                status, mess_angle = self.car_handler.setAngle(10)
                    
            elif imu_angle < 7:
                status, mess_speed = self.car_handler.setSpeed(30)
                status, mess_angle = self.car_handler.setAngle(14)
               
            
            elif imu_angle < 9:
                status, mess_speed = self.car_handler.setSpeed(30)
                status, mess_angle = self.car_handler.setAngle(15)

            
            elif imu_angle < 10:
                status, mess_speed = self.car_handler.setSpeed(30)
                status, mess_angle = self.car_handler.setAngle(17)

            
            elif imu_angle < 15:
                status, mess_speed = self.car_handler.setSpeed(30)
                status, mess_angle = self.car_handler.setAngle(19)

            
            elif imu_angle < 20:
                status, mess_speed = self.car_handler.setSpeed(30)
                status, mess_angle = self.car_handler.setAngle(19)

            
            elif imu_angle < 25:
                status, mess_speed = self.car_handler.setSpeed(30)
                status, mess_angle = self.car_handler.setAngle(20)

            
            
            elif imu_angle < 30:
                status, mess_speed = self.car_handler.setSpeed(30)
                status, mess_angle = self.car_handler.setAngle(22)

            
            elif imu_angle < 75:
                status, mess_speed = self.car_handler.setSpeed(30)
                status, mess_angle = self.car_handler.setAngle(23)

                            
    def send_speed(self, speed):
        # print("set speed: ", speed)
        status, mess_speed = self.car_handler.setSpeed(speed, send_attempt= 10)
        
        if status < 0:
            self.speed_log(status, mess_speed)
            
            
            
    def send_angle(self, angle):
        # print("set angle: ", angle)
        status, mess_angle = self.car_handler.setAngle(angle, send_attempt= 10)
        
        if status < 0:
            self.angle_log(status, mess_angle)


    def turn_left(self):
        imu_angle = self.imu_handler.get_yaw()   
        self.send_speed(30)

        while imu_angle > -75:       
            if imu_angle > -10:
                angle = -5
                self.send_angle(-5)

            elif imu_angle > -15:
                angle = -10
                self.send_angle(-11)
            
            elif imu_angle > -20:
                angle = -16
                self.send_angle(-12)
   
            elif imu_angle > -25:
                angle = -17
                self.send_angle(-13)

            elif imu_angle > -55:
                angle = -18
                self.send_angle(-15)
     
            else:
                angle = -23
                self.send_angle(-23)
                
            self.log_handler(imu_angle, angle)
            
            time.sleep(0.1)
            
            imu_angle = self.imu_handler.get_yaw()   


    def log_handler(self, imu_angle, angle): 
        log_message = "\t\t\timu_ange: {}    angle: {}\n".format(imu_angle, angle)
        self.logger.write(log_message)
        
        
    def end_handler_log(self):
        log_message = "\nEND INTERCEPT HANDLER\n"
        self.logger.write(log_message)
        self.logger.write(aterisk_line + "\n")
        
        
    def start_handler_log(self, direction):
        self.logger.write("\n" + aterisk_line)
        
        log_message = "\nSTART INTERCEPT HANDLER  DIRECTION " + direction
        self.logger.write(log_message + "\n")


    def speed_log(self, status, message):
        log_message = "\nFail send speed: {} \t {}\n".format(status, message)
        self.logger.write(log_message)
        
        
    def angle_log(self, status, message):
        log_message = "\nFail send angle: {} \t {}\n".format(status, message)
        self.logger.write(log_message)

            

            