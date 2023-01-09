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

from src.utils.utils_function import display_lines, get_point

class LaneDebugging:
    # ===================================== INIT =========================================
    def __init__(self):
        pass

    def visualize(self, data):
        angle = data["angle"]
        image_size = data["image_size"]
        lines = data["lines"]
        left_lines = data["left_lines"]
        right_lines = data["right_lines"]
        filtered_left_lines = data["filtered_left_lines"]
        filtered_right_lines = data["filtered_right_lines"]
        error_point = data["error_point"]
        left_average_fit, right_average_fit = data["fit_data"]


        lines_image = np.zeros(image_size)
        if lines is not None:
            lines_image = display_lines(lines_image, [line[0] for line in lines], 255)


        left_lines_image = np.zeros(image_size)
        left_lines_image = display_lines(left_lines_image, left_lines, 255)
        
        right_lines_image = np.zeros(image_size)
        right_lines_image = display_lines(right_lines_image, right_lines, 255)

        filtered_left_lines_image = np.zeros(image_size)
        filtered_left_lines_image = display_lines(filtered_left_lines_image, filtered_left_lines, 255)

        filtered_right_lines_image = np.zeros(image_size)
        filtered_right_lines_image = display_lines(filtered_right_lines_image, filtered_right_lines, 255)

        angle_visualized_image = np.zeros(image_size)
        if left_average_fit is not None:
            x1 = get_point(left_average_fit, image_size[0])
            x2 = get_point(left_average_fit, image_size[0] * 0.5)

            angle_visualized_image = cv2.line(angle_visualized_image, (x1, image_size[0]), (x2, int(image_size[0]* 0.5)), 255, 2)
        if right_average_fit is not None:
            x1 = get_point(right_average_fit, image_size[0])
            x2 = get_point(right_average_fit, image_size[0] * 0.5)
            angle_visualized_image = cv2.line(angle_visualized_image, (x1, image_size[0]), (x2, int(image_size[0] * 0.5)), 255, 2)


        if error_point[0] != None:
            angle_visualized_image = cv2.line(angle_visualized_image, error_point, (int(image_size[1] * 0.5), image_size[0]), 125, 2)
            
        angle_visualized_image = cv2.putText(angle_visualized_image, str(int(angle)), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, \
            1, 255, 1, cv2.LINE_AA)

        visualize_image = np.vstack([filtered_right_lines_image, filtered_left_lines_image, angle_visualized_image])

        return lines_image, visualize_image
