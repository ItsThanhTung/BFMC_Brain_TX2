from sklearn.metrics.pairwise import euclidean_distances
from pygraphml import GraphMLParser
import numpy as np


class Point:
    def __init__(self):
        
        self.map_arr = np.load('src/data/localisationssystem/map_arr.npy')
        self.cur_pos = {'x':0,'y':0}
        self.trajectory = np.array([10, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 0, 109, 110, 111, 112, 5, 61, 62, 116, 117, 118, 119])
        self.trajectory_map = [self.map_arr[i] for i in self.trajectory]
        
        self.map_arr = np.loadtxt('trajectory.txt')[:, ::-1]
        self.trajectory = np.arange(len(self.map_arr))
    
    def getClosestNode(self):
        dist_arr = euclidean_distances([[self.cur_pos['x'],self.cur_pos['y']]], self.map_arr)
        closest_idx = np.argmin(dist_arr)
        closest_point = self.trajectory[closest_idx]
        return closest_point, self.get_point(closest_point)
    
    
    def getNextPoint(self, node=None):
        if node is None:
            node = self.getClosestNode()

        next_point = np.where(self.trajectory==node)[0][0]

        if next_point == len(self.trajectory)-1:
            return self.trajectory[0], self.get_point(self.trajectory[0])
        else:
            return self.trajectory[next_point+1], self.get_point(self.trajectory[next_point+1])
        
    def get_point(self, idx):
        return self.map_arr[idx]
        
        
    