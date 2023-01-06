# Copyright (c) 2019, Bosch Engineering Center Cluj and BFMC organizers
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE

import socket
import struct
import time
import numpy as np
import math

from threading import Thread

import cv2
from simple_pid import PID

from src.templates.workerprocess import WorkerProcess

class LaneKeepingProcess(WorkerProcess):
    pid = PID(Kp = 1.0, Ki = 1.45, Kd = 0.15, output_limits = [-23, 23])
    # ===================================== INIT =========================================
    def __init__(self, inPs, outPs, debug):
        """Process used for sending images over the network to a targeted IP via UDP protocol 
        (no feedback required). The image is compressed before sending it. 

        Used for visualizing your raspicam images on remote PC.
        
        Parameters
        ----------
        inPs : list(Pipe) 
            List of input pipes, only the first pipe is used to transfer the captured frames. 
        outPs : list(Pipe) 
            List of output pipes (not used at the moment)
        """

        self.debug = debug
        super(LaneKeepingProcess,self).__init__( inPs, outPs, debug)
        
    # ===================================== RUN ==========================================
    def run(self):
        """Apply the initializing methods and start the threads.
        """
        super(LaneKeepingProcess,self).run()

    # ===================================== INIT THREADS =================================
    def _init_threads(self):
        """Initialize the sending thread.
        """
        if self._blocker.is_set():
            return
        laneTh = Thread(name='LaneKeepingThread',target = self._run, args= (self.inPs[0], self.outPs))
        laneTh.daemon = True
        self.threads.append(laneTh)

    def laneKeeping(self, edge_image, old_angle, old_state):
        def region_of_interest(canny):
            height = canny.shape[0]
            width = canny.shape[1]
            mask = np.zeros_like(canny)

            region_of_interest_vertices = np.array([[   (0, height-1),
                                                        (0.3*width, height * 0.45),
                                                        (0.7*width, height * 0.45),
                                                        (width - 1, height-1)]], np.int32)

            cv2.fillPoly(mask, region_of_interest_vertices, 255)
            masked_image = cv2.bitwise_and(canny, mask)
            return masked_image

        def filter_lines(lines, image_size):
            left_lines = []
            right_lines = []
            horizontal_lines = []
           
            if lines is not None:
                middle_y = image_size[1]
                for line in lines:
                    line = line[0]
                    fit = np.polyfit([line[0],line[2]+1], [line[1],line[3]+1], 1)
                    slope = fit[0]
                    if np.abs(slope) < 0.3:
                        if abs(line[2] - line[0]) > image_size[1] * 0.075: 
                            horizontal_lines.append(line)
                    else:
                        if min(line[0], line[2]) <= middle_y * 0.45 and slope < 0:  # or min(line[0], line[2]) <= middle_y * 0.3:
                            left_lines.append(line)
                        elif (max(line[0], line[2]) > middle_y * 0.55) and slope > 0: #or max(line[0], line[2]) > middle_y * 0.7:
                            right_lines.append(line)
            
            return np.array(left_lines), np.array(right_lines), np.array(horizontal_lines)

        def is_length_enough(lines, img_size):
            if lines.shape[0] == 0:
                return lines
            max_x = max(np.max(lines[:,0]), np.max(lines[:,2]))
            min_x = min(np.min(lines[:,0]), np.min(lines[:,2]))

            max_y = max(np.max(lines[:,1]), np.max(lines[:,3]))
            min_y = min(np.min(lines[:,1]), np.min(lines[:,3]))

            if np.abs(max_x - min_x) > 0.05 * img_size[1] and np.abs(max_y - min_y) > 0.1 * img_size[0]:
                return lines
            else:
                return np.array([])

        def average_slope_intercept(image_size, lines):
            fit_point = []
            dist = []
            for line in lines:
                x1, y1, x2, y2 = line
                fit = np.polyfit([x1,x2+1], [y1,y2+1], 1)
                distance = ((y2-y1) **2 + (x2-x1)**2)**0.5
                slope = fit[0]
                intercept = fit[1]
                fit_point.append((slope, intercept))
                dist.append(distance)

            if len(fit_point) > 0:
                fit_average  = np.average(fit_point, weights= dist,axis=0)
            else:
                fit_average = None

            return fit_average

        def get_farest_point(lines):
            if lines is not None:
                all_x_point = []
                for line in lines:
                    _, y1, _, y2 = line
                    all_x_point.append(min(y1, y2))
                return min(all_x_point) if len(all_x_point) != 0 else 0
            
            return 0

        def get_point(y, fit):
            if fit is not None:
                slope = fit[0]
                intercept = fit[1]
                x = int((y - intercept)/slope)
                return [x, y]
            
            return None

        def calculate_angle(left_lines, right_lines, image_size):
            h = image_size[0]
            w = image_size[1]
            fit_average_left = average_slope_intercept((h, w), left_lines)
            fit_average_right = average_slope_intercept((h, w), right_lines)

            farest_point_left = get_farest_point(left_lines)
            farest_point_right = get_farest_point(right_lines)

            min_farest_point = max(farest_point_left, farest_point_right)
            left_point = get_point(min_farest_point, fit_average_left)
            right_point = get_point(min_farest_point, fit_average_right)
            middle_point = None

            if left_point is None and right_point is not None:
                if old_state == 1:
                    print('right  - left')
                    angle = 23
                    state = old_state
                else:
                    state = -1
                    print("left")
                    middle_point = (right_point[0] + 0) //2
                    angle = -23

            elif left_point is not None and right_point is None:
                if old_state == -1:
                    print('left  - right')
                    angle = -23
                    state = old_state
                else:
                    state = 1
                    middle_point = (left_point[0] + w - 1) //2
                    angle = 23
            
            elif left_point is None and right_point is None:
                state = old_state
                angle = old_angle

            else:
                state = 0
                middle_point = (left_point[0] + right_point[0]) //2
                dx = w//2 - middle_point
                if dx != 0:
                    dy = h - min_farest_point
                    angle =  math.atan(dy/dx) * 180 / math.pi
                    if angle >= 0:
                        angle = - (90 - angle)
                    else:
                        angle = 90 +  angle
                else:
                    angle = 0

            return angle, state, [middle_point, min_farest_point], [fit_average_left, fit_average_right]

        def gauss(x, x0, sigma):
            return  (1/(math.pi * sigma ** 2) ** 0.5) * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))

        def scale_up(value, sigma, min_value, max_value):
            max_ = gauss(0, 0, sigma)
            value = gauss(value, 0, sigma)
            return value/max_ * (max_value - min_value) + min_value

        def calculate_speed(angle, max_speed=0.3):
            ratio = scale_up(angle, 23, 0.5, 1)
            return ratio * max_speed

        roi_edge_image = region_of_interest(edge_image)
        lines = cv2.HoughLinesP(roi_edge_image, rho=9, theta=np.pi/60, threshold=50, lines=np.array([]), minLineLength= 4, maxLineGap=2)
        left_lines, right_lines, _ = filter_lines(lines, roi_edge_image.shape)

        filtered_left_lines = is_length_enough(left_lines, roi_edge_image.shape)
        filtered_right_lines = is_length_enough(right_lines, roi_edge_image.shape)

        angle, state, error_point, fit_data = calculate_angle(filtered_left_lines, filtered_right_lines, roi_edge_image.shape)
        angle = np.clip(angle, -23, 23)
        speed = calculate_speed(angle, max_speed = 100)

        if self.debug:
            debug_data = {"angle": angle,
                          "image_size": roi_edge_image.shape,
                          "lines" : lines,
                          "left_lines" : left_lines,
                          "right_lines" : right_lines,
                          "filtered_left_lines" : filtered_left_lines,
                          "filtered_right_lines" : filtered_right_lines,
                          "error_point" : error_point,
                          "fit_data" : fit_data}
            
            return speed, angle, state, debug_data

        return speed, angle, state, None

    def computeSteeringAngle(self, averaged_lines):
        return 0, 0


    def _run(self, inP, outP):
        """Obtains image, applies the required image processing and computes the steering angle value. 
        
        Parameters
        ----------
        inP  : Pipe
            Input pipe to read the frames from other process.
        outP : Pipe
            Output pipe to send the steering angle value to other process.

        """
        old_angle = 0
        state = 0
        # EnablePID(outP[0])

        while True:
            try:
                # Obtain image
                data = inP.recv()
                # Apply image processing

                edge_image = data["new_combined_binary"]
            
                speed, angle, state, debug_data = self.laneKeeping(edge_image, old_angle, state) 
                old_angle = angle
                # new_angle = self.pid(angle)
                print(angle)
                # setSpeed(outP[0], float(speed * 0.35))
                setSpeed(outP[0], float(0))
                setAngle(outP[0] , float(angle))

                if self.debug:
                    outP[1].send(debug_data)

            except Exception as e:
                print("Lane keeping error:")
                print(e)


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