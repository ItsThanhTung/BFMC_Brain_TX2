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

from threading import Thread, Condition
from src.templates.workerprocess import WorkerProcess

from src.hardware.data_fusion.DataFusion import DataFusion

class DataFusionProcess(WorkerProcess):
    flag_condition = Condition()
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

        self.isSet = False
        self.data_fuser = DataFusion()
        
        super(DataFusionProcess,self).__init__(inPs, outPs)

        
    # ===================================== RUN ==========================================
    def run(self):
        """Apply the initializing methods and start the threads.
        """
        super(DataFusionProcess,self).run()

    # ===================================== INIT THREADS =================================
    def _init_threads(self):
        """Initialize the sending thread.
        """
        if self._blocker.is_set():
            return
        
        imageReadTh = Thread(name='IMUListenerThread',target = self._read_image, args= (self.inPs["LANE_IMAGE"],))
        imagePreprocessTh = Thread(name='EncoderListenerThread',target = self._run_image_preprocessing)


    # def _read_encoder_data
    
    def _decision_making_listener(self):
        while True:
            try:
                data = self.inPs["DECISION_MAKING_FLAG"].recv()
                self.flag_condition.acquire()
                self.isSet = data
                self.flag_condition.notify()
                self.flag_condition.release()

            except Exception as e:
                print("Data Fusion - decision making listener thread error:")
                print(e)
    
            
    def _fuse_data(self):
        while True:
            try:     
                
                self.flag_condition.acquire()               
                if not self.isSet:
                    self.flag_condition.wait()
                        
                    print("start encoder")
                    print("start imu")
                    
                else:
                    self.flag_condition.release()       
                    print("read imu")
                    print("encoder_data")
                    imu_data = 0
                    encoder_data = 0
                    data = self.data_fuser.fuse(imu_data, encoder_data)
                    self.outPs["DECISION_MAKING"].send({"data" : data})
            
                
            except Exception as e:
                print("Data Fusion - fuse data thread error:")
                print(e)
            