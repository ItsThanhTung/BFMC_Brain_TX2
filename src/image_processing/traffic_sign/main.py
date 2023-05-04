import sys
sys.path.append('/home/ceec/BFMC_Brain_TX2')
from detection import Yolo
import cv2
import time

yolo=Yolo(streamP=None, outP=None, debugP=None, debug=None,is_tensorRt=True,imgsize=(640,640))
img=cv2.imread('/home/ceec/BFMC_Brain_TX2/src/image_processing/traffic_sign/1325.jpg')
_=yolo.detect(img)
img=cv2.imread('/home/ceec/BFMC_Brain_TX2/src/image_processing/traffic_sign/1325.jpg')
_=yolo.detect(img)
img=cv2.imread('/home/ceec/BFMC_Brain_TX2/src/image_processing/traffic_sign/1325.jpg')
_=yolo.detect(img)
start=time.time()
for i in range(30):
    # img=cv2.imread('/home/ceec/BFMC_Brain_TX2/src/image_processing/traffic_sign/1325.jpg')
    img,results=yolo.detect(img)
    # print(results)
print(30/(time.time()-start))
cv2.imwrite('img.jpg',img)