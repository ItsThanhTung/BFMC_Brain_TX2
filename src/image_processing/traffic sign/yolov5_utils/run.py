from multiprocessing.connection import Client
from yolo_detection import YoloV5
import cv2
from client import Client
from utils.augmentations import letterbox
import time
object_detection=YoloV5()
# img=cv2.imread('/home/huycq/yolov5/data/images/zidane.jpg')
# img,detection=object_detection.detect(img)

client = Client()

client.detection_buffer=object_detection.processed_backbone_buffer
client.c_detection=object_detection.c_processed_frame

client._running=True
client.send_data_thread.start()
import cv2
import numpy as np


cap = cv2.VideoCapture('/home/tx2jp462/yolov5/test.mp4')


if (cap.isOpened()== False): 
    print("Error opening video stream or file")
end_t,start_t=5,5
while(cap.isOpened()):
    end_t=time.time()
    # print("FPS :",1/(end_t-start_t))
    start_t=time.time()
    ret, frame = cap.read()
    if ret == True:
        
        img,detection=object_detection.detect(frame)
        cv2.imshow('Frame',img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else: 
        break


cap.release()
# client._running=False
cv2.destroyAllWindows()