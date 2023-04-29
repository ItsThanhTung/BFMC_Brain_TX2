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

from threading import Thread, Lock
from simple_pid import PID

from src.templates.workerprocess import WorkerProcess
from src.image_processing.LaneKeeping import LaneKeeping

from src.utils.utils_function import setSpeed, setAngle, EnablePID


class LaneKeepingProcess(WorkerProcess):
    data_object_detection_lock = Lock()
    pid = PID(Kp = 1.0, Ki = 1.45, Kd = 0.15, output_limits = [-23, 23])
    # ===================================== INIT =========================================
    def __init__(self, inPs, outPs, opt, debugP=None, debug=False, objectP=None, is_remote=False):
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

        self.opt = opt
        self.debug = debug
        self.debugP = debugP
        self.is_remote = is_remote

        self.objectP = objectP
        self.object_data = None
        
        super(LaneKeepingProcess,self).__init__( inPs, outPs, debug)
        
    # ===================================== RUN ==========================================
    def run(self):
        """Apply the initializing methods and start the threads.
        """
        super(LaneKeepingProcess,self).run()

    # ===================================== INIT THREADS =================================
    def _init_threads(self):
        """Initialize the sending thread.
        """
        if self._blocker.is_set():
            return
        laneTh = Thread(name='LaneKeepingThread',target = self._run, args= (self.inPs[0], self.outPs[0]))
        laneObjectTh = Thread(name='ReadObjectDataThread',target = self._read_object_data_thread)
        laneTh.daemon = True
        laneObjectTh.daemon = True
        
        self.threads.append(laneTh)
        self.threads.append(laneObjectTh)


    def _read_object_data_thread(self):
        while True:
            try:
                data = self.objectP.recv()
                self.data_object_detection_lock.acquire()
                self.object_data = data
                self.data_object_detection_lock.release()
            except Exception as e:
                print("Lane Keeping - read object data thread error:")
                print(e)

    def _run(self, inP, outP):
        """Obtains image, applies the required image processing and computes the steering angle value. 
        
        Parameters
        ----------
        inP  : Pipe
            Input pipe to read the frames from other process.
        outP : Pipe
            Output pipe to send the steering angle value to other process.

        """

        LaneKeeper = LaneKeeping(self.opt, self.debug)
        while True:
            try:
                # Obtain image
                data = inP.recv()
                edge_image = data["new_combined_binary"]

                self.data_object_detection_lock.acquire()
                object_info = self.object_data
                self.object_data = None
                self.data_object_detection_lock.release()

                speed, angle, state, debug_data = LaneKeeper.lane_keeping(edge_image, object_info) 
                # new_angle = self.pid(angle)
                # setSpeed(outP[0], float(speed * 0.35))
                if not self.is_remote:
                    outP.send({"speed" : speed,
                            "angle" : angle,
                            "lane_data" : debug_data,})


                if self.debug: 
                    self.debugP.send(debug_data)

            except Exception as e:
                print("Lane keeping error:", e)


