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
        self.id = 0x1705
        self.dummy = True
        self.localizeCondition = Condition()
        self.gpsStR,self.gpsStS  = Pipe(duplex = False)
        self.serverpublickey = 'src/data/localisationssystem/publickey_server_test.pem'
        super(LocalizeProcess,self).__init__( None, outPs)
        
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
        self.threads.append(readTh)
        self.threads.append(LocalizeSytem)
    def _run(self):
        """Obtains image, applies the required image processing and computes the steering angle value. 
        
        Parameters
        ----------
        inP  : Pipe
            Input pipe to read the frames from other process.
        outP : Pipe
            Output pipe to send the steering angle value to other process.

        """
        print('in localize')
        while True:
            try:
                if not self.dummy:
                    coora = self.gpsStR.recv()
                    coora = ast.literal_eval(coora)
                    self.point=[coora['coor'][1].real,coora['coor'][0].real]
                else:
                    self.point = [0,1]
                self.debug_data = f"x: {self.point[0]} y: {self.point[1]}"
                for out in self.outPs:      # decision 
                    out.send({"point" : self.point
                            })

                     
                # remote 
                if self.debug:
                    print(f'localize debug')
                    self.debugP.send(self.debug_data)
                

                
                time.sleep(0.005)
            except Exception as e:
                print("Localize error:", e)
        