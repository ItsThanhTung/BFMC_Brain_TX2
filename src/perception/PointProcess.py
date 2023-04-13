from sklearn.metrics.pairwise import euclidean_distances
from pygraphml import GraphMLParser
import numpy as np
class Point:
    def __init__(self):
        graphFile = 'src/data/localisationssystem/Test_track.graphml'
        parser = GraphMLParser()
        map = parser.parse('src/data/localisationssystem/Test_track.graphml')
        x=[]
        y=[]
        for node in map.nodes():
            x.append(node['d0'])
            y.append(node['d1'])
        x = np.array(x).astype(float)
        y = np.array(y).astype(float)
        self.map_arr = [[x,y]for x,y in zip(x,y)]
        self.cur_pos = {'x':0,'y':0}
    def getClosestPoint(self):
        dist_arr = euclidean_distances([[self.cur_pos['x'],self.cur_pos['y']]], self.map_arr)
        closest_point = np.argmin(dist_arr)
        return self.map_arr[closest_point]
        
    