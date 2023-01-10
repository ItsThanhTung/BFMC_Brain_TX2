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

from threading import Thread
from simple_pid import PID

from src.templates.workerprocess import WorkerProcess
from src.image_processing.LaneKeeping import LaneKeeping

from src.utils.utils_function import setSpeed, setAngle, EnablePID


class LaneKeepingProcess(WorkerProcess):
    pid = PID(Kp = 1.0, Ki = 1.45, Kd = 0.15, output_limits = [-23, 23])
    # ===================================== INIT =========================================
    def __init__(self, inPs, outPs, opt, debugP=None, debug=False):
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
        laneTh = Thread(name='LaneKeepingThread',target = self._run, args= (self.inPs[0], self.outPs,))
        laneTh.daemon = True
        self.threads.append(laneTh)


    def _run(self, inP, outPs):
        """Obtains image, applies the required image processing and computes the steering angle value. 
        
        Parameters
        ----------
        inP  : Pipe
            Input pipe to read the frames from other process.
        outP : Pipe
            Output pipe to send the steering angle value to other process.

        """
        for outP in outPs:
            EnablePID(outP)

        LaneKeeper = LaneKeeping(self.opt, self.debug)

        while True:
            try:
                # Obtain image
                data = inP.recv()
                edge_image = data["new_combined_binary"]
                speed, angle, state, debug_data = LaneKeeper.lane_keeping_v2(edge_image) 

                # new_angle = self.pid(angle)
                # setSpeed(outP[0], float(speed * 0.35))
                print(angle)
                for outP in outPs:
                    setSpeed(outP, float(0))
                    setAngle(outP , float(angle))

                if self.debug: 
                    self.debugP.send(debug_data)

            except Exception as e:
                print("Lane keeping error:", e)


