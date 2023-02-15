from src.utils.utils_function import setSpeed, setAngle, EnablePID, MoveDistance

class InterceptionHandler:
    def __init__(self):
        self.min_intercept_length = 100
        self.max_intercept_gap = 40

        pass

    def is_intercept(self, intercept_length, intercept_gap):
        if intercept_length >= self.min_intercept_length and intercept_gap < self.max_intercept_gap:
            return True, self.log_messagge(False, 0, 0, 0, 0, 0, intercept_length, intercept_gap)
        return False, self.log_messagge(False, 0, 0, 0, 0, 0, intercept_length, intercept_gap)


    def turn_right(self, imu_angle, CarHandler=None):
        if imu_angle < 5:
            status, mess_speed = CarHandler.setSpeed(30)
            status, mess_angle = CarHandler.setAngle(10)
            return self.log_messagge(True, imu_angle, 10, 30, mess_speed, mess_angle), False
        
        elif imu_angle < 7:
            status, mess_speed = CarHandler.setSpeed(30)
            status, mess_angle = CarHandler.setAngle(14)
            return self.log_messagge(True, imu_angle, 14, 30, mess_speed, mess_angle), False
        
        elif imu_angle < 9:
            status, mess_speed = CarHandler.setSpeed(30)
            status, mess_angle = CarHandler.setAngle(15)
            return self.log_messagge(True, imu_angle, 15, 30, mess_speed, mess_angle), False
        
        elif imu_angle < 10:
            status, mess_speed = CarHandler.setSpeed(30)
            status, mess_angle = CarHandler.setAngle(17)
            return self.log_messagge(True, imu_angle, 17, 30, mess_speed, mess_angle), False
        
        elif imu_angle < 15:
            status, mess_speed = CarHandler.setSpeed(30)
            status, mess_angle = CarHandler.setAngle(19)
            return self.log_messagge(True, imu_angle, 19, 30, mess_speed, mess_angle), False
        
        elif imu_angle < 20:
            status, mess_speed = CarHandler.setSpeed(30)
            status, mess_angle = CarHandler.setAngle(19)
            return self.log_messagge(True, imu_angle, 19, 30, mess_speed, mess_angle), False
        
        elif imu_angle < 25:
            status, mess_speed = CarHandler.setSpeed(30)
            status, mess_angle = CarHandler.setAngle(20)
            return self.log_messagge(True, imu_angle, 20, 30, mess_speed, mess_angle), False
        
        
        elif imu_angle < 30:
            status, mess_speed = CarHandler.setSpeed(30)
            status, mess_angle = CarHandler.setAngle(22)
            return self.log_messagge(True, imu_angle, 22, 30, mess_speed, mess_angle), False
        
        elif imu_angle < 75:
            status, mess_speed = CarHandler.setSpeed(30)
            status, mess_angle = CarHandler.setAngle(23)
            return self.log_messagge(True, imu_angle, 23, 30, mess_speed, mess_angle), False
        
        else:
            return "\n \n ***************************************************** \n" + \
                        "\n \nFINISH TURN RIGHT\n" + \
                        "\n \n ***************************************************** \n", True

    def turn_left(self, imu_angle, CarHandler=None):
        if imu_angle > -5:
            status, mess_speed = CarHandler.setSpeed(40)
            status, mess_angle = CarHandler.setAngle(-5)
            return self.log_messagge(True, imu_angle, -6, 30, mess_speed, mess_angle), False
        
        elif imu_angle > -7:
            status, mess_speed = CarHandler.setSpeed(40)
            status, mess_angle = CarHandler.setAngle(-5)
            return self.log_messagge(True, imu_angle, -7, 30, mess_speed, mess_angle), False
        
        elif imu_angle > -9:
            status, mess_speed = CarHandler.setSpeed(40)
            status, mess_angle = CarHandler.setAngle(-7)
            return self.log_messagge(True, imu_angle, -10, 30, mess_speed, mess_angle), False
        
        elif imu_angle > -10:
            status, mess_speed = CarHandler.setSpeed(40)
            status, mess_angle = CarHandler.setAngle(-10)
            return self.log_messagge(True, imu_angle, -13, 30, mess_speed, mess_angle), False
        
        elif imu_angle > -15:
            status, mess_speed = CarHandler.setSpeed(40)
            status, mess_angle = CarHandler.setAngle(-15)
            return self.log_messagge(True, imu_angle, -17, 30, mess_speed, mess_angle), False
        
        elif imu_angle > -20:
            status, mess_speed = CarHandler.setSpeed(30)
            status, mess_angle = CarHandler.setAngle(-17)
            return self.log_messagge(True, imu_angle, -18, 30, mess_speed, mess_angle), False
        
        elif imu_angle > -25:
            status, mess_speed = CarHandler.setSpeed(40)
            status, mess_angle = CarHandler.setAngle(-13)
            return self.log_messagge(True, imu_angle, -19, 30, mess_speed, mess_angle), False
        
        
        elif imu_angle > -35:
            status, mess_speed = CarHandler.setSpeed(40)
            status, mess_angle = CarHandler.setAngle(-15)
            return self.log_messagge(True, imu_angle, -21, 30, mess_speed, mess_angle), False
        
        elif imu_angle > -45:
            status, mess_speed = CarHandler.setSpeed(30)
            status, mess_angle = CarHandler.setAngle(-15)
            return self.log_messagge(True, imu_angle, -21, 30, mess_speed, mess_angle), False
        
        elif imu_angle > -55:
            status, mess_speed = CarHandler.setSpeed(30)
            status, mess_angle = CarHandler.setAngle(-18)
            return self.log_messagge(True, imu_angle, -21, 30, mess_speed, mess_angle), False
        
        elif imu_angle > -75:
            status, mess_speed = CarHandler.setSpeed(30)
            status, mess_angle = CarHandler.setAngle(-23)
            return self.log_messagge(True, imu_angle, -23, 30, mess_speed, mess_angle), False
        
        else:
            return "\n \n ***************************************************** \n" + \
                        "\n \nFINISH TURN LEFT\n" + \
                        "\n \n ***************************************************** \n", True


    def log_messagge(self, is_handle, imu_angle, angle, speed, mess_speed = "", mess_angle = "", intercept_length=0, intercept_gap=0):
        if is_handle:
            return "Intercept Handler - IMU angle: " + str(imu_angle) + " - Run angle: " + str(angle) \
                + " " + mess_angle + " - speed: " + str(speed) + " " + mess_speed 
        
        return "Intercept Handler - intercept length: " + str(intercept_length) + " - intercept gap: " + str(intercept_gap) + "\n"
            