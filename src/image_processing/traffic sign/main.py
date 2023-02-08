import sys
sys.path.append('./yolov5')
from Detection import Yolo
import cv2
import time


yolo=Yolo()
img=cv2.imread('/home/tx2jp462/yolov5/sign/test/images/16_JPG.rf.f003457380bedb607fbfc05669f3cb0a.jpg')
img=yolo.detect(img)
img=cv2.imread('/home/tx2jp462/yolov5/sign/test/images/16_JPG.rf.f003457380bedb607fbfc05669f3cb0a.jpg')
img=yolo.detect(img)
start=time.time()
for i in range(100):
    img=cv2.imread('/home/tx2jp462/yolov5/sign/test/images/16_JPG.rf.f003457380bedb607fbfc05669f3cb0a.jpg')
    img=yolo.detect(img)
print(100/(time.time()-start))
cv2.imwrite('img.jpg',img)