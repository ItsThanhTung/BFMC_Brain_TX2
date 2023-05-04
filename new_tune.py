import json
import numpy as np
import cv2
from src.utils.utils_function import load_config_file
from src.image_processing.LaneKeeping import LaneKeeping
from src.image_processing.ImagePreprocessing import ImagePreprocessing
import os
import shutil
def nothing(x):
    pass

cv2.namedWindow('frame')
#ImagePreprocessing
opt = load_config_file("main_rc.json")
cv2.createTrackbar("sobelx_upper", "frame", opt['LANE_PREPROCESSING']['sobel_x_thres'][1], 255, nothing)
cv2.createTrackbar("sobelx_lower", "frame", opt['LANE_PREPROCESSING']['sobel_x_thres'][0], 255, nothing)
cv2.createTrackbar("sobely_upper", "frame", opt['LANE_PREPROCESSING']['sobel_x_thres'][1], 255, nothing)
cv2.createTrackbar("sobely_lower", "frame", opt['LANE_PREPROCESSING']['sobel_x_thres'][0], 255, nothing)
cv2.createTrackbar("red_upper", "frame", opt['LANE_PREPROCESSING']['red_thres'][1], 255, nothing)
cv2.createTrackbar("red_lower", "frame", opt['LANE_PREPROCESSING']['red_thres'][0], 255, nothing)
cv2.createTrackbar("adaptive_block_size", "frame", opt['LANE_PREPROCESSING']['adaptive_block_size'], 255, nothing)
cv2.createTrackbar("adaptive_offset", "frame", abs(opt['LANE_PREPROCESSING']['adaptive_offset']), 255, nothing)
cv2.createTrackbar("dilate_kernel", "frame", opt['LANE_PREPROCESSING']['dilate_kernel'], 255, nothing)
cv2.createTrackbar("roi_mid", "frame",   int(opt['LANE_PREPROCESSING']['roi']['mid']*10), 10, nothing)
cv2.createTrackbar("roi_left", "frame",  int(opt['LANE_PREPROCESSING']['roi']['left']*10), 10, nothing)
cv2.createTrackbar("roi_right", "frame", int(opt['LANE_PREPROCESSING']['roi']['right']*10), 10, nothing)
cv2.createTrackbar("roi_upper", "frame", int(opt['LANE_PREPROCESSING']['roi']['upper']*10), 10, nothing)
is_cam = False
# "LANE_KEEPING": {
#     "middle_point": {
#       "longest_distance": 30
#     },
#     "anchor_step": -1,
#     "step": -3,
#     "x_ratio": 0.8,
#     "y_ratio": 0.2,
#     "y_dist": 100,
#     "x_dist": 50,
#     "min_length": 50,
#     "middle_point_ratio": 0.25,
#     "angle_scale_ratio": 0.4
#   },
#LaneKeeping
step_sign = 0 if int(opt['LANE_KEEPING']['anchor_step']) > 0 else 1
cv2.createTrackbar("anchor_step", "frame", -10, 10, nothing)



cv2.createTrackbar("step", "frame", abs(int(opt['LANE_KEEPING']['step'])), 10, nothing)
step_sign = 0 if int(opt['LANE_KEEPING']['step']) > 0 else 1
cv2.createTrackbar("step_sign", "frame", step_sign, 1, nothing)

cv2.createTrackbar("middle_point_ratio", "frame", 0, 10, nothing)
cv2.createTrackbar("angle_scale_ratio", "frame", 0, 10, nothing)
cv2.createTrackbar("x_ratio", "frame", 0, 10, nothing)
cv2.createTrackbar("y_ratio", "frame", 0, 10, nothing)
cv2.createTrackbar("y_dist", "frame", 10, 200, nothing)
cv2.createTrackbar("x_dist", "frame", 10, 200, nothing)


if is_cam:
    cam = cv2.VideoCapture("/dev/video0")
else:
    img_dir = '/home/topo/lane_data/lane_video_4/'
    img_files = os.listdir(img_dir)
    cur_frame = 0
while True:
    img_files = os.listdir(img_dir)
    img_files.sort()

    opt["LANE_PREPROCESSING"]["sobel_x_thres"] = [int(cv2.getTrackbarPos('sobelx_lower','frame')), int(cv2.getTrackbarPos('sobelx_upper','frame'))]
    opt["LANE_PREPROCESSING"]["sobel_y_thres"] = [int(cv2.getTrackbarPos('sobely_lower','frame')), int(cv2.getTrackbarPos('sobely_upper','frame'))]
    opt["LANE_PREPROCESSING"]["adaptive_block_size"] = int(cv2.getTrackbarPos('adaptive_block_size','frame')) if cv2.getTrackbarPos('adaptive_block_size','frame') % 2 == 1 else int(cv2.getTrackbarPos('adaptive_block_size','frame')) + 1
    opt["LANE_PREPROCESSING"]["adaptive_offset"] = -int(cv2.getTrackbarPos('adaptive_offset','frame'))
    opt["LANE_PREPROCESSING"]["red_thres"][0] = int(cv2.getTrackbarPos('red_lower','frame'))
    opt["LANE_PREPROCESSING"]["red_thres"][1] = int(cv2.getTrackbarPos('red_upper','frame'))
    opt["LANE_PREPROCESSING"]['roi']['mid'] = int(cv2.getTrackbarPos('roi_mid','frame'))/10
    opt["LANE_PREPROCESSING"]["roi"]["left"] = int(cv2.getTrackbarPos('roi_left','frame'))/10
    opt["LANE_PREPROCESSING"]["roi"]["right"] = int(cv2.getTrackbarPos('roi_right','frame'))/10
    opt["LANE_PREPROCESSING"]["roi"]["upper"] = int(cv2.getTrackbarPos('roi_upper','frame'))/10
    
    
    if cur_frame > len(img_files)-1:    
        print('this is the end')
        json.dump(opt, open("end_config.json", "w"))
        break
    Img_proc = ImagePreprocessing(opt)
    if is_cam:
        ret, frame = cam.read()
    else:
        
        path = os.path.join(img_dir,img_files[cur_frame])
        print(path)
        frame = cv2.imread(path)
        ret = True
    
    if ret:
        
        combined_binary, sybinary, grayImg = Img_proc.process_image(frame)
        cv2.imshow("combined_binary", combined_binary)
        # cv2.imshow("sybinary", sybinary)
        # cv2.imshow("grayImg", grayImg)
        cv2.imshow("frame", frame)
        key = cv2.waitKey(1) & 0xff
        if key == ord('q'):
            break
        elif key == ord('n'):
            cur_frame+=10
        elif key == ord('b'):
            cur_frame-=10
        elif key == ord('s'):
            json.dump(opt, open("new_config.json", "w"))
        elif key== ord('d')  :
            os.remove(path)
    else:
        break
