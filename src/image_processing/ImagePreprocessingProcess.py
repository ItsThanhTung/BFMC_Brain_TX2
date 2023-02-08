# Copyright (c) 2019, Bosch Engineering Center Cluj and BFMC organizers
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE
import numpy as np
import math

from threading import Thread, Condition
from src.templates.workerprocess import WorkerProcess
from src.image_processing.ImagePreprocessing import ImagePreprocessing
from queue import Queue

class ImagePreprocessingProcess(WorkerProcess):
    image_stream_queue = Queue(maxsize=5)
    preprocess_image_condition = Condition()
    read_image_condition = Condition()
    # ===================================== INIT =========================================
    def __init__(self, inPs, outPs, opt, debugP = None, debug=False):
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

        super(ImagePreprocessingProcess,self).__init__( inPs, outPs)

        self.image = None
        self.new_combined_binary = None
        self.sybinary = None
        self.image_ff = None

        self.debug = debug
        self.debugP = debugP
        self.opt = opt

        
    # ===================================== RUN ==========================================
    def run(self):
        """Apply the initializing methods and start the threads.
        """
        super(ImagePreprocessingProcess,self).run()

    # ===================================== INIT THREADS =================================
    def _init_threads(self):
        """Initialize the sending thread.
        """
        if self._blocker.is_set():
            return
        
        imageReadTh = Thread(name='ImageReadThread',target = self._read_image, args= (self.inPs["LANE_IMAGE"],))
        imagePreprocessTh = Thread(name='ImagePreprocessingThread',target = self._run_image_preprocessing)

        sendImageLaneKeepingTh = Thread(name='SendImageLaneKeeping',target = self._send_image_lane_keeping, args= (self.outPs["LANE_KEEPING"],))
        sendImageInterceptDetectionTh = Thread(name='SendImageInterceptDetection',target = self._send_image_intercept_detection, args= (self.outPs["INTERCEPT_DETECTION"],))
        
        if self.debug:
            imageStreamTh = Thread(name='ImageStreamThread',target = self._stream_image, args= (self.debugP,))
            imageStreamTh.daemon = True
            self.threads.append(imageStreamTh)
        else:
            sendImageShowTh = Thread(name='SendImageShow',target = self._send_image_show, args= (self.outPs["IMAGE_SHOW"],))
            self.threads.append(sendImageShowTh)
            
        imagePreprocessTh.daemon = True
        imageReadTh.daemon = True
        self.threads.append(imageReadTh)
        self.threads.append(imagePreprocessTh)
        self.threads.append(sendImageLaneKeepingTh)
        self.threads.append(sendImageInterceptDetectionTh)
        
    
    def _read_image(self, inP):
         while True:
            try:
                data = inP.recv()
                self.read_image_condition.acquire()
                self.image = data["image"]
                self.read_image_condition.notify()
                self.read_image_condition.release()

            except Exception as e:
                print("Image Preprocessing - read image thread error:")
                print(e)


    def _stream_image(self, outP):
        while True:
            try:
                image = self.image_stream_queue.get()
                outP.send({"image": image})
        
            except Exception as e:
                print("Image Preprocessing - stream image thread error:")
                print(e)
            

    def _run_image_preprocessing(self):
        image_processor = ImagePreprocessing(self.opt)
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
                            print("Image Preprocessing - preprocess image thread full Queue")
                
                    new_combined_binary, sybinary, image_ff = image_processor.process_image(image)
                   
                    self.preprocess_image_condition.acquire()
                    self.original_image = image
                    self.new_combined_binary = new_combined_binary
                    self.sybinary = sybinary
                    self.image_ff = image_ff
                    self.preprocess_image_condition.notify_all()
                    self.preprocess_image_condition.release()
                
                else:
                    self.read_image_condition.release()

            except Exception as e:
                print("Image Preprocessing - preprocess image thread error:")
                print(e)


    def _send_image_lane_keeping(self, outP):
        while True:
            try:
                self.preprocess_image_condition.acquire()
                self.preprocess_image_condition.wait()

                if self.new_combined_binary is not None:
                    new_combined_binary = self.new_combined_binary.copy()
                    self.preprocess_image_condition.release()
                    outP.send({"new_combined_binary" : new_combined_binary})
                else:
                    self.preprocess_image_condition.release()
        
            except Exception as e:
                print("Image Preprocessing - send image lane keeping thread error:")
                print(e)


    def _send_image_intercept_detection(self, outP):
        while True:
            try:
                self.preprocess_image_condition.acquire()
                self.preprocess_image_condition.wait()

                if self.sybinary is not None:
                    sybinary = self.sybinary.copy()
                    self.preprocess_image_condition.release()
                    outP.send({"sybinary" : sybinary})
                else:
                    self.preprocess_image_condition.release()

            except Exception as e:
                print("Image Preprocessing - send image intercept detection thread error:")
                print(e)
    

    def _send_image_show(self, outP):
        while True:
            try:
                self.preprocess_image_condition.acquire()
                self.preprocess_image_condition.wait()

                if self.new_combined_binary is not None:
                    new_combined_binary = self.new_combined_binary.copy()
                    sybinary = self.sybinary.copy()
                    image_ff = self.image_ff.copy()
                    original_image = self.original_image.copy()
                    self.preprocess_image_condition.release()

                    outP.send({"original_image" : original_image,
                                "new_combined_binary" : new_combined_binary, 
                                "sybinary" : sybinary, 
                                "image_ff" : image_ff})
                    
                else:
                    self.preprocess_image_condition.release()

            except Exception as e:
                print("Image Preprocessing - send image show thread error:")
                print(e)
    


            
