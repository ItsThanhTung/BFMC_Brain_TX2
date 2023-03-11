from src.utils.utils_function import setSpeed, setAngle, EnablePID, MoveDistance
import time
import numpy as np

aterisk_line = "*******************************************************************"
class InterceptionHandler:
    def __init__(self, imu_handler, car_handler, logger):
        self.min_intercept_length = 100
        self.max_intercept_gap = 40

        self.imu_handler = imu_handler
        self.car_handler = car_handler
        
        self.logger = logger
        
    def handler(self, direction,angle_lane_keeping):
        # self.send_speed(0)
        # time.sleep(1)
        
        self.start_handler_log(direction)
        
        self.imu_handler.set_yaw()
        if direction == 'right':
            self.turn_right()
            
        elif direction == 'special_turn_left':
            self.special_turn_left()
            
        elif direction == 'special_turn_right':
            self.special_turn_right()
        
        elif direction =='straight':
            self.go_straight(angle_lane_keeping)
            
        else:
            self.turn_left(angle_lane_keeping)
            
        self.end_handler_log()


    def turn_right(self):
        imu_angle = self.imu_handler.get_yaw()   
        self.send_speed(20)

        while imu_angle < 75:   
            print("imu ", imu_angle)    
            if imu_angle < 5:
                angle = 7
                self.send_angle(angle)
                
            elif imu_angle < 10:
                angle = 18
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
            
            
    def go_straight(self, angle_lane_keeping):
        # angle_lane_keeping = np.clip(angle_lane_keeping, -5, 5)

        # self.send_angle(angle_lane_keeping, send_attempt=100)
        # # self.send_speed(30)
        # time.sleep(0.5)
        # self.send_angle(0,send_attempt=10)

        t = time.time()
        self.send_speed(40)
        imu_angle = self.imu_handler.get_yaw()   
        while time.time()-t <= 3.5:
            imu_angle = self.imu_handler.get_yaw()   
            print(-imu_angle*0.5)
            self.send_angle(-imu_angle*0.5)
            time.sleep(0.1)
            
                            
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
                self.send_angle(angle)
            
            elif imu_angle > -20:
                angle = -15
                self.send_angle(angle)
   
            elif imu_angle > -25:
                angle = -16
                self.send_angle(angle)

            elif imu_angle > -55:
                angle = -18
                self.send_angle(angle)
     
            else:
                angle = -23
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
            if imu_angle > -10:
                angle = -5
                self.send_angle(-7)

            elif imu_angle > -15:
                angle = -8
                self.send_angle(angle)
            
            elif imu_angle > -20:
                angle = -10
                self.send_angle(angle)
   
            elif imu_angle > -25:
                angle = -13
                self.send_angle(angle)

            elif imu_angle > -55:
                angle = -15
                self.send_angle(angle)
     
            else:
                angle = -23
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

            

            