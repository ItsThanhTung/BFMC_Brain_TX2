from src.templates.workerprocess import WorkerProcess
import numpy as np
from pygraphml import GraphMLParser
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances
from matplotlib.markers import MarkerStyle
from threading import Thread, Condition
import joblib

class LocalizeDebugProcess(WorkerProcess):
    localize_condition = Condition()
    filter_condition = Condition()
    # ===================================== INIT =========================================
    def __init__(self, inPs, outPs,filter = True):
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

        super(LocalizeDebugProcess,self).__init__( inPs, outPs)
        self.filter = filter
        self.localize_data = {"x":0, "y":0}
        self.filter_data = {"x":0, "y":0, "Heading":0}
        self.main_map_path = 'src/data/localisationssystem/semifinal.txtt'
        self.sub_map_path='src/data/localisationssystem/sub_semifinal.txtt'
        self.main_map = None
        self.sub_map = None
        self.map_bg_path  = 'src/data/localisationssystem/gray_not.jpg'
    # ===================================== RUN ==========================================
    def load_map(self,main_map=True):
        map_arr = []
        with open(self.main_map_path,'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line[:-1].split(' ')
                map_arr.append([float(line[0]),float(line[1])])
        if main_map:
            self.main_map = map_arr
    def run(self):
        """Apply the initializing methods and start the threads.
        """
        super(LocalizeDebugProcess,self).run()

    # ===================================== INIT THREADS =================================
    def _init_threads(self):
        """Initialize the sending thread.
        """
        if self._blocker.is_set():
            return
        localizeShowTh = Thread(name='LocalizeShowProcessThread',target = self._run)
        recvLocalizeTh = Thread(name='recvLocalize',target = self.recvLocalize)
        recvFilter = Thread(name='recvFilter',target = self.recvFilter)
        
        localizeShowTh.daemon = True
        recvLocalizeTh.daemon = True
        recvFilter.daemon = True
        
        self.threads.append(localizeShowTh)
        self.threads.append(recvLocalizeTh)
        self.threads.append(recvFilter)

    def recvLocalize(self):
        while True:
            try:
                data = self.inPs['localize'].recv()
                self.localize_condition.acquire()
                self.localize_data = data
                self.localize_condition.notify()
                self.localize_condition.release()

            except Exception as e:
                print("Localize Debug Process - recvLocalize thread error:")
                print(e)
                
                
    def recvFilter(self):
        while True:
            try:
                data = self.inPs['filter'].recv()
                self.filter_condition.acquire()
                self.filter_data = data
                self.filter_condition.notify()
                self.filter_condition.release()

            except Exception as e:
                print("Localize Debug Process - recvLocalize thread error:")
                print(e)
            
            
    def _run(self):
        img = plt.imread(self.map_bg_path)
        self.load_map()
        map_arr =  self.main_map

        x = [row[0] for row in map_arr]
        y = [row[1] for row in map_arr]

        fig, ax = plt.subplots(figsize=(13.0, 7.0))
        # img = np.fliplr(img)
        ax.imshow(np.flipud(img), origin='upper',extent=[0,14.65,0,15])
        fig.gca().invert_yaxis()
        (ln,) = ax.plot(x, y,marker='o', markerfacecolor='blue',linestyle='None', markersize=6,)
        
        for i,point in enumerate(zip(x,y)):
           
            ax.annotate(i,(point[0],point[1]),fontsize=6,weight = 'bold')
        plt.show(block=False)
        plt.pause(0.1)
        bg = fig.canvas.copy_from_bbox(fig.bbox)
        # ax.draw_artist(ln)
        fig.canvas.blit(fig.bbox)

        # map_arr=[[x,y]for x,y in zip(x,y)]
        
        while True:
            if True:
                # Obtain image

                
                self.localize_condition.acquire()
                point_raw = self.localize_data
                self.localize_condition.release()
                
                self.filter_condition.acquire()
                point_filter = self.filter_data
                self.filter_condition.release()
                

                passed = []
                fig.canvas.restore_region(bg)
                if not(point_filter['x'] == 0 and point_filter['y'] == 0):
                    dist_arr = euclidean_distances([[point_filter['x'],point_filter['y']]], map_arr)
                    closest_point = np.argmin(dist_arr)
                    if closest_point not in passed:
                        passed.append(closest_point)
                        (ln,)=plt.plot(map_arr[closest_point][0],map_arr[closest_point][1], marker="o",markerfacecolor='green', markersize=6)
                        ax.draw_artist(ln)
                        bg = fig.canvas.copy_from_bbox(fig.bbox)
                (ln,)=plt.plot(point_raw['x'],point_raw['y'], marker="o",markerfacecolor='red', markersize=6)
                ax.draw_artist(ln)
                if self.filter:
                    marker_raw = MarkerStyle("$>$")
                    marker_raw._transform.rotate_deg(np.rad2deg(point_filter['Heading']))
                    (ln,)=plt.plot(point_filter['x'],point_filter['y'], marker=marker_raw,markerfacecolor='yellow', markersize=10)
                    ax.draw_artist(ln)
                # (ln,)=plt.plot(map_arr[closest_point][0],map_arr[closest_point][1], marker="o",markerfacecolor='yellow', markersize=12)
                
                # ax.draw_artist(ln)
                fig.canvas.blit(fig.bbox)
                fig.canvas.flush_events()
                # fig.pause(0.1)
            # except Exception as e:
            #     print("Localize show error:")
            #     print(e)

