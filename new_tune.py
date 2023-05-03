import json
import numpy as np
import cv2
from src.utils.utils_function import load_config_file

class ImagePreprocessing():
    def __init__(self, opt):
        self.opt = opt["LANE_PREPROCESSING"]
        self.sobel_x_thres          = self.opt["sobel_x_thres"]
        self.sobel_y_thres          = self.opt["sobel_y_thres"]
        self.adaptive_block_size    = self.opt["adaptive_block_size"]
        self.adaptive_offset        = self.opt["adaptive_offset"]
        self.red_thres_lower        = self.opt["red_thres"][0]
        self.red_thres_upper        = self.opt["red_thres"][1]
        self.roi_mid                = self.opt['roi']['mid']
        self.roi_left               = self.opt["roi"]["left"]
        self.roi_right              = self.opt["roi"]["right"]
        self.roi_upper              = self.opt["roi"]["upper"]

    def get_sobel_image(self, sobel_image, threshold):
        abs_sobel_image = np.absolute(sobel_image)
        scaled_sobelx = np.uint8(255*abs_sobel_image/np.max(abs_sobel_image))
        binary = np.zeros_like(scaled_sobelx)
        binary[(scaled_sobelx >= threshold[0])
               & (scaled_sobelx <= threshold[1])] = 255

        return binary

    def process_image(self, frame):

        bgr_image = np.copy(frame)

        # bgr_image = self.region_of_interest(bgr_image)
        red_channel = bgr_image[:, :, 2]

        hls = np.float64(cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HLS))
        l_channel = hls[:, :, 1]

        sobelx = cv2.Sobel(l_channel, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(l_channel, cv2.CV_64F, 0, 1, ksize=3)

        sxbinary = self.get_sobel_image(sobelx, self.sobel_x_thres)
        sybinary = self.get_sobel_image(sobely, self.sobel_y_thres)

        r_binary = np.zeros_like(red_channel)
        r_binary[(red_channel >= self.red_thres_lower) & (
            red_channel <= self.red_thres_upper)] = 255

        combined_binary = np.zeros_like(sxbinary)

        grayImg = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # _, image_ff = cv2.threshold(grayImg, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        adaptive = cv2.adaptiveThreshold(grayImg, 255,
                                         cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, self.adaptive_block_size, self.adaptive_offset)
        combined_binary[((adaptive == 255) & (sxbinary == 255))
                        | ((sxbinary == 255) & (r_binary == 255))] = 255

        new_combined_binary = combined_binary
        new_combined_binary[((combined_binary == 255) &
                             (adaptive == 255))] = 255
        new_combined_binary = self.region_of_interest(new_combined_binary)
        # new_combined_binary = cv2.dilate(new_combined_binary, \
        #                         np.ones((self.opt["dilate_kernel"], self.opt["dilate_kernel"]), np.uint8))

        return new_combined_binary, sybinary, grayImg

    def region_of_interest(self, frame):
        height = frame.shape[0]
        width = frame.shape[1]
        mask = np.zeros_like(frame)

        region_of_interest_vertices = np.array([[(0, height-30),
                                                 (0, height *
                                                  self.roi_mid),
                                                 (self.roi_left*width,
                                                     height * self.roi_upper),
                                                 (self.roi_right*width,
                                                     height * self.roi_upper),
                                                 (width-1, height *
                                                  self.roi_mid),
                                                 (width - 1, height-30)]], np.int32)
        cv2.fillPoly(mask, region_of_interest_vertices, 255)
        masked_image = cv2.bitwise_and(frame, mask)
        return masked_image
def nothing(x):
    pass

cv2.namedWindow('frame')
cv2.createTrackbar("sobelx_upper", "frame", 0, 255, nothing)
cv2.createTrackbar("sobelx_lower", "frame", 0, 255, nothing)
cv2.createTrackbar("sobely_upper", "frame", 0, 255, nothing)
cv2.createTrackbar("sobely_lower", "frame", 0, 255, nothing)
cv2.createTrackbar("red_upper", "frame", 0, 255, nothing)
cv2.createTrackbar("red_lower", "frame", 0, 255, nothing)
cv2.createTrackbar("adaptive_block_size", "frame", 3, 255, nothing)
cv2.createTrackbar("adaptive_offset", "frame", 0, 255, nothing)
cv2.createTrackbar("roi_mid", "frame", 0, 10, nothing)
cv2.createTrackbar("roi_left", "frame", 0, 10, nothing)
cv2.createTrackbar("roi_right", "frame", 0, 10, nothing)
cv2.createTrackbar("roi_upper", "frame", 0, 10, nothing)


opt = load_config_file("main_rc.json")

cam = cv2.VideoCapture("/home/topo/code/sam.mp4")
while True:
    opt["LANE_PREPROCESSING"]["sobel_x_thres"] = [int(cv2.getTrackbarPos('sobelx_upper','frame')), int(cv2.getTrackbarPos('sobelx_lower','frame'))]
    opt["LANE_PREPROCESSING"]["sobel_y_thres"] = [int(cv2.getTrackbarPos('sobely_upper','frame')), int(cv2.getTrackbarPos('sobely_lower','frame'))]
    opt["LANE_PREPROCESSING"]["adaptive_block_size"] = int(cv2.getTrackbarPos('adaptive_block_size','frame')) if cv2.getTrackbarPos('adaptive_block_size','frame') % 2 == 1 else int(cv2.getTrackbarPos('adaptive_block_size','frame')) + 1
    opt["LANE_PREPROCESSING"]["adaptive_offset"] = int(cv2.getTrackbarPos('adaptive_offset','frame'))
    opt["LANE_PREPROCESSING"]["red_thres"][0] = int(cv2.getTrackbarPos('red_lower','frame'))
    opt["LANE_PREPROCESSING"]["red_thres"][1] = int(cv2.getTrackbarPos('red_upper','frame'))
    opt["LANE_PREPROCESSING"]['roi']['mid'] = int(cv2.getTrackbarPos('roi_mid','frame'))/10
    opt["LANE_PREPROCESSING"]["roi"]["left"] = int(cv2.getTrackbarPos('roi_left','frame'))/10
    opt["LANE_PREPROCESSING"]["roi"]["right"] = int(cv2.getTrackbarPos('roi_right','frame'))/10
    opt["LANE_PREPROCESSING"]["roi"]["upper"] = int(cv2.getTrackbarPos('roi_upper','frame'))/10
    
    Img_proc = ImagePreprocessing(opt)
    ret, frame = cam.read()
    if ret:
        
        combined_binary, sybinary, grayImg = Img_proc.process_image(frame)
        cv2.imshow("combined_binary", combined_binary)
        cv2.imshow("sybinary", sybinary)
        cv2.imshow("grayImg", grayImg)
        cv2.imshow("frame", frame)
        key = cv2.waitKey(1) & 0xff
        if key == ord('q'):
            break
        elif key == ord('s'):
            json.dump(opt, open("new_config.json", "w"))
    else:
        break
