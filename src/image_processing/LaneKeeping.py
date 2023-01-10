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

import time
import numpy as np
import math
import cv2
from src.utils.utils_function import calculate_speed
from collections import defaultdict
class LaneKeeping:
    # ===================================== INIT =========================================
    def __init__(self, opt, debug):
        self.opt = opt["LANE_KEEPING"]
        self.debug = debug
        self.prev_angle = 0
        self.prev_state = 0


    def region_of_interest(self, frame):
        height = frame.shape[0]
        width = frame.shape[1]
        mask = np.zeros_like(frame)

        region_of_interest_vertices = np.array([[   (0, height-1),
                                                    (self.opt["roi"]["left"]*width, height * self.opt["roi"]["upper"]),
                                                    (self.opt["roi"]["right"]*width, height * self.opt["roi"]["upper"]),
                                                    (width - 1, height-1)]], np.int32)

        cv2.fillPoly(mask, region_of_interest_vertices, 255)
        masked_image = cv2.bitwise_and(frame, mask)
        return masked_image


    def filter_lines(self, lines, image_size):
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
                    if abs(line[2] - line[0]) > image_size[1] * self.opt["filter_lines"]["hslope"]: 
                        horizontal_lines.append(line)
                else:
                    if max(line[0], line[2]) <= middle_y * self.opt["filter_lines"]["left_bound"]: #and slope < 0:  # or min(line[0], line[2]) <= middle_y * 0.3:
                        left_lines.append(line)
                    elif (min(line[0], line[2]) > middle_y * self.opt["filter_lines"]["right_bound"]): # and slope > 0: #or max(line[0], line[2]) > middle_y * 0.7:
                        right_lines.append(line)
        
        return np.array(left_lines), np.array(right_lines), np.array(horizontal_lines)


    def is_length_enough(self, lines, img_size):
        if lines.shape[0] == 0:
            return lines

        max_x = max(np.max(lines[:,0]), np.max(lines[:,2]))
        min_x = min(np.min(lines[:,0]), np.min(lines[:,2]))

        max_y = max(np.max(lines[:,1]), np.max(lines[:,3]))
        min_y = min(np.min(lines[:,1]), np.min(lines[:,3]))

        if np.abs(max_x - min_x) > self.opt["limited_length"]["x"] * img_size[1] \
                and np.abs(max_y - min_y) > self.opt["limited_length"]["y"] * img_size[0]:
            return lines

        else:
            return np.array([])

    
    def average_slope_intercept(self, lines):
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


    def get_farest_point(self, lines):
        if lines is not None:
            all_x_point = []
            for line in lines:
                _, y1, _, y2 = line
                all_x_point.append(min(y1, y2))
            return min(all_x_point) if len(all_x_point) != 0 else 0
        
        return 0

    
    def get_point(self, y, fit):
        if fit is not None:
            slope = fit[0]
            intercept = fit[1]
            x = int((y - intercept)/slope)
            return [x, y]
        
        return None


    def calculate_angle(self, left_lines, right_lines, image_size):
        h = image_size[0]
        w = image_size[1]
        fit_average_left = self.average_slope_intercept(left_lines)
        fit_average_right = self.average_slope_intercept(right_lines)

        farest_point_left = self.get_farest_point(left_lines)
        farest_point_right = self.get_farest_point(right_lines)

        min_farest_point = max(farest_point_left, farest_point_right)
        left_point = self.get_point(min_farest_point, fit_average_left)
        right_point = self.get_point(min_farest_point, fit_average_right)
        middle_point = None

        if left_point is None and right_point is not None:
            if self.prev_state == 1:
                print('right  - left')
                angle = 23
                state = self.prev_state
            else:
                state = -1
                print("left")
                middle_point = (right_point[0] + 0) //2
                angle = -23

        elif left_point is not None and right_point is None:
            if self.prev_state == -1:
                print('left  - right')
                angle = -23
                state = self.prev_state
            else:
                state = 1
                middle_point = (left_point[0] + w - 1) //2
                angle = 23
        
        elif left_point is None and right_point is None:
            state = self.prev_state
            angle = self.prev_angle

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


    def lane_keeping(self, edge_image):
        roi_edge_image = self.region_of_interest(edge_image)
        lines = cv2.HoughLinesP(roi_edge_image, rho=4, theta=np.pi/60, threshold=50, lines=np.array([]), minLineLength= 10, maxLineGap=10)
        left_lines, right_lines, _ = self.filter_lines(lines, roi_edge_image.shape)

        filtered_left_lines = self.is_length_enough(left_lines, roi_edge_image.shape)
        filtered_right_lines = self.is_length_enough(right_lines, roi_edge_image.shape)

        angle, state, error_point, fit_data = self.calculate_angle(filtered_left_lines, filtered_right_lines, roi_edge_image.shape)
        angle = np.clip(angle, -23, 23)
        speed = calculate_speed(angle, max_speed = 100)

        self.prev_state  = state
        self.angle  = angle

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

    def convert_line_to_point(self, lines):
        if lines.shape[0] == 0:
            return None
        else:
            points = []
            for line in lines:
                pointX = int((line[0] + line[2])/2)
                pointY = int((line[1] + line[3])/2)
                points.append([pointX, pointY])
            return np.array(points)


    def find_anchor(self, white_pixel_idx):
        white_pixel_idx = white_pixel_idx[np.argsort(white_pixel_idx[::, 0])]

        return white_pixel_idx[::-1]

    def get_middle_point(self, points, get_closet=False):
        if len(points) > 0:
            points = np.array(points)
            mean_x = np.mean(points[:, 0])
            anchor_idx = np.argmin(np.abs(mean_x - points[:, 0]))

            middle_point = points[anchor_idx, :]

            
            middle_points = points[np.abs(middle_point[0] - points[:, 0]) < 30]
            middle_point = np.mean(middle_points, axis = 0, dtype=np.int32) 
            if get_closet:
                return middle_point, middle_points
            return middle_point, None
        
        else:
            return None, None

    def find_left_right_lanes(self, roi_edge_image):
        white_pixel_idx = np.argwhere(roi_edge_image == 255)[:, ::-1]
        white_pixel_idx  = self.find_anchor(white_pixel_idx)
        
        white_map = defaultdict(list)
        for point in white_pixel_idx:
            white_map[point[1]].append(point)

        left_anchor = []
        right_anchor = []
        for anchor_height in range(239, 0, -1):
            if white_map[anchor_height] != []:
                points = white_map[anchor_height]
                for point in points:
                    if point[0] < 160:
                        left_anchor.append(point)
                    elif point[0] > 160:
                        right_anchor.append(point)
                        
                if len(left_anchor) > 0 or len(right_anchor) > 0:
                    break
        
        left_anchor, _ = self.get_middle_point(left_anchor)
        right_anchor, _ = self.get_middle_point(right_anchor)

        if left_anchor is None:
            left_anchor = [-1, anchor_height]

        if right_anchor is None:
            right_anchor = [320, anchor_height]

        left_points = []
        right_points = []

        for height in range(anchor_height -1, 120, -3):
            if white_map[height] != []:
                if right_anchor[0] == 320:
                    right_anchor[1] = height

                if left_anchor[0] == -1:
                    left_anchor[1] = height

                points = white_map[height]
                current_left_anchor = []
                current_right_anchor = []

                for point in points:
                    left_offset = abs(point[0] - left_anchor[0]) * 0.8 + abs(point[1] - left_anchor[1]) * 0.2
                    right_offset = abs(point[0] - right_anchor[0]) * 0.8 + abs(point[1] - right_anchor[1]) * 0.2

                    if left_offset < right_offset and abs(point[1] - left_anchor[1]) < 20:
                        if left_anchor[0] != -1 and abs(point[0] - left_anchor[0]) < 50:
                            current_left_anchor.append(point)
                        else:
                            current_left_anchor.append(point)

                    elif left_offset > right_offset and abs(point[1] - right_anchor[1]) < 20:
                        if right_anchor[0] != 320 and abs(point[0] - right_anchor[0]) < 50:
                            current_right_anchor.append(point)
                        else:
                            current_right_anchor.append(point)

                left_middle_point, left_middle_points = self.get_middle_point(current_left_anchor, True)
                right_middle_point, right_middle_points = self.get_middle_point(current_right_anchor, True)


                ## update 
                if left_middle_point is not None:
                    left_anchor = left_middle_point
                    for point in left_middle_points:
                        left_points.append(point)
                
                if right_middle_point is not None:
                    right_anchor = right_middle_point
                    for point in right_middle_points:
                        right_points.append(point)

        return np.array(left_points), np.array(right_points)

    def fit_2d(self, fit, pointX):
        pointY =  int(fit[2] + fit[1] * pow(pointX, 1) + fit[0] * pow(pointX, 2))
        return pointY

    def lane_keeping_v2(self, edge_image):
        image_size = edge_image.shape
        h = image_size[0]
        w = image_size[1]

        roi_edge_image = self.region_of_interest(edge_image)
        left_points, right_points = self.find_left_right_lanes(roi_edge_image)

        left_point_x, left_point_y = 0, 0
        right_point_x, right_point_y = 0, w - 1
        point_y = 0
        
        if len(left_points) != 0:
            left_points = np.array(left_points)
            if abs(np.max(left_points[:, 1]) - np.min(left_points[:, 1])) > 50:
                left_points = left_points
            else:
                left_points = []

        if len(right_points) != 0:
            right_points = np.array(right_points)
            if abs(np.max(right_points[:, 1]) - np.min(right_points[:, 1])) > 50:
                right_points = right_points
            else:
                right_points = []

        if len(left_points) == 0 and len(right_points) == 0:
            state = self.prev_state
            angle = self.prev_angle
            middle_point_x = w//2

        elif len(left_points) == 0 and len(right_points) != 0:
            state = -1
            angle = -23
            middle_point_x = 0
        
        elif len(left_points) != 0 and len(right_points) == 0:
            state = 1
            angle = 23
            middle_point_x = w-1
        
        else:
            state = 0
            left_line = np.polyfit(left_points[:,1], left_points[:, 0], 2)
            left_point_y = int(abs(np.max(left_points[:, 1]) - np.min(left_points[:, 1])) * 0.25 + np.min(left_points[:, 1]))
            right_line = np.polyfit(right_points[:,1], right_points[:, 0], 2)
            right_point_y = int(abs(np.max(right_points[:, 1]) - np.min(right_points[:, 1])) * 0.25 + np.min(right_points[:, 1]))

            point_y = int((left_point_y  + right_point_y)/2)
            left_point_x = self.fit_2d(left_line, left_point_y)
            right_point_x = self.fit_2d(right_line, right_point_y)
            middle_point_x = int((left_point_x + right_point_x)/2)

            dx = w//2 - middle_point_x
            if dx != 0:
                dy = h - point_y
                angle =  math.atan(dy/dx) * 180 / math.pi
                if angle >= 0:
                    angle = - (90 - angle)
                else:
                    angle = 90 +  angle
            else:
                angle = 0
            angle = angle * 0.5
            
        angle = np.clip(angle, -23, 23)
        speed = calculate_speed(angle, max_speed = 100)

        if self.debug:
            debug_data = {"angle": angle,
                        "image_size": roi_edge_image.shape,
                        "left_points" : np.array(left_points),
                        "right_points" : np.array(right_points),
                        "left_point" : [left_point_x, left_point_y],
                        "right_point" : [right_point_x, right_point_y],
                        "middle_point" : [middle_point_x, point_y]}
            
            return speed, angle, state, debug_data

        return speed, angle, state, None


