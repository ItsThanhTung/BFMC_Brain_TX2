import cv2
from src.image_processing.traffic_sign.detection import Yolo

yolo=Yolo()

if __name__ == "__main__":
    img = cv2.imread('/home/ceec/BFMC_Brain_TX2/output.jpg')
    _=yolo.detect(img)