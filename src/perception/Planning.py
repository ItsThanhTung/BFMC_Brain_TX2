from math import radians
import numpy as np
import math


class Planning:
    def __init__(self, init_x=0, init_y=0):
        # Model parameters
        self.prev_point = (init_x, init_y)
        self.x = init_x
        self.y = init_y
        self.cur_angle = 0
        self.count = 0
        
        
    def update_point(self, point):
        if self.count == 10:
            self.prev_point = (self.x, self.y)
            self.count = 0
            
        self.x = point['x']
        self.y = point['y']
        
        self.count += 1
        

    def drive(self, tar_point):
        curr_point = np.array([self.x, self.y])
        dist = np.linalg.norm([tar_point - curr_point])
        
        print("dist: ", dist)
        
        if True:
            vec1 = self.prev_point - curr_point
            vec2 = tar_point- curr_point

            def left_or_right(prev_point, cur_point, tar_point):
                d = (tar_point[0] - prev_point[0]) * (cur_point[1] - prev_point[1]) - (tar_point[1] - prev_point[1]) * (cur_point[0] - prev_point[0])
                if d > 0:
                    return 1
                
                elif d < 0:
                    return -1
                
                else:
                    return 0


            direction = left_or_right(self.prev_point, curr_point, tar_point)

            if direction != 0:
                angle = 180 - math.degrees(math.acos(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))))
                angle *= direction
                
                angle = np.clip(angle * 0.7, -23, 23)
                
            else:
                angle = 0
            
            self.prev_point = curr_point
            self.cur_angle = angle
            
            return angle

