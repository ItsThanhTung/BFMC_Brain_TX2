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

import sys
sys.path.append('.')

import time
import socket
import struct
import numpy as np


import cv2
from threading import Thread
import pickle

import json
from src.templates.workerprocess import WorkerProcess


class DataReceiverProcess(WorkerProcess):
    # ===================================== INIT =========================================
    def __init__(self, inPs, outPs, port,check_length = False):
        """Process used for debugging. Can be used as a direct frame analyzer, instead of using the VNC
        It receives the images from the raspberry and displays them.

        Parameters
        ----------
        inPs : list(Pipe)  
            List of input pipes
        outPs : list(Pipe) 
            List of output pipes
        """
        super(DataReceiverProcess,self).__init__(inPs, outPs)
        
        self.port = port
        self.check_length = check_length
    # ===================================== RUN ==========================================
    def run(self):
        """Apply the initializers and start the threads. 
        """
        self._init_socket()
        super(DataReceiverProcess,self).run()

    # ===================================== INIT SOCKET ==================================
    def _init_socket(self):
        """Initialize the socket server. 
        """
        self.serverIp   =   '0.0.0.0'
        
        self.server_socket = socket.socket()
        self.server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.server_socket.bind((self.serverIp, self.port))

        self.server_socket.listen(0)
        self.connection = self.server_socket.accept()[0]#.makefile('rb')

    # ===================================== INIT THREADS =================================
    def _init_threads(self):
        """Initialize the read thread to receive and display the frames.
        """
        readTh = Thread(name='StreamReceivingThread',target = self._read_stream, args= (self.outPs,))
        self.threads.append(readTh)

    # ===================================== READ STREAM ==================================
    def _read_stream(self, outPs):
        """Read the image from input stream, decode it and display it with the CV2 library.
        """
        try:
            while True:
                try:

                # decode image
                    image_len = struct.unpack('<L', self.connection.recv(struct.calcsize('<L')))[0]
                    bts = self.connection.recv(image_len)
                    # ----------------------- read image -----------------------
                    str_data = bts.decode('UTF-8')
                    if self.check_length:
                        if str_data.count('{') != 1 or str_data.find('{') != 0:
                            print('error')
                            continue
                        
                        json_data = json.loads(str_data) 
                    for outP in outPs:
                        outP.send(json_data)
                except Exception as e:
                    continue

        except Exception as e:
            # self.server_socket.listen(0)
            # self.connection = self.server_socket.accept()[0]
            print('localize error ',e)
            pass
        finally:
            self.server_socket.close()
