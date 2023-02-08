import base64
import json                    
import cv2
import requests
import threading
import queue
from datetime import datetime
class Client(object):
    def __init__(self):
        self.headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        self.api='http://192.168.0.106:8080/test'
        self.send_data_thread = threading.Thread(target=self.send,daemon=False)
        self.c_detection = threading.Condition()  
        self.detection_buffer = queue.Queue(maxsize=5)
        self._running = False 
    def send(self):
        while True:
            # print("check")
            with self.c_detection:
                self.c_detection.wait()
            # print("size :",self.detection_buffer.qsize())
            image,detection=self.detection_buffer.get()
            # print(image.shape)
            success, encoded_image = cv2.imencode('.png', image)
            im_bytes = encoded_image.tobytes()   
            im_b64 = base64.b64encode(im_bytes).decode("utf8")

            
            
            payload = json.dumps({"image": im_b64, "detection": detection, "time": datetime.now().strftime("%d/%m/%Y %H:%M:%S")})
            response = requests.post(self.api, data=payload, headers=self.headers)
            try:
                data = response.json()     
                print(data)                
            except requests.exceptions.RequestException:
                print(response.text)
            if not self._running:
                break