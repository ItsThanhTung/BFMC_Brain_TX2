import cv2
import time
from datetime import datetime
  
  
# define a video capture object

vid = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc(*'MP4V')
out = cv2.VideoWriter("tx2_huycq_51.mp4", fourcc, 20.0, (640,480))
start=time.time()
while(time.time()-start<3600):
      
    # Capture the video frame
    # by frame
    ret, frame = vid.read()
    # print(frame.shape)
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame,str(datetime.now()),(40,40), font, .5,(255,255,255),2,cv2.LINE_AA)
    out.write(frame)
    # Display the resulting frame
    cv2.imshow('frame', cv2.resize(frame,(200,200)))
      
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
  
# After the loop release the cap object
vid.release()
# out.release()
# Destroy all the windows
cv2.destroyAllWindows()
