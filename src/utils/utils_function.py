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


def setSpeed(outP, Speed:float):
    data = {
        "action": '1',
        "speed": Speed/100
    }
    outP.send(data)


def setAngle(outP, Angle:float):
    data = {
        "action": '2',
        "steerAngle": float(Angle)
    }
    outP.send(data)

def Brake(outP , Angle = 0):
    data = {
        "action": '3',
        "brake (steerAngle)": Angle
    }
    outP.send(data)

def EnablePID(outP , Enable = True):
    data = {
        "action": '4',
        "activate": Enable
    }
    outP.send(data)

def MoveDistance(outP , Distance, Speed):
    print("run distance")
    if(np.abs(Distance) > 1):
        print("UTIL Move ERR: Distance out of Range")
    data = {
        "action": '7',
        "distance": Distance,
        "speed": Speed
    }
    outP.send(data)

def GetDistanceStatus(inP, timeout = 0.1):
    Status = -2
    Mess = ""
    if inP.poll(timeout):
        buff = inP.recv()
        print("buff", buff)
    else:
        print("Receive Timeout")
        return -3, "Receive Timeout"
    # print("Buff ", buff)
    Packet = buff[3:-2].split(";", 1)
    # print("Packet ", Packet)
    if len(Packet) == 2:
        Status, Mess = int(Packet[0]), Packet[1]
    return Status, Mess

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


def connect_lines_y_axis(lines, tolerance=0):
    min_index = np.argsort(lines[:, 1])

    sorted_lines = lines[min_index]

    min_y = sorted_lines[0, 1]
    max_y = sorted_lines[0, 3]
    max_length = max_y - min_y
    current_max_lines = [sorted_lines[0]]
    max_lines = current_max_lines
    
    for line in sorted_lines[1:]:
        line_min_y = min(line[1], line[3])
        line_max_y = max(line[1], line[3])
        if line_min_y < max_y + tolerance:
            if line_max_y > max_y:
                max_y = line_max_y
                current_max_lines.append(line)
                if max_y - min_y > max_length:
                    max_length = max_y - min_y
                    max_lines = current_max_lines
            
        else:
            min_y = line_min_y
            max_y = line_max_y
            current_max_lines = [line]
            if max_y - min_y > max_length:
                max_length =  max_y - min_y
                max_lines = current_max_lines

    return np.array(max_lines), max_length


def connect_lines_x_axis(lines, tolerance=0):
    min_index = np.argsort(lines[:, 0])

    sorted_lines = lines[min_index]

    min_x = sorted_lines[0, 0]
    max_x = sorted_lines[0, 2]
    max_length = max_x - min_x
    current_max_lines = [sorted_lines[0]]
    max_lines = current_max_lines

    for line in sorted_lines[1:]:
        if line[0] < max_x + tolerance:
            if line[2] > max_x:
                max_x = line[2]
                current_max_lines.append(line)
                if max_x - min_x > max_length:
                    max_length = max_x - min_x
                    max_lines = current_max_lines
            
        else:
            min_x = line[0]
            max_x = line[2]
            current_max_lines = [line]
            if max_x - min_x > max_length:
                max_length =  max_x - min_x
                max_lines = current_max_lines

    return np.array(max_lines), max_length