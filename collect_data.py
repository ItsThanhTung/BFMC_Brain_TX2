import cv2


i = 0
while True:
    for video in ["/dev/video0"]:
        cap = cv2.VideoCapture(video)
        while True:
            ret, frame = cap.read()
            
            if ret: 
                cv2.imwrite("/home/tung/bosch/object_data_1/object_" + str(i) + ".jpg", frame)
                cv2.imshow("image", frame)
                cv2.waitKey(1)
                i += 1
            else:
                break
        cap.release()