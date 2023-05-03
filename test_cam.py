import cv2
import numpy as np
import os 


def get_sobel_image(sobel_image, threshold):
  abs_sobel_image = np.absolute(sobel_image)
  scaled_sobelx = np.uint8(255*abs_sobel_image/np.max(abs_sobel_image))
  binary = np.zeros_like(scaled_sobelx)
  binary[(scaled_sobelx >= threshold[0]) 
          & (scaled_sobelx <= threshold[1])] = 255

  return binary

image_dir = r'D:\bosch\afternoon\lane_video_2'


for path in os.listdir(image_dir):
  image_path = os.path.join(image_dir, path)
  image = cv2.imread(image_path)
  image = cv2.GaussianBlur(image,(3,3),0)

  hls = np.float64(cv2.cvtColor(image, cv2.COLOR_BGR2HLS))
  grey = np.float64(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))

  l_channel = hls[:,:,1]
  sobelx = cv2.Sobel(grey, cv2.CV_64F, 1, 0, ksize = 3)
  sxbinary = get_sobel_image(sobelx, [25, 255])


  ret, thresh = cv2.threshold(grey, 200, 255, cv2.THRESH_BINARY)
  thresh_2 = cv2.adaptiveThreshold(np.uint8(grey), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 13, 5)


  result = sxbinary + thresh

  cv2.imshow("image", image)
  cv2.imshow("thresh", thresh)
  cv2.imshow("thresh_2", thresh_2)
  cv2.imshow("sxbinary", sxbinary)
  cv2.imshow("result", result)
  cv2.waitKey(1)