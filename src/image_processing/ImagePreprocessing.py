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

import socket
import struct
import time
import numpy as np
import math

from threading import Thread

import cv2

from src.templates.workerprocess import WorkerProcess


class ImagePreprocessingProcess(WorkerProcess):
    # ===================================== INIT =========================================
    def __init__(self, inPs, outPs):
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
        imagePreprocessTh = Thread(name='ImagePreprocessingThread',target = self._run, args= (self.inPs[0], self.outPs))
        imagePreprocessTh.daemon = True
        self.threads.append(imagePreprocessTh)

    # def laneKeeping(self, frame, old_angle, old_state):
        

    def _run(self, inP, outP):
        """Obtains image, applies the required image processing and computes the steering angle value. 
        
        Parameters
        ----------
        inP  : Pipe
            Input pipe to read the frames from other process.
        outP : Pipe
            Output pipe to send the steering angle value to other process.

        """
        while True:
            try:
                # Obtain image
                data = inP.recv()
                img = data["image"]

                # img = cv2.resize(img, (320, 240))
                new_combined_binary, sybinary, image_ff = thresholding(img)
                # image_ff = cv2.Canny(image_ff, 50, 150)
                for out in outP:
                    out.send({"original_image": img, 
                                "new_combined_binary" : new_combined_binary, 
                                "sybinary" : sybinary, 
                                "image_ff" : image_ff})

            except Exception as e:
                print("Image Preprocessing error:")
                print(e)

    
def get_sobel_image(sobel_image, threshold):
    abs_sobel_image = np.absolute(sobel_image)
    scaled_sobelx = np.uint8(255*abs_sobel_image/np.max(abs_sobel_image))
    binary = np.zeros_like(scaled_sobelx)
    binary[(scaled_sobelx >= threshold[0]) 
            & (scaled_sobelx <= threshold[1])] = 255

    return binary

sx_thresh=(70, 255)
sy_thresh=(131, 250)
r_thresh = (150, 255)

def thresholding(frame):
    bgr_image = np.copy(frame)
    red_channel = bgr_image[:,:,2]

    hls = np.float64(cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HLS))
    l_channel = hls[:,:,1]

    sobelx = cv2.Sobel(l_channel, cv2.CV_64F, 1, 0, ksize = 3)
    sobely = cv2.Sobel(l_channel, cv2.CV_64F, 0, 1, ksize = 3)

    sxbinary = get_sobel_image(sobelx, sx_thresh)
    sybinary = get_sobel_image(sobely, sy_thresh)

    r_binary = np.zeros_like(red_channel)
    r_binary[(red_channel >= r_thresh[0]) & (red_channel <= r_thresh[1])] = 255

    combined_binary = np.zeros_like(sxbinary)

    grayImg = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, image_ff = cv2.threshold(grayImg, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    combined_binary[((adaptive == 255) & (sxbinary == 255)) 
                    | ((sxbinary == 255) & (r_binary == 255))] = 255

    adaptive = cv2.adaptiveThreshold(grayImg, 255,\
                        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 45, -70)
    
    new_combined_binary = combined_binary
    new_combined_binary[((combined_binary == 255) & (adaptive == 255))] = 255

    new_combined_binary = cv2.dilate(new_combined_binary, np.ones((3, 3), np.uint8)) 

    return new_combined_binary, sybinary, image_ff

            
