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

from threading import Thread

from src.templates.workerprocess import WorkerProcess
from src.image_processing.InterceptDetection import InterceptDetection


class InterceptDetectionProcess(WorkerProcess):
    # ===================================== INIT =========================================
    def __init__(self, inPs, outPs, opt, debugP = None, debug=False, is_remote=False):
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

        super(InterceptDetectionProcess,self).__init__( inPs, outPs)

        self.debug = debug
        self.debugP = debugP
        self.opt = opt
        self.is_remote = is_remote

        
    # ===================================== RUN ==========================================
    def run(self):
        """Apply the initializing methods and start the threads.
        """
        super(InterceptDetectionProcess,self).run()

    # ===================================== INIT THREADS =================================
    def _init_threads(self):
        """Initialize the sending thread.
        """
        if self._blocker.is_set():
            return
        
        interceptDetectionTh = Thread(name='interceptDetectionTh',target = self._run_intercept_detection)
        interceptDetectionTh.daemon = True
        self.threads.append(interceptDetectionTh)


    def _run_intercept_detection(self):
        intercept_detector = InterceptDetection(self.opt, debug=self.debug)
        while True:
            try:
                data = self.inPs["IMAGE_PREPROCESSING"].recv()
                image = data["sybinary"]
                max_intercept_length, debug_data = intercept_detector.detect(image)
                
                if not self.is_remote:
                    self.outPs["DECISION_MAKING"].send(max_intercept_length)

                if self.debug:
                    self.debugP.send(debug_data)
                
            except Exception as e:
                print("Intercept Detection - intercept detection thread error:")
                print(e)

    


            
