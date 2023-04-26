import sys
sys.path.append('/home/ceec/usb/BFMC_Brain_TX2')
from detection import Yolo
import cv2
import time

yolo=Yolo(streamP=None, outP=None, debugP=None, debug=None,is_tensorRt=True,imgsize=(512,640))
img=cv2.imread('/home/ceec/usb/yolov5_old/imgs/car_207.png')
_=yolo.detect(img)
img=cv2.imread('/home/ceec/usb/yolov5_old/imgs/car_207.png')
_=yolo.detect(img)
img=cv2.imread('/home/ceec/usb/yolov5_old/imgs/car_207.png')
_=yolo.detect(img)
start=time.time()
for i in range(30):
    # img=cv2.imread('/home/ceec/usb/yolov5_old/imgs/car_207.png')
    img,results=yolo.detect(img)
    print(results)
print(30/(time.time()-start))
cv2.imwrite('img.jpg',img)