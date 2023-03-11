import cv2
import time

cap = cv2.VideoCapture('/dev/video0')
i = 0

while cap.isOpened():
    
    ret, frame = cap.read()

    if i % 1 == 0:
        cv2.imwrite(r'/home/ceec/BFMC_Brain_TX2/object_data_7/object_7_image_' + str(i//1) + ".jpg", frame)
        
    i += 1
    
    time.sleep(0.1)