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


    def turn_right(self, debug, outP=None):
        if not debug:
            setSpeed(outP, float(0))
            setAngle(outP , float(22))
            return self.log_messagge(True)
        else:
            return "Turn Right\n"

    def turn_left(self, debug, outP=None):
        if not debug:
            setSpeed(outP, float(0))
            setAngle(outP , float(22))
            return self.log_messagge(True)
        else:
            return "Turn left\n"

    def log_messagge(self, is_handle, intercept_length=0, intercept_gap=0):
        if is_handle:
            return "Intercept Handler - Run angle: " + str(22) + " - speed: " + str(0) + "\n"
        return "Intercept Handler - intercept length: " + str(intercept_length) + " - intercept gap: " + str(intercept_gap) + "\n"
            