import cv2
import numpy as np


from src.image_processing.ImagePreprocessing import ImagePreprocessing
from src.image_processing.LaneKeeping import LaneKeeping
from src.utils.utils_function import load_config_file

opt = load_config_file("main_rc.json")
ImagePreprocessor = ImagePreprocessing(opt)
LaneKeeper = LaneKeeping(opt, True)

vid = cv2.VideoCapture(r'D:\bosch\lane_keeping\video.avi')

def display_points(points, image):
    if points is not None:
        for point in points:
            image = cv2.circle(image, point, 1, 255, 2)
    
    return image



while vid.isOpened():  
    ret, frame = vid.read()

    if ret:
        frame = cv2.resize(frame, (320, 240))
        new_combined_binary, sybinary, image_ff = ImagePreprocessor.process_image(frame)
        speed, angle, state, debug_data = LaneKeeper.lane_keeping_v2(new_combined_binary)

        left_points = debug_data["left_points"] 
        right_points = debug_data["right_points"] 
        left_point = debug_data["left_point"] 
        right_point = debug_data["right_point"] 
        middle_point = debug_data["middle_point"] 

        left_points_image = np.zeros_like(new_combined_binary)
        if len(left_points) != 0:
            left_points_image = display_points(left_points, left_points_image)

        right_points_image = np.zeros_like(new_combined_binary)
        if len(right_points) != 0:
            right_points_image = display_points(right_points, right_points_image)
        

        new_combined_binary = cv2.line(new_combined_binary, left_point, right_point, 255, 1)
        new_combined_binary = cv2.line(new_combined_binary, (160, 240), middle_point, 255, 1)
    
        
        
        # points_image = display_points(left_points, points_image)
        # points_image = display_points(right_points, points_image)

        cv2.imshow("frame", frame)
        cv2.imshow("left_points_image", left_points_image)
        cv2.imshow("right_points_image", right_points_image)
        cv2.imshow("roi_edge_image", new_combined_binary)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break