import numpy as np
from threading import Thread,Condition
from src.templates.workerprocess import WorkerProcess
from src.data.localisationssystem.locsys import LocalisationSystem
from multiprocessing import Pipe

import time
import ast
class LocalizeProcess(WorkerProcess):
    def __init__(self,  outPs, opt, debugP=None, debug=False):
        self.opt = opt
        self.debug = debug
        self.debugP = debugP
        self.point= None
        self.beacon = 12345
        self.id = 1
        self.dummy = True
        self.localizeCondition = Condition()
        self.gpsStR,self.gpsStS  = Pipe(duplex = False)
        self.serverpublickey = 'src/data/localisationssystem/publickey_server_test.pem'
        super(LocalizeProcess,self).__init__( None, outPs)
        self.point=[0,0]


    def run(self):
        """Apply the initializing methods and start the threads.
        """
        super(LocalizeProcess,self).run()
    def _init_threads(self):
        """Initialize the sending thread.
        """
        if self._blocker.is_set():
            return
        if not self.dummy:
            LocalizeSytem = LocalisationSystem(self.id, self.beacon, self.serverpublickey, self.gpsStS)
        else:
            LocalizeSytem = None
        readTh = Thread(name='LocalizeThread',target = self._run )
        readTh.daemon = True
        update_data = Thread(name='Update localize',target=self.update_data_func)
        update_data.daemon=True
        self.threads.append(update_data)
        self.threads.append(readTh)
        self.threads.append(LocalizeSytem)


    def update_data_func(self):
        while True:
            coora = self.gpsStR.recv()
            self.point=[coora['coor'][1],coora['coor'][0]]


    def _run(self):
        """Obtains image, applies the required image processing and computes the steering angle value. 
        
        Parameters
        ----------
        inP  : Pipe
            Input pipe to read the frames from other process.
        outP : Pipe
            Output pipe to send the steering angle value to other process.

        """
        
        print('inited localize')
        while True:
            try:
                
                # if not self.dummy:
                #     # coora = self.gpsStR.recv()
                #     # self.point=[coora['coor'][0],coora['coor'][1]]
                #     # print(self.point)
                # else:
                #     self.point = [0,1]
                point = self.point
                self.debug_data = {"x": point[0], "y": point[1]}
                for outP in self.outPs:      # decision 
                    outP.send({"point" : point
                            })

                     
                # remote 
                
                if self.debug:
                    self.debugP.send(self.debug_data)
                time.sleep(0.05)
                if self.dummy:
                    time.sleep(0.05)
            except Exception as e:
                print("Localize error:", e)

def read_thread(gpsStR):
    global x,y
    # map_vis = MapVisualize([],'/home/topo/code/new_loc/localisationsystemserver/Track_Test_White.png')
    
    while True:
        
        raw = gpsStR.recv()
        x,y = raw['coor'][0],raw['coor'][1]
        # map_vis.plot([[x,y]])  
        print(x,y)  
if __name__ == '__main__':
    
    beacon = 12345
    id = 1
    serverpublickey = 'src/data/localisationssystem/publickey_server_test.pem'
    
    gpsStR, gpsStS = Pipe(duplex = False)
    
    LocalisationSystem = LocalisationSystem(id, beacon, serverpublickey, gpsStS)
    LocalisationSystem.start()  
    my_thread = Thread(target=read_thread, args=(gpsStR,))
    my_thread.daemon=True
    my_thread.start()
    while True:
        pass