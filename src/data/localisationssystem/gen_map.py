import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import time
from pygraphml import GraphMLParser
from mpl_point_clicker import clicker
from sklearn.metrics.pairwise import euclidean_distances
FROM_BEGIN = False
if FROM_BEGIN:
    parser = GraphMLParser()
    map = parser.parse('src/data/localisationssystem/Test_track.graphml')
    x=[]
    y=[]

    for i,node in enumerate(map.nodes()):
        if i==0:
            continue
        x.append(node['d0'])
        y.append(node['d1'])
    x = np.array(x).astype(float)
    y = np.array(y).astype(float)
    map_arr_raw=[[x,y]for x,y in zip(x,y)]
    map_arr=[]
    [map_arr.append(point) for point in map_arr_raw if point not in map_arr]
else:
    map_arr = np.load('src/data/localisationssystem/map_arr.npy').to_list()
img = plt.imread('Track_Test_White.png')
img = np.fliplr(img)


while True:
    fig, ax = plt.subplots(figsize=(6.4, 4.8))
    ax.imshow(img,extent=[0,6,0,6])
    fig.gca().invert_yaxis()
    x = [row[0] for row in map_arr]
    y = [row[1] for row in map_arr]
    ax.plot(x,y,marker='o', markerfacecolor='blue',linestyle='None', markersize=6,)
    for i, point in enumerate(map_arr):
        ax.annotate(i, (point[0], point[1]), fontsize=6, weight='bold')
    klicker = clicker(ax, ["event"], markers=["o"])
    plt.show(block=False)
    i = input()
    if i == 'q':
        break
    new_points = klicker.get_positions()['event']
    if i == 'a':
        for point in new_points:
            map_arr.append(point)
    if i == 'r':
        for point in new_points:
            dist_arr = euclidean_distances([point],map_arr)
            node = map_arr[np.argmin(dist_arr)]
            print(node)
            map_arr.remove(node)
    
    print(klicker.get_positions())
    plt.close()

np.save('src/data/localisationssystem/map_arr.npy',map_arr)
