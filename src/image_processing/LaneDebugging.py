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

import numpy as np
import cv2

from src.utils.utils_function import display_lines, get_point, display_points

class LaneDebugging:
    # ===================================== INIT =========================================
    def __init__(self):
        pass

    def visualize_lane_keeping(self, data):
        angle = data["angle"]
        left_points = data["left_points"] 
        right_points = data["right_points"] 
        left_point = data["left_point"] 
        right_point = data["right_point"] 
        middle_point = data["middle_point"] 
        image_size = data["image_size"]

        visualize_image = np.zeros(image_size)
        left_points_image = np.zeros(image_size)
        if len(left_points) != 0:
            left_points_image = display_points(left_points, left_points_image)
            visualize_image = display_points(left_points, visualize_image)

        right_points_image = np.zeros(image_size)
        if len(right_points) != 0:
            right_points_image = display_points(right_points, right_points_image)
            visualize_image = display_points(right_points, visualize_image)
        

        visualize_image = cv2.line(visualize_image, left_point, right_point, 255, 1)
        visualize_image = cv2.line(visualize_image, (160, 240), middle_point, 255, 1)

        visualize_image = cv2.putText(visualize_image, str(int(angle)), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, \
            1, 255, 1, cv2.LINE_AA)

        visualize_image = np.vstack([right_points_image, left_points_image, visualize_image])

        return {"lane_keeping_visualize_image" : visualize_image}

    def visualize_intercept_detection(self, data):
        image_size = data["image_size"]
        max_points = data["max_points"]

        point_image = np.zeros(image_size)
        point_image = display_points(max_points, point_image)
        return {"point_image" : point_image}
              

