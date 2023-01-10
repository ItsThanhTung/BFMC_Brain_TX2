import cv2
import numpy as np

from src.image_processing.LaneDebugging import LaneDebugging
from src.image_processing.LaneKeeping import LaneKeeping
from src.utils.utils_function import load_config_file

opt = load_config_file("main_remote.json")

LaneDebugger = LaneDebugging()
LaneKeeper = LaneKeeping(opt, True)
vid = cv2.VideoCapture(0)

def get_sobel_image(sobel_image, threshold):
    abs_sobel_image = np.absolute(sobel_image)
    scaled_sobelx = np.uint8(255*abs_sobel_image/np.max(abs_sobel_image))
    binary = np.zeros_like(scaled_sobelx)
    binary[(scaled_sobelx >= threshold[0]) 
            & (scaled_sobelx <= threshold[1])] = 255
    
    return binary

sobel_x_thres = []
sobel_y_thres = []
red_thres = []
adaptive_block_size = 3
adaptive_offset = -50
dilate_kernel = 3


def process_image(frame, sobel_x_thres, sobel_y_thres, red_thres, adaptive_block_size, adaptive_offset, dilate_kernel):
    bgr_image = np.copy(frame)
    red_channel = bgr_image[:,:,2]

    hls = np.float64(cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HLS))
    l_channel = hls[:,:,1]

    sobelx = cv2.Sobel(l_channel, cv2.CV_64F, 1, 0, ksize = 3)
    sobely = cv2.Sobel(l_channel, cv2.CV_64F, 0, 1, ksize = 3)

    sxbinary = get_sobel_image(sobelx, sobel_x_thres)
    sybinary = get_sobel_image(sobely, sobel_y_thres)
    
    r_binary = np.zeros_like(red_channel)
    r_binary[(red_channel >= red_thres[0]) & (red_channel <= red_thres[1])] = 255

    combined_binary = np.zeros_like(sxbinary)

    grayImg = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, image_ff = cv2.threshold(grayImg, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    

    adaptive = cv2.adaptiveThreshold(grayImg, 255,\
                        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, adaptive_block_size, adaptive_offset)
    combined_binary[((adaptive == 255) & (sxbinary == 255)) 
                    | ((sxbinary == 255) & (r_binary == 255))] = 255
    
    new_combined_binary = combined_binary
    new_combined_binary[((combined_binary == 255) & (adaptive == 255))] = 255
    
    new_combined_binary = cv2.dilate(new_combined_binary, \
                            np.ones((dilate_kernel, dilate_kernel), np.uint8)) 

    return new_combined_binary, sybinary, image_ff

def nothing(x):
    pass

cv2.namedWindow('sobelx')
cv2.createTrackbar("upper_value", "sobelx", 0, 255, nothing)
cv2.createTrackbar("lower_value", "sobelx", 0, 255, nothing)

cv2.namedWindow('sobely')
cv2.createTrackbar("upper_value", "sobely", 0, 255, nothing)
cv2.createTrackbar("lower_value", "sobely", 0, 255, nothing)

cv2.namedWindow('red')
cv2.createTrackbar("upper_value", "red", 0, 255, nothing)
cv2.createTrackbar("lower_value", "red", 0, 255, nothing)

cv2.namedWindow('adaptive_block_size')
cv2.createTrackbar("value", "adaptive_block_size", 2, 255, nothing)

cv2.namedWindow('adaptive_offset')
cv2.createTrackbar("value", "adaptive_offset", 0, 255, nothing)

while vid.isOpened():
    ret, frame = vid.read()

    if ret:
        frame = cv2.resize(frame, (320, 240))
        sobel_x_thres = [int(cv2.getTrackbarPos('lower_value','sobelx')), \
                        int(cv2.getTrackbarPos('upper_value','sobelx'))]

        sobel_y_thres = [int(cv2.getTrackbarPos('lower_value','sobely')), \
                        int(cv2.getTrackbarPos('upper_value','sobely'))]

        red_thres = [int(cv2.getTrackbarPos('lower_value','red')), \
                        int(cv2.getTrackbarPos('upper_value','red'))]

        adaptive_block_size = int(cv2.getTrackbarPos('value','adaptive_block_size'))
        if adaptive_block_size % 2 == 0:
            adaptive_block_size += 1

        adaptive_offset = - int(cv2.getTrackbarPos('value','adaptive_offset'))

        new_combined_binary, sybinary, image_ff = process_image(frame, sobel_x_thres, sobel_y_thres, \
                                                                red_thres, adaptive_block_size, adaptive_offset, 3)

        speed, angle, state, debug_data = LaneKeeper.lane_keeping(new_combined_binary)
        lines_image, visualize_image = LaneDebugger.visualize(debug_data)


        cv2.imshow("frame", frame)
        cv2.imshow("lines_image", lines_image)
        cv2.imshow("visualize_image", visualize_image)
        cv2.imshow("preprocessed_image", new_combined_binary)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    



