import time
from src.image_processing.traffic_sign.detection import Yolo
from threading import Thread, Condition
from src.templates.torch_workerprocess import Torch_WorkerProcess
from queue import Queue
import numpy as np


class ObjectDetectionProcess(Torch_WorkerProcess):
    image_stream_queue = Queue(maxsize=5)
    object_image_condition = Condition()
    read_image_condition = Condition()
    # ===================================== INIT =========================================
    def __init__(self, inPs, outPs, is_show, debugP = None, debug=False):
        """Process used for sending images over the network to a targeted IP via UDP protocol 
        (no feedback required). The image is compressed before sending it. 

        Used for visualizing your raspicam images on remote PC.
        
        Parameters
        ----------
        inPs : list(Pipe) 
            List of input pipes, only the first pipe is used to transfer the captured frames. 
        outPs : list(Pipe) 
            List of output pipes (not used at the moment)
        """
        
        self.detector = Yolo()
        super(ObjectDetectionProcess,self).__init__( inPs, outPs)

        self.image = None
        self.visualized_image = None
        self.results = None

        self.debug = debug
        self.debugP = debugP

        self.is_show = is_show

        
    # ===================================== RUN ==========================================
    def run(self):
        """Apply the initializing methods and start the threads.
        """
        super(ObjectDetectionProcess,self).run()

    # ===================================== INIT THREADS =================================
    def _init_threads(self):
        """Initialize the sending thread.
        """
        if self._blocker.is_set():
            return
        
        imageReadTh = Thread(name='ImageReadThread',target = self._read_image, args= (self.inPs["OBJECT_IMAGE"],))
        runDetectionTh = Thread(name='RunDetectionThread',target = self._run_detection)

        sendResultth = Thread(name='SendImageLaneKeeping',target = self._send_result, args= (self.outPs["DECISION_MAKING"],))

        if self.debug:
            imageStreamTh = Thread(name='ImageStreamThread',target = self._stream_image, args= (self.debugP,))
            imageStreamTh.daemon = True
            self.threads.append(imageStreamTh)

        if self.is_show:
            sendImageShowTh = Thread(name='SendImageShow',target = self._send_image_show, args= (self.outPs["IMAGE_SHOW"],))
            sendImageShowTh.daemon = True
            self.threads.append(sendImageShowTh)

            
        runDetectionTh.daemon = True
        imageReadTh.daemon = True
        sendResultth.daemon = True

        self.threads.append(imageReadTh)
        self.threads.append(runDetectionTh)
        self.threads.append(sendResultth)

    
    def _read_image(self, inP):
         while True:
            try:
                data = inP.recv()
                self.read_image_condition.acquire()
                self.image = data["image"]
                self.read_image_condition.notify()
                self.read_image_condition.release()

            except Exception as e:
                print("Object detection - read image thread error:")
                print(e)


    def _stream_image(self, outP):
        while True:
            try:
                image = self.image_stream_queue.get()
                outP.send({"image": image})
        
            except Exception as e:
                print("Image Preprocessing - stream image thread error:")
                print(e)

    def _run_detection(self):
        while True:
            try:
                self.read_image_condition.acquire()
                self.read_image_condition.wait()
                if self.image is not None:
                    image = self.image.copy()
                    self.read_image_condition.release()

                    if self.debug:
                        if not self.image_stream_queue.full():
                            self.image_stream_queue.put(image)
                        else:
                            print("Object Detection - object image thread full Queue")
                    visualized_image = np.zeros((480, 640))
                    results = [1, 2, 3, 4]
                    visualized_image, results = self.detector.detect(image)
                    self.object_image_condition.acquire()
                    self.visualized_image = visualized_image
                    self.results = results
                    self.object_image_condition.notify_all()
                    self.object_image_condition.release()

                else:
                    self.read_image_condition.release()

            except Exception as e:
                print("Object Detection - run detection thread error:")
                print(e)

    def _stream_image(self, outP):
        while True:
            try:
                image = self.image_stream_queue.get()
                outP.send({"image": image})
        
            except Exception as e:
                print("Object Detection - stream image thread error:")
                print(e)

    def _send_image_show(self, outP):
        while True:
            try:
                self.object_image_condition.acquire()
                self.object_image_condition.wait()

                if self.visualized_image is not None:
                    visualized_image = self.visualized_image.copy()
                    self.object_image_condition.release()
                    outP.send({"visualized_object_image" : visualized_image})
                else:
                    self.object_image_condition.release()
        
            except Exception as e:
                print("Object detection - send image show thread error:")
                print(e)

    def _send_result(self, outP):
        while True:
            try:
                self.object_image_condition.acquire()
                self.object_image_condition.wait()

                if self.results is not None:
                    results = self.results.copy()
                    self.object_image_condition.release()
                    outP.send({"results" : results})
                else:
                    self.object_image_condition.release()
        
            except Exception as e:
                print("Object detection - send result thread error:")
                print(e)


            

   