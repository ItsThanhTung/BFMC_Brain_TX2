import numpy as np
from threading import Thread,Condition
from src.templates.workerprocess import WorkerProcess
from src.data.localisationssystem.locsys import LocalisationSystem
from multiprocessing import Pipe
import time
import ast
from pygraphml import GraphMLParser
from sklearn.metrics.pairwise import euclidean_distances
class LocalizeProcess(WorkerProcess):
    def __init__(self,  outPs, opt, debugP=None, debug=False):
        self.opt = opt
        self.debug = debug
        self.debugP = debugP
        self.point= None
        self.beacon = 12345
        self.id = 0x8704
        self.dummy = False
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
    def getClosetPoint(self,map_array,point):
        dist_arr = euclidean_distances([[point[0],point[1]]], map_array)
        closest_point = map_array[np.argmin(dist_arr)]
        return closest_point
    def _run(self):
        """Obtains image, applies the required image processing and computes the steering angle value. 
        
        Parameters
        ----------
        inP  : Pipe
            Input pipe to read the frames from other process.
        outP : Pipe
            Output pipe to send the steering angle value to other process.

        """
        parser = GraphMLParser()
        map = parser.parse('src/data/localisationssystem/Test_track.graphml')
        x=[]
        y=[]
        for node in map.nodes():
            x.append(node['d0'])
            y.append(node['d1'])
        x = np.array(x).astype(float)
        y = np.array(y).astype(float)
        map_array = np.array([[x,y] for x,y in zip(x,y)])

        print('inited localize')
        while True:
            try:
                if not self.dummy:
                    coora = self.gpsStR.recv()
                    coora = ast.literal_eval(coora)
                    self.point=[coora['coor'][1].real,coora['coor'][0].real]
                    # print(self.point)
                else:
                    self.point = [0,1]
                self.debug_data = {"x": self.point[0], "y": self.point[1]}
                # print(self.debug_data)
                for outP in self.outPs:      # decision 
                    outP.send({"point" : self.point
                            })

                     
                # remote 
                
                if self.debug:
                    closest_point = self.getClosetPoint(map_array,self.point)
                    self.debug_data = {"x": closest_point[0], "y": closest_point[1]}
                    print(self.debug_data)
                    self.debugP.send(self.debug_data)
                if self.dummy:
                    time.sleep(0.05)
            except Exception as e:
                print("Localize error:", e)
        