from src.templates.workerprocess import WorkerProcess
import numpy as np
from pygraphml import GraphMLParser
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances

from threading import Thread
class LocalizeDebugProcess(WorkerProcess):
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

        super(LocalizeDebugProcess,self).__init__( inPs, outPs)
        
    # ===================================== RUN ==========================================
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
        localizeShowTh.daemon = True
        self.threads.append(localizeShowTh)


    def _run(self):
        parser = GraphMLParser()
        map = parser.parse('src/data/localisationssystem/Test_track.graphml')
        x=[]
        y=[]
        for node in map.nodes():
            x.append(node['d0'])
            y.append(node['d1'])
        x = np.array(x).astype(float)
        y = np.array(y).astype(float)

        fig, ax = plt.subplots(figsize=(6.4, 4.8))
        fig.gca().invert_yaxis()
        (ln,) = ax.plot(x, y,marker='o', markerfacecolor='blue', markersize=12)

        for i,point in enumerate(zip(x,y)):
            ax.annotate(i+1,(point[0],point[1]))
        plt.show(block=False)
        plt.pause(0.1)
        bg = fig.canvas.copy_from_bbox(fig.bbox)
        # ax.draw_artist(ln)
        fig.canvas.blit(fig.bbox)

        map_arr=[[x,y]for x,y in zip(x,y)]

        data = []
     
        while True:
            try:
                # Obtain image
                for  inP in self.inPs:
                    point = inP.recv()
                    passed = []
                    fig.canvas.restore_region(bg)
                    dist_arr = euclidean_distances([[point['x'],point['y']]], map_arr)
                    closest_point = np.argmin(dist_arr)
                    data.append(point)
                    np.save('data.npy',data)
                    # if closest_point not in passed:
                    #     passed.append(closest_point)
                    #     (ln,)=plt.plot(map_arr[closest_point][0],map_arr[closest_point][1], marker="o",markerfacecolor='green', markersize=12)
                    #     ax.draw_artist(ln)
                    #     bg = fig.canvas.copy_from_bbox(fig.bbox)
                    (ln,)=plt.plot(point['x'],point['y'], marker="o",markerfacecolor='red', markersize=12)
                    ax.draw_artist(ln)
                    # (ln,)=plt.plot(map_arr[closest_point][0],map_arr[closest_point][1], marker="o",markerfacecolor='yellow', markersize=12)
                    
                    # ax.draw_artist(ln)
                    fig.canvas.blit(fig.bbox)
                    fig.canvas.flush_events()
                    # fig.pause(0.1)
            except Exception as e:
                print("Localize show error:")
                print(e)

