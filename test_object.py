import cv2
from src.image_processing.ObjectDetectionProcess import ObjectDetectionProcess

if __name__ == "__main__":
    img = cv2.imread(r'D:\stop.jpg')
    objectDetector = ObjectDetectionProcess()
    objectDetector.detect(img)