from time import sleep
from multiprocessing import Pipe
from threading import Thread


if __name__=='__main__':
    from server_data import ServerData
    from server_listener import ServerListener
    from server_subscriber import ServerSubscriber
    from position_listener import PositionListener
else:
    from src.data.localisationssystem.server_data import ServerData
    from src.data.localisationssystem.server_listener import ServerListener
    from src.data.localisationssystem.server_subscriber import ServerSubscriber
    from src.data.localisationssystem.position_listener import PositionListener
from PIL import Image
import ast
import json
import time
from pygraphml import GraphMLParser
from pygraphml import Graph
import matplotlib.pyplot as plt
import numpy as np

# from sklearn.metrics.pairwise import euclidean_distances

class LocalisationSystem(Thread):
    
    def __init__(self, ID, beacon, serverpublickey, streamPipe):
        """ GpsTracker targets to connect on the server and to receive the messages, which incorporates 
        the coordinate of the robot on the race track. It has two main state, the setup state and the listening state. 
        In the setup state, it creates the connection with server. It's receiving  the messages from the server in the listening
        state. on

        It's a thread, so can be running parallel with other threads. You can access to the received parameters via 'coor' function.

        """
        super(LocalisationSystem, self).__init__()
        #: serverData object with server parameters
        self.__server_data = ServerData(beacon)
        #: discover the parameters of server
        self.__server_listener = ServerListener(self.__server_data)
        #: connect to the server
        self.__subscriber = ServerSubscriber(self.__server_data, ID, serverpublickey)
        #: receive and decode the messages from the server
        self.__position_listener = PositionListener(self.__server_data, streamPipe)
        
        self.__running = True

    def setup(self):
        """Actualize the server's data and create a new socket with it.
        """
        # Running while it has a valid connection with the server
        while(self.__server_data.socket == None and self.__running):
            # discover the parameters of server
            self.__server_listener.find()
            if self.__server_data.is_new_server and self.__running:
                # connect to the server 
                self.__subscriber.subscribe()
        
    def listen(self):
        """ Listening the coordination of robot
        """
        self.__position_listener.listen()

    def run(self):
        while(self.__running):
            self.setup()
            self.listen()
            
    def stop(self):
        """Terminate the thread running.
        """
        self.__running = False
        self.__server_listener.stop()
        self.__position_listener.stop()

if __name__ == '__main__':
    # parser = GraphMLParser()
    # map = parser.parse('Test_track.graphml')
    # x=[]
    # y=[]
    # for node in map.nodes():
    #     x.append(node['d0'])
    #     y.append(node['d1'])
    # x = np.array(x).astype(float)
    # y = np.array(y).astype(float)
    beacon = 12345
    id = 0x1705
    serverpublickey = 'src/data/localisationssystem/publickey_server_test.pem'
    gpsStR, gpsStS = Pipe(duplex = False)

    LocalisationSystem = LocalisationSystem(id, beacon, serverpublickey, gpsStS)
    LocalisationSystem.start()  
    
    fig, ax = plt.subplots(figsize=(6.4, 4.8))
    # fig.gca().invert_yaxis()

    # x_tag,y_tag=(0.74,5.59)
    # plt.plot(x, y,marker='o', markerfacecolor='blue', markersize=12)
    # for i,point in enumerate(zip(x,y)):
    #     ax.annotate(i+1,(point[0],point[1]))
    # plt.plot(x_tag,y_tag, marker="o",markerfacecolor='red', markersize=12)
    # fig.canvas.draw()
    # img =Image.frombytes('RGB', fig.canvas.get_width_height(),fig.canvas.tostring_rgb())
    # img.save('image.jpg')
    # map_arr=[[x,y]for x,y in zip(x,y)]
    # np.save('map.npy',map_arr)
    # dist_arr = euclidean_distances([[x_tag,y_tag]], map_arr)
    # print(np.argmin(dist_arr)+1)
    time.sleep(3)
    data=[]
    while True:
        try:
            coora = gpsStR.recv()
            coora = ast.literal_eval(coora)
            #mo file a.jpg de xem ket qua realtime
            x_tag,y_tag=coora['coor'][1].real,coora['coor'][0].real
            # plt.plot(x_tag,y_tag, marker="o",markerfacecolor='red', markersize=12)
            # data.append([x_tag,y_tag])       
            print(x_tag,y_tag)
            
            sleep(0.005)            
        except KeyboardInterrupt:
            break
    LocalisationSystem.stop()

    LocalisationSystem.join()
