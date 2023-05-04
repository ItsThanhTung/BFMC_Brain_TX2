import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import time
from pygraphml import GraphMLParser
from mpl_point_clicker import clicker
from sklearn.metrics.pairwise import euclidean_distances
import joblib
FROM_BEGIN = False
filename = 'src/data/localisationssystem/compe.pkl'
else:
    # map_arr = np.load('src/data/localisationssystem/map_arr.npy').tolist()
    map_arr = joblib.load(filename)
    # map_arr = [[point[1],point[0]] for point in map_arr]
img = plt.imread('Competition_track.png')
# img = np.fliplr(img)


while True:
    fig, ax = plt.subplots(figsize=(13.0, 7.0))
        # img = np.fliplr(img)
    ax.imshow(np.flipud(img), origin='upper',extent=[0,14.65,0,15])
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
    if i == 'c':
        dist_arr = euclidean_distances([new_points[0]],map_arr)
        map_arr[np.argmin(dist_arr)] = new_points[1]
    if i == 's':
        # dist_arr = euclidean_distances([new_points[0]],map_arr)
        # map_arr[np.argmin(dist_arr)] = new_points[1]
        joblib.dump(map_arr,filename)
    print(klicker.get_positions())
    plt.close()
# np.save('src/data/localisationssystem/map_arr.npy',map_arr)
