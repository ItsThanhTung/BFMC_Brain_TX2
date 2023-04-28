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

import io
import numpy as np
import time
import cv2


import multiprocessing
from src.templates.threadwithstop import ThreadWithStop

#================================ CAMERA PROCESS =========================================
class CameraThread(ThreadWithStop):
    
    #================================ CAMERA =============================================
    def __init__(self, cam_path, outPs,opt):
        """The purpose of this thread is to setup the camera parameters and send the result to the CameraProcess. 
        It is able also to record videos and save them locally. You can do so by setting the self.RecordMode = True.
        
        Parameters
        ----------
        outPs : list(Pipes)
            the list of pipes were the images will be sent
        """
        super(CameraThread,self).__init__()
        self.daemon = True


        # streaming options
        self._stream      =   io.BytesIO()

        self.recordMode   =   False
        
        #output 
        self.outPs        =   outPs

        self.cam_path = cam_path
        self.opt = opt
    #================================ RUN ================================================
    def run(self):
        """Apply the initializing methods and start the thread. 
        """
        self._init_camera()
        
        # record mode
        # if self.recordMode:
        #     self.camera.start_recording('picam'+ self._get_timestamp()+'.h264',format='h264')

        # Sets a callback function for every unpacked frame
        # self.camera.capture_sequence(
        #                             self._streams(), 
        #                             use_video_port  =   True, 
        #                             format          =   'rgb',
        #                             resize          =   self.imgSize)
        self._streams()
        # record mode
        if self.recordMode:
            self.camera.stop_recording()
     

    #================================ INIT CAMERA ========================================
    def _init_camera(self):
        """Init the PiCamera and its parameters
        """
        
        # this how the firmware works.
        # the camera has to be imported here
        # from picamera import PiCamera

        # camera
        self.camera = cv2.VideoCapture(self.cam_path)

        # camera settings
        # self.camera.resolution      =   (1280,960)
        # self.camera.framerate       =   30

        # self.camera.brightness      =   50
        # self.camera.shutter_speed   =   2000
        #self.camera.contrast        =   0
        # self.camera.iso             =   0 # auto
        

        self.imgSize                =   (640, 480)    # the actual image size

    # ===================================== GET STAMP ====================================
    def _get_timestamp(self):
        stamp = time.gmtime()
        res = str(stamp[0])
        for data in stamp[1:6]:
            res += '_' + str(data)  

        return res

    #================================ STREAMS ============================================
    def _streams(self):
        """Stream function that actually published the frames into the pipes. Certain 
        processing(reshape) is done to the image format. 
        """

        while self._running:
            ret, data = self.camera.read()
            lane_image = cv2.resize(data, (320, 240))
            lane_image = self.region_of_interest(lane_image)
            # Note: The sending process can be blocked, when doesn't exist any consumer process and it reaches the limit size.
            self.outPs["PREPROCESS_IMAGE"].send({"image": lane_image})
            
            if self.outPs["OBJECT_IMAGE"] is not None:
                self.outPs["OBJECT_IMAGE"].send({"image": data})


    def region_of_interest(self, frame):
        height = frame.shape[0]
        width = frame.shape[1]
        mask = np.zeros_like(frame)

        region_of_interest_vertices = np.array([[   (0, height-1),
                                                    (0,height*self.opt['roi']['mid']),
                                                    (self.opt["roi"]["left"]*width, height * self.opt["roi"]["upper"]),
                                                    (self.opt["roi"]["right"]*width, height * self.opt["roi"]["upper"]),
                                                    (width-1,height*self.opt['roi']['mid']),
                                                    (width - 1, height-1)]], np.int32)

        cv2.fillPoly(mask, region_of_interest_vertices, (255,255,255))
        masked_image = cv2.bitwise_and(frame, mask)
        return masked_image       


