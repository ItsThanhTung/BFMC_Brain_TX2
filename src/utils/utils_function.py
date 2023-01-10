import math
import numpy as np
import json
import cv2

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

def Brake (outP , Angle = 0):
    data = {
        "action": '3',
        "brake (steerAngle)": Angle
    }
    outP.send(data)

def EnablePID (outP , Enable = True):
    data = {
        "action": '4',
        "activate": Enable
    }
    outP.send(data)

def MoveDistance (outP , Distance, Speed):
    if(np.abs(Distance) > 1):
        print("UTIL Move ERR: Distance out of Range")
    data = {
        "action": '7',
        "distance": Distance,
        "speed": Speed
    }
    outP.send(data)

def load_config_file(config_file):
    with open(config_file, "r") as jsonfile:
        data = json.load(jsonfile) # Reading the file
        print("Read successful")
        jsonfile.close()
    return data


def get_point(fit, y):
    return int((y - fit[1])/fit[0])


def display_lines(img, lines, color=(255,0,0)):
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line
            img = cv2.line(img,(x1,y1),(x2,y2),color, 1)
    return img


def display_points(points, image):
    if points is not None:
        for point in points:
            image = cv2.circle(image, point, 1, 255, 2)
    
    return image