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


    def get_middle_point(self, points):
        if len(points) > 0:
            points = np.array(points)
            mean_x = np.mean(points[:, 0])
            anchor_idx = np.argmin(np.abs(mean_x - points[:, 0]))                           # find close point to the mean

            middle_point = points[anchor_idx, :]                                
            middle_points = points[np.abs(middle_point[0] - points[:, 0]) < 30]             # For point have the distance to the mean point > 30, discard it
            middle_point = np.mean(middle_points, axis = 0, dtype=np.int32)                 # The middle point is calculated by the mean of the remaining point
            return middle_point, middle_points
        
        else:
            return None, None

    def find_left_right_lanes(self, roi_edge_image):
        image_height = roi_edge_image.shape[0]
        image_width = roi_edge_image.shape[1]

        white_pixel_idx = np.argwhere(roi_edge_image == 255)[:, ::-1]                       # Get index of all white pixel
        white_pixel_idx  = white_pixel_idx[np.argsort(white_pixel_idx[::, 0])][::-1]        # sort all index in descending order of image's height
        
        white_map = defaultdict(list)                                                       # Create dict map where key: point_x[0] value                                    
        for point in white_pixel_idx:                                                       # value is the list of all pixel have the same point_x[0] 
            white_map[point[1]].append(point)                                               # [point_1, point_2, point_3,...]

        left_anchor = []                                                                    # The lowest pixel of left lane
        right_anchor = []                                                                   # The lowest pixel of right lane

        # Find the anchor of left or right line/ depend on which lane is lower
        for anchor_height in range(image_height-1-30, 0, self.opt["anchor_step"]):
            if white_map[anchor_height] != []:
                points = white_map[anchor_height]
                for point in points:
                    if point[0] < image_width//2:                      
                        left_anchor.append(point)
                    elif point[0] > image_width//2:
                        right_anchor.append(point)
                        
                if len(left_anchor) > 0 or len(right_anchor) > 0:
                    break
        
        # For all achor points that have the same height (point[0]), we find the middle point (point[1])
        left_anchor, _ = self.get_middle_point(left_anchor)
        right_anchor, _ = self.get_middle_point(right_anchor)

        if left_anchor is None:                                                             # If we could not find left or right point, init the dummy point
            left_anchor = [-1, anchor_height]               

        if right_anchor is None:
            right_anchor = [320, anchor_height]

        left_points = []
        right_points = []

        # From anchor height, we traverse back to the top of the image
        # we separate left and right point based on the distance to left anchor and right anchor.

        for height in range(anchor_height -1, 120, self.opt["step"]):
            if white_map[height] != []:
                if right_anchor[0] == 320:
                    right_anchor[1] = height

                if left_anchor[0] == -1:
                    left_anchor[1] = height

                points = white_map[height]
                current_left_anchor = []
                current_right_anchor = []

                for point in points:
                    # calculate the distance to the left anchor and to the right anchor
                    left_offset = abs(point[0] - left_anchor[0]) * self.opt["x_ratio"] \
                                    + abs(point[1] - left_anchor[1]) * self.opt["y_ratio"]    
                    
                    right_offset = abs(point[0] - right_anchor[0]) * self.opt["x_ratio"] \
                                    + abs(point[1] - right_anchor[1]) * self.opt["y_ratio"]

                    if left_offset < right_offset and abs(point[1] - left_anchor[1]) < self.opt["y_dist"]:
                        if  abs(point[0] - left_anchor[0]) < self.opt["x_dist"]:                # if anchor is not dummy anchor, we compare x_axis
                            current_left_anchor.append(point)
                        elif left_anchor[0] == -1:
                            current_left_anchor.append(point)

                    elif left_offset > right_offset and abs(point[1] - right_anchor[1]) < self.opt["y_dist"]:
                        if  abs(point[0] - right_anchor[0]) < self.opt["x_dist"]:             # if anchor is not dummy anchor, we compare x_axis
                            current_right_anchor.append(point)
                        elif right_anchor[0] == 320:
                            current_right_anchor.append(point)
                        # else:
                        #     current_right_anchor.append(point)

                # find the middle point
                left_middle_point, left_middle_points = self.get_middle_point(current_left_anchor)
                right_middle_point, right_middle_points = self.get_middle_point(current_right_anchor)

                # update the new anchor point for left and right lane 
                if left_middle_point is not None:
                    left_anchor = left_middle_point
                    for point in left_middle_points:
                        left_points.append(point)
                
                if right_middle_point is not None:
                    right_anchor = right_middle_point
                    for point in right_middle_points:
                        right_points.append(point)

        return np.array(left_points), np.array(right_points)


    def fit_2d(self, fit, pointX):                                                          # F(x) = ax^2 + bx + c, fit = [a, b, c]
        pointY =  int(fit[2] + fit[1] * pow(pointX, 1) + fit[0] * pow(pointX, 2))
        return pointY
    

    def lane_keeping(self, edge_image, object_info):
        if object_info is not None:
            for object_box in object_info:
                if object_box.clss_max == 'car':
                    tlwh=object_box.tlwh/2  # scale to 240 320
              
                    edge_image=cv2.rectangle(edge_image, (int(tlwh[0]),int(tlwh[1])), (int(tlwh[0]+tlwh[2]),int(tlwh[1]+tlwh[3])), 0, -1)


        image_size = edge_image.shape
        h = image_size[0]
        w = image_size[1]

        left_points, right_points = self.find_left_right_lanes(edge_image)              # Get left lane and right lane
        
        # Init dummy variables
        left_point_x, left_point_y = 0, 0           
        right_point_x, right_point_y = 0, w - 1
        point_y = 0
        
        if len(left_points) != 0:                                                           # If there is a left lane
            left_points = np.array(left_points)

            # If the height of lane is enough
            if abs(np.max(left_points[:, 1]) - np.min(left_points[:, 1])) > self.opt["min_length"]:             
                left_points = left_points                                                   # Keep the left lane
            else:
                left_points = []                                                            # Else remove short left lane

        if len(right_points) != 0:                                                          # If there is a right lane
            right_points = np.array(right_points)                       

            # If the height of lane is enough
            if abs(np.max(right_points[:, 1]) - np.min(right_points[:, 1])) > self.opt["min_length"]:           
                right_points = right_points                                                 # Keep the right lane
            else:
                right_points = []                                                           # Else remove short right lane

        if len(left_points) == 0 and len(right_points) == 0:                                # If there is no lane
            state = self.prev_state                                                         # Remain the same angle and the same state
            angle = self.prev_angle
            middle_point_x = w//2 

        elif len(left_points) == 0 and len(right_points) != 0:                              # If there is only right lane
            state = -1                                                                      # Turn max angle to the left                   
            angle = -23                                                                     # Assign state = -1 means missing left lane   
            middle_point_x = 0
        
        elif len(left_points) != 0 and len(right_points) == 0:                              # If there is only left lane
            state = 1                                                                       # Turn max angle to the right   
            angle = 23                                                                      # Assign state = 1 means missing right lane   
            middle_point_x = w-1
        
        else:
            state = 0                                                                       # If there are 2 lanes, Assign state = 0 means fully visible
            left_line = np.polyfit(left_points[:,1], left_points[:, 0], 2)                  # Find the 2d polynomial function for all left point
            
            # Get 1st quartile point between max height pixel and min height pixel in left lane
            left_point_y = int(abs(np.max(left_points[:, 1]) - np.min(left_points[:, 1])) * self.opt["middle_point_ratio"] \
                                                                                                + np.min(left_points[:, 1]))

            right_line = np.polyfit(right_points[:,1], right_points[:, 0], 2)               # Find the 2d polynomial function for all right point
            # Get 1st quartile point between max height pixel and min height pixel in left lane
            right_point_y = int(abs(np.max(right_points[:, 1]) - np.min(right_points[:, 1])) * self.opt["middle_point_ratio"] \
                                                                                                + np.min(right_points[:, 1]))

            # Get the middle height between left_point_y and right_point_y
            point_y = int((left_point_y  + right_point_y)/2)

            # Find the x value of 2 1st quartile point from left, right, and the middle point
            left_point_x = self.fit_2d(left_line, left_point_y)
            right_point_x = self.fit_2d(right_line, right_point_y)
            middle_point_x = int((left_point_x + right_point_x)/2)

            dx = w//2 - middle_point_x                                                      # Calculate error angle 
            if dx != 0:
                dy = h - point_y
                angle =  math.atan(dy/dx) * 180 / math.pi
                if angle >= 0:
                    angle = - (90 - angle)
                else:
                    angle = 90 +  angle
            else:
                angle = 0

            angle = angle * self.opt["angle_scale_ratio"]                                   # Scale angle to the small value to maintain the stability    
            
        angle = np.clip(angle, -23, 23)                                                     
        speed = calculate_speed(angle, max_speed = 100)                                     # Calculate speed using gaussian function

        if self.debug:
            debug_data = {"angle": int(angle),
                        "image_size" : [int(h), int(w)],
                        "left_points" : [list([int(point[0]), int(point[1])]) for point in left_points],
                        "right_points" : [list([int(point[0]), int(point[1])]) for point in right_points],
                        "left_point" : [left_point_x, left_point_y],
                        "right_point" : [right_point_x, right_point_y],
                        "middle_point" : [middle_point_x, point_y]}
        
            return speed, angle, state, debug_data

        lane_data = { "image_size" : [int(h), int(w)],
                        "left_points" : left_points,
                        "right_points" : right_points,
                        "left_point" : [left_point_x, left_point_y],
                        "right_point" : [right_point_x, right_point_y]}
        
        
        return speed, angle, state, lane_data
        
        



