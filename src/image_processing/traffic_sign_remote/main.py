import sys
sys.path.append('./yolov5_utils')
from detection import Yolo
import cv2
import time


yolo=Yolo()
img=cv2.imread('/home/tx2jp462/yolov5/sign/test/images/16_JPG.rf.f003457380bedb607fbfc05669f3cb0a.jpg')
_=yolo.detect(img)
img=cv2.imread('/home/tx2jp462/yolov5/sign/test/images/16_JPG.rf.f003457380bedb607fbfc05669f3cb0a.jpg')
_=yolo.detect(img)
start=time.time()
for i in range(100):
    img=cv2.imread('/home/tx2jp462/yolov5/sign/test/images/16_JPG.rf.f003457380bedb607fbfc05669f3cb0a.jpg')
    img,results=yolo.detect(img)
    print(results)
print(100/(time.time()-start))
cv2.imwrite('img.jpg',img)