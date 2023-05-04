import numpy as np
import matplotlib.pyplot as plt
from pygraphml import GraphMLParser
import time

def graph2arr(graph_path,allow_duplicates=False):
    parser = GraphMLParser()
    map = parser.parse(graph_path)
    map_arr_raw = [[0,0]]
    map_dict = {}
    for i, node in enumerate(map.nodes()):
        map_dict[int(node.id)] = [float(node['d0']), float(node['d1'])]
    for i in sorted(list(map_dict.keys())):
        map_arr_raw.append(map_dict[i])
    map_arr = []
    if not allow_duplicates:
        [map_arr.append(point) for point in map_arr_raw if point not in map_arr]
        return map_arr
    else:
        return map_arr_raw


class MapVisualize:
    def __init__(self, map_arr, background):
        self.map_arr = map_arr
        img = plt.imread(background)
        img = np.fliplr(img)
        self.fig, self.ax = plt.subplots(figsize=(6.4, 4.8))
        self.ax.imshow(img, extent=[0, 6, 0, 6])
        self.fig.gca().invert_yaxis()
        x = [row[0] for row in map_arr]
        y = [row[1] for row in map_arr]
        self.ax.plot(x, y, marker='o', markerfacecolor='blue', linestyle='None', markersize=6, )
        for i, point in enumerate(map_arr):
            self.ax.annotate(i, (point[0], point[1]), fontsize=6, weight='bold')
        plt.show(block=False)
        plt.pause(0.1)
        self.bg = self.fig.canvas.copy_from_bbox(self.fig.bbox)
        self.fig.canvas.blit(self.fig.bbox)
    def plot(self, point_arr, color='red',save=False):
        self.fig.canvas.restore_region(self.bg)
        for point in point_arr:
            (ln,) = plt.plot(point[1], point[0], marker='o', markerfacecolor=color, linestyle='None', markersize=6, )
            self.ax.draw_artist(ln)
        if save:
            self.bg = self.fig.canvas.copy_from_bbox(self.fig.bbox)
        self.fig.canvas.blit(self.fig.bbox)
        self.fig.canvas.flush_events()
    def plot_w_interval(self, point_arr, color='red', interval=0.1,save=False):
        for point in point_arr:
            self.plot([point], color=color,save=save)
            time.sleep(interval)