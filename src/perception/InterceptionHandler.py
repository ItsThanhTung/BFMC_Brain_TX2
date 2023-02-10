from src.utils.utils_function import setSpeed, setAngle, EnablePID, MoveDistance

class InterceptionHandler:
    def __init__(self):
        self.min_intercept_length = 130
        self.max_intercept_gap = 40

        pass
    
    def is_intercept(self, intercept_length, intercept_gap):
        if intercept_length >= self.min_intercept_length and intercept_gap < self.max_intercept_gap:
            return True, self.log_messagge(False, intercept_length, intercept_gap)
        return False, self.log_messagge(False, intercept_length, intercept_gap)


    def turn_right(self, imu_angle, debug, outP=None):
        if not debug:
            if imu_angle < 90:
                setSpeed(outP, float(0))
                setAngle(outP , float(22))
                return self.log_messagge(True, imu_angle), False
            else:
                return "FINISH TURN RIGHT\n", True
        else:
            return "FINISH TURN RIGHT\n", True

    def turn_left(self, imu_angle, debug, outP=None):
        if not debug:
            if imu_angle > -90:
                setSpeed(outP, float(0))
                setAngle(outP , float(22))
                return self.log_messagge(True, imu_angle), False
            else:
                return "FINISH TURN LEFT\n", True
        else:
            return "FINISH TURN LEFT\n", True

    def log_messagge(self, is_handle, imu_angle, intercept_length=0, intercept_gap=0):
        if is_handle:
            return "Intercept Handler - IMU angle: ", str(imu_angle), " - Run angle: " + str(22) + " - speed: " + str(0) + "\n"
        
        return "Intercept Handler - intercept length: " + str(intercept_length) + " - intercept gap: " + str(intercept_gap) + "\n"
            