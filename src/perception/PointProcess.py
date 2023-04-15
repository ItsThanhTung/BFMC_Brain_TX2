from sklearn.metrics.pairwise import euclidean_distances
from pygraphml import GraphMLParser
import numpy as np


class Point:
    def __init__(self):
        graphFile = 'src/data/localisationssystem/Test_track.graphml'
        parser = GraphMLParser()
        map = parser.parse('src/data/localisationssystem/Test_track.graphml')
        
        x = []
        y = []
        for node in map.nodes():
            x.append(node['d0'])
            y.append(node['d1'])
            
        x = np.array(x).astype(float)
        y = np.array(y).astype(float)
        
        self.map_arr = [[x,y] for x,y in zip(x,y)]
        self.cur_pos = {'x':0,'y':0}
        self.trajectory = np.array([16, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 1, 118, 8, 119, 6, 73, 74, 14, 120, 18, 121])
        
    
    def getClosestNode(self):
        dist_arr = euclidean_distances([[self.cur_pos['x'],self.cur_pos['y']]], self.map_arr)
        closest_point = np.argmin(dist_arr)
        return closest_point
    
    
    def getNextPoint(self, node=None):
        if node is None:
            node = self.getClosestNode()
        print(node)
        next_point = np.where(self.trajectory==node)[0][0]

        if next_point == len(self.trajectory)-1:
            return self.trajectory[0]
        else:
            return self.trajectory[next_point+1]
        
    def get_point(self, idx):
        return self.map_arr[idx]
        
        
    