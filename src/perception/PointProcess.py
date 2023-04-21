from sklearn.metrics.pairwise import euclidean_distances
from pygraphml import GraphMLParser
import numpy as np
import joblib

class Point:
    def __init__(self):
        
        trajectory = [0,1,2,3,4,5,18,29,30,6,7,8,9,10,11,12,13,14,15,16,17]
        map_arr_full = joblib.load('src/data/localisationssystem/data__21_04_10_26.pkl')
        map_arr=[]
        for i in trajectory:
            map_arr.append(map_arr_full[i])
        self.cur_pos = {'x':0,'y':0}
        self.trajectory_map = self.map_arr
        print("map len: ",len(self.map_arr))
        # self.map_arr = np.loadtxt('trajectory.txt')[:, ::-1]
        self.trajectory = trajectory
    
    def getClosestNode(self):
        dist_arr = euclidean_distances([[self.cur_pos['x'],self.cur_pos['y']]], self.map_arr)
        closest_idx = np.argmin(dist_arr)
        closest_point = self.trajectory[closest_idx]
        print(closest_idx)
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
        
        
    