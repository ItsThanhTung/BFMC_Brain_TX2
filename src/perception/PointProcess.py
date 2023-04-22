from sklearn.metrics.pairwise import euclidean_distances
from pygraphml import GraphMLParser
import numpy as np
import joblib

class Point:
    def __init__(self):
        
        trajectory = np.array([0,1,2,3,4,5,18,29,30,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,2,3,4,5,18,29,30])
        self.map_arr_full = joblib.load('src/data/localisationssystem/data__21_04_10_26.pkl')
        self.map_arr=[]
        for i in trajectory:
            self.map_arr.append(self.map_arr_full[i])
        self.cur_pos = {'x':0,'y':0}
        self.trajectory_map = self.map_arr
        print("map len: ",len(self.map_arr))
        # self.map_arr = np.loadtxt('trajectory.txt')[:, ::-1]
        self.trajectory = trajectory
        self.track = 0
        self.prev_point = None
        self.local_node = None
    def getClosestNode(self):
        
        if not self.prev_point:
            dist_arr = euclidean_distances([[self.cur_pos['x'],self.cur_pos['y']]], self.trajectory_map)
            closest_idx = np.argmin(dist_arr)
            closest_point = self.trajectory[closest_idx]
            print(f"closest: {self.cur_pos}")
            print(f"closest: {self.trajectory_map[26]}")
            print(f"closest: {self.map_arr_full[23]}")
            self.prev_point = closest_point
        else:
            if self.prev_point > len(self.trajectory_map)-4:
                dist_arr = euclidean_distances([[self.cur_pos['x'],self.cur_pos['y']]], self.trajectory_map)
                closest_idx = np.argmin(dist_arr)
                closest_point = self.trajectory[closest_idx]
                self.prev_point = closest_point
            else:
                next_point = np.where(self.trajectory==self.prev_point)[0][0]
                self.local_node = self.trajectory[next_point:next_point+3]
                print(f"prev:{self.prev_point} local: {self.local_node}")
                local_map = [self.map_arr_full[i] for i in self.trajectory[next_point:next_point+3]]
                dist_arr = euclidean_distances([[self.cur_pos['x'],self.cur_pos['y']]], local_map)
                closest_idx = np.argmin(dist_arr)
                closest_point = self.local_node[closest_idx]
                self.prev_point = closest_point
                for i in range(0,next_point):
                    self.trajectory[i]=99
        if closest_point == 17:
            self.track = 1
        
        return closest_point, self.get_point(closest_point)
    
    def getNextPoint(self, node=None):
        if node is None:
            node = self.getClosestNode()
        if not self.local_node is None:
            print(f"node: {node} local:{self.local_node}")
            next_points = np.where(self.local_node==node)[0]
            next_point = next_points[0]
        else:
            next_point = np.where(self.trajectory==node)[0][0]
            return self.trajectory[next_point+1], self.get_point(self.trajectory[next_point+1])
        if next_point == len(self.trajectory)-1:
            return self.trajectory[0], self.get_point(self.trajectory[0])
        else:
            return self.local_node[next_point+1], self.get_point(self.local_node[next_point+1])
        
    def get_point(self, idx):
        print(f'idx {idx}')
        return self.map_arr_full[idx]
        
        
    