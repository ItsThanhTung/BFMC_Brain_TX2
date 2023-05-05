from src.utils.utils_function import setSpeed, setAngle, EnablePID, MoveDistance
import time
import numpy as np

aterisk_line = "*******************************************************************"
class InterceptionHandler:
    def __init__(self, car_handler, logger):
        self.car_handler = car_handler
        self.logger = logger
        self.count = 0
        
    def handler(self):
        print("handler")
        # self.send_speed(0)
        # time.sleep(1)
        print(self.count)
        if self.count == 0:
            self.start_handler_log("First intercept right")
            status, mess_angle = self.car_handler.setAngle(-2, send_attempt=100)
            self.car_handler.moveDistance_Block(0.4, 0.04)
            # status, messSpd = self.car_handler.setSpeed(0, send_attempt=100) 
            status, mess_angle = self.car_handler.setAngle(23, send_attempt=100)
            self.car_handler.moveDistance_Block(0.8, 0.04)
            self.count += 1
            time.sleep(1)
            return True

        elif self.count == -1:
            self.start_handler_log("Roundabout")
            return True

        elif self.count == 1:
            self.start_handler_log("Third intercept left")
            status, mess_angle = self.car_handler.setAngle(-2, send_attempt=100)
            self.car_handler.moveDistance_Block(0.75, 0.04)
            # status, messSpd = self.car_handler.setSpeed(0, send_attempt=100) 
            status, mess_angle = self.car_handler.setAngle(-23, send_attempt=100)
            self.car_handler.moveDistance_Block(0.8, 0.04)

            status, mess_angle = self.car_handler.setAngle(0, send_attempt=100)
            self.car_handler.moveDistance_Block(0.3, 0.04)

            self.count += 1
            time.sleep(1)
            return True

        elif self.count == 2:
            self.start_handler_log("Third intercept straight")
            status, mess_angle = self.car_handler.setAngle(0, send_attempt=100)
            self.car_handler.moveDistance_Block(1.5, 0.04)
            self.count += 1
            return True

        elif self.count == 3:
            self.start_handler_log("Third intercept left")
            status, mess_angle = self.car_handler.setAngle(-2, send_attempt=100)
            self.car_handler.moveDistance_Block(0.23, 0.04)
            # status, messSpd = self.car_handler.setSpeed(0, send_attempt=100) 
            status, mess_angle = self.car_handler.setAngle(23, send_attempt=100)
            self.car_handler.moveDistance_Block(1.1, 0.04)
            time.sleep(5)
            self.count += 1
            return True

        elif self.count == 4:
            self.start_handler_log("Fourth intercept right")
            status, mess_angle = self.car_handler.setAngle(-2, send_attempt=100)
            self.car_handler.moveDistance_Block(0.23, 0.04)
            # status, messSpd = self.car_handler.setSpeed(0, send_attempt=100) 
            status, mess_angle = self.car_handler.setAngle(23, send_attempt=100)
            self.car_handler.moveDistance_Block(1.1, 0.04)
            time.sleep(5)
            self.count += 1
            return True

        elif self.count == 5:
            self.start_handler_log("Fifth intercept right")
            status, mess_angle = self.car_handler.setAngle(-2, send_attempt=100)
            self.car_handler.moveDistance_Block(0.23, 0.04)
            # status, messSpd = self.car_handler.setSpeed(0, send_attempt=100) 
            status, mess_angle = self.car_handler.setAngle(23, send_attempt=100)
            self.car_handler.moveDistance_Block(1.1, 0.04)
            time.sleep(5)
            self.count += 1
            return True

        elif self.count == 6:
            self.start_handler_log("Sixth intercept left")
            status, mess_angle = self.car_handler.setAngle(-2, send_attempt=100)
            self.car_handler.moveDistance_Block(0.23, 0.04)
            # status, messSpd = self.car_handler.setSpeed(0, send_attempt=100) 
            status, mess_angle = self.car_handler.setAngle(23, send_attempt=100)
            self.car_handler.moveDistance_Block(1.1, 0.04)
            time.sleep(5)
            self.count += 1
            return True

        elif self.count == 7:
            self.start_handler_log("Seventh intercept left")
            status, mess_angle = self.car_handler.setAngle(-2, send_attempt=100)
            self.car_handler.moveDistance_Block(0.23, 0.04)
            # status, messSpd = self.car_handler.setSpeed(0, send_attempt=100) 
            status, mess_angle = self.car_handler.setAngle(23, send_attempt=100)
            self.car_handler.moveDistance_Block(1.1, 0.04)
            time.sleep(5)
            self.count += 1
            return False


        
       
        self.end_handler_log()
    

    def turn_right(self):
    

        while imu_angle < 75:   
            print("imu ", imu_angle)    
            if imu_angle < 5:
                angle = 7
                
            elif imu_angle < 10:
                angle = 18

            elif imu_angle < 15:
                angle = 23
            
            elif imu_angle < 25:
                angle = 23
   
            else:
                angle = 23
                
            angle = int(angle*1.5)            
            self.send_angle(angle)
            self.log_handler(imu_angle, angle)
            
            time.sleep(0.08)
            
            imu_angle = self.imu_handler.get_yaw()  
            
            
    def go_straight(self, angle_lane_keeping):
        # angle_lane_keeping = np.clip(angle_lane_keeping, -5, 5)

        # self.send_angle(angle_lane_keeping, send_attempt=100)
        # # self.send_speed(30)
        # time.sleep(0.5)
        # self.send_angle(0,send_attempt=10)

        self.send_speed(40)
        time.sleep(3.5)            
                            
    def send_speed(self, speed):
        # print("set speed: ", speed)
        status, mess_speed = self.car_handler.setSpeed(speed, send_attempt= 10)
        
        if status < 0:
            self.speed_log(status, mess_speed)
            
            
            
    def send_angle(self, angle, send_attempt=10):
        # print("set angle: ", angle)
        status, mess_angle = self.car_handler.setAngle(angle, send_attempt= send_attempt)
        
        if status < 0:
            self.angle_log(status, mess_angle)
            
    def special_turn_left(self):
        imu_angle = self.imu_handler.get_yaw()   
        self.send_speed(20)

        while imu_angle > -75:       
            if imu_angle > -7:
                angle = -7
            
            elif imu_angle > -20:
                angle = -15
   
            elif imu_angle > -25:
                angle = -16

            elif imu_angle > -55:
                angle = -18
     
            else:
                angle = -23
            angle = int(angle*1.5)                
            self.send_angle(angle)
            self.log_handler(imu_angle, angle)
            
            time.sleep(0.08)
            
            imu_angle = self.imu_handler.get_yaw()   


    def turn_left(self, angle_lane_keeping):
        # angle_lane_keeping = np.clip(angle_lane_keeping, -5, 5)

        # self.send_angle(angle_lane_keeping, send_attempt=100)
        # # self.send_speed(30)
        # time.sleep(0.5)
        # self.send_angle(0,send_attempt=10)
        
        
        imu_angle = self.imu_handler.get_yaw()   
        self.send_speed(20)

        while imu_angle > -75:    
            print(imu_angle)   
            if imu_angle > -10:
                angle = -7

            elif imu_angle > -15:
                angle = -8
            
            elif imu_angle > -20:
                angle = -10
   
            elif imu_angle > -25:
                angle = -13

            elif imu_angle > -55:
                angle = -15
     
            else:
                angle = -23
            angle = int(angle*2.5)       
            print(angle)     
            self.send_angle(angle)
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
        
        
    def special_turn_right(self):
        imu_angle = self.imu_handler.get_yaw()   
        self.send_speed(20)

        while imu_angle < 75:   
            print("imu ", imu_angle)    
            if imu_angle < 5:
                angle = 10
                self.send_angle(angle)
                
            elif imu_angle < 10:
                angle = 20
                self.send_angle(angle)

            elif imu_angle < 15:
                angle = 23
                self.send_angle(angle)
            
            elif imu_angle < 25:
                angle = 23
                self.send_angle(angle)
   
            else:
                angle = 23
                self.send_angle(angle)
                
            self.log_handler(imu_angle, angle)
            
            time.sleep(0.08)
            
            imu_angle = self.imu_handler.get_yaw()  

            

            