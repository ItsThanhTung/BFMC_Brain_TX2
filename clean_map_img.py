import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import time
from pygraphml import GraphMLParser
from mpl_point_clicker import clicker
from sklearn.metrics.pairwise import euclidean_distances
import joblib
from MapVisualize import graph2arr
from matplotlib.markers import MarkerStyle
FROM_BEGIN = True
filename = 'compete.pkl'
map_arr = graph2arr('/home/topo/code/BFMC_Brain_TX2/Competition_track.graphml',allow_duplicates=True)
img = plt.imread('/home/topo/code/localisationssystem/gray_not.jpg')
trajec_order=[8,range(139,144),15,63,range(196,171,-1),range(265,230,-1)]

# trajec_order = [86,77,78,87,45,42,98,99,4,7,range(134,137),16,13,145,61,62,range(148,171),range(198,230),range(267,287)]
# del trajec_order[15]
trajec = []

for i in trajec_order:
    if isinstance(i, range):
        for j in i:
            trajec.append(j)
    else:
        trajec.append(i)
trajec = [map_arr[i] for i in trajec]
map_arr = trajec
map_arr=[]
with open('/home/topo/code/localisationssystem/gps_log.txtt') as f:
    raw = f.readlines()
    for line in raw:
        line = line[:-1].split(' ')
        map_arr.append([float(line[0]),float(line[1])])
        
map_filter = []
with open('/home/topo/code/localisationssystem/gps_log_filtered.txtt') as f:
    raw = f.readlines()
    for line in raw:
        line = line[:-1].split(' ')
        map_filter.append([float(line[0]),float(line[1]),float(line[2])])
# marker_raw = MarkerStyle("$>$")
# marker_raw._transform.rotate_deg(np.rad2deg())
while True:
    fig, ax = plt.subplots(figsize=(13.0, 7.0))
    ax.imshow(np.flipud(img), origin='upper',extent=[0,14.65,0,15])
    fig.gca().invert_yaxis()
    x = [row[0] for row in map_arr]
    y = [row[1] for row in map_arr]
    for pos in zip(x, y):
        ax.plot(pos[0],pos[1],marker='o', markerfacecolor='blue',linestyle='None', markersize=6,)
    
    x = [row[0] for row in map_filter]
    y = [row[1] for row in map_filter]
    Heading = [row[2] for row in map_filter]
    for pos in zip(x,y,Heading):
        marker_raw = MarkerStyle("$>$")
        marker_raw._transform.rotate_deg(np.rad2deg(pos[2]))
        ax.plot(pos[0],pos[1],marker=marker_raw, markerfacecolor='pink',linestyle='None', markersize=6,)
    
    
    
    
    # for i, point in enumerate(map_arr):
    #     ax.annotate(i, (point[0], point[1]), fontsize=6, weight='bold')
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
    if i == 'c':
        dist_arr = euclidean_distances([new_points[0]],map_arr)
        map_arr[np.argmin(dist_arr)] = new_points[1]
    if i == 's':
        with open('sub_semifinal.txt','w') as f:
            for i in map_arr:
                f.write(f"{i[0]} {i[1]}\n")
            
        # joblib.dump(map_arr,filename)
    print(klicker.get_positions())
    plt.close()
# np.save('src/data/localisationssystem/map_arr.npy',map_arr)
