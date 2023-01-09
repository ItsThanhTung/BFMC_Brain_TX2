import math
import numpy as np

def gauss(x, x0, sigma):
            return  (1/(math.pi * sigma ** 2) ** 0.5) * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))


def scale_up(value, sigma, min_value, max_value):
    max_ = gauss(0, 0, sigma)
    value = gauss(value, 0, sigma)
    return value/max_ * (max_value - min_value) + min_value


def calculate_speed(angle, max_speed=0.3):
    ratio = scale_up(angle, 23, 0.5, 1)
    return ratio * max_speed


def setSpeed (outP, Speed:float):
    data = {
        "action": '1',
        "speed": Speed/100
    }
    outP.send(data)


def setAngle (outP , Angle:float):
    data = {
        "action": '2',
        "steerAngle": Angle
    }
    outP.send(data)


def EnablePID (outP , Enable = True):
    data = {
        "action": '4',
        "activate": Enable
    }
    outP.send(data)