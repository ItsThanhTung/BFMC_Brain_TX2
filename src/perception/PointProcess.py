from sklearn.metrics.pairwise import euclidean_distances
from pygraphml import GraphMLParser
import numpy as np
import joblib

class Point:
    def __init__(self):
        self.main_map_path = 'src/data/localisationssystem/semifinal.txt'
        self.sub_map_arr = 'src/data/localisationssystem/sub_semifinal.txt'
        
        self.main_map_arr = None
        self.sub_map_arr = None
        
        self.map_arr = self.main_map_arr
        
        self.main_trajectory = np.arange(len(self.main_map_arr))
        self.sub_trajectory = np.arange(len(self.sub_map_arr))

        self.trajectory = self.main_trajectory
        self.local_node = None

    
    def load_map(self,main_map=True):
        map_arr = []
        if main_map:
            with open(self.main_map_path,'r') as f:
                lines = f.readlines()
                for line in lines:
                    line = line[:-1].split(' ')
                    map_arr.append([float(line[0]),float(line[1])])
                self.main_map_arr = map_arr
        else:
            with open(self)
            self.sub_map_arr = map_arr
    def switch_to_sub_map(self):
        print("switch to sub")
        self.map_arr = self.sub_map_arr
        self.trajectory = self.sub_trajectory
        self.local_node = None
    def switch_to_main_map(self):
        print("switch to main")
        self.map_arr = self.main_map_arr
        self.trajectory = self.main_trajectory
        self.local_node = None
    def get_closest_node(self, pose):
        if self.local_node is None:
            dist_arr = euclidean_distances([[pose['x'], pose['y']]], self.map_arr)
            closest_idx = np.argmin(dist_arr)
            closet_dist = dist_arr[0][closest_idx]
            
        else:
           
            dist_arr = euclidean_distances([[pose['x'], pose['y']]], [self.map_arr[i] for i in self.local_node])
            closest_idx = np.argmin(dist_arr)
            closet_dist = dist_arr[0][closest_idx]
            closest_idx = self.local_node[closest_idx]

        self.local_node = self.trajectory[closest_idx:] if closest_idx > len(self.trajectory) - 4 \
                                                        else self.trajectory[closest_idx:closest_idx+3]

        for i in range(self.local_node[0]):
            self.map_arr[i] = [1000, 1000]

        # return node_name, distant from current position to that node.
        return self.local_node[0], closet_dist, self.local_node

        
    def get_point(self, idx):
        return self.map_arr[idx]
        
        
    