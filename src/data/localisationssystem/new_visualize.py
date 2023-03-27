import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from numpy.linalg import norm
import random
from pygraphml import GraphMLParser
from sklearn.metrics.pairwise import euclidean_distances
def cal_distance(p1, p2,p3):
    p1,p2,p3=np.array(p1),np.array(p2),np.array(p3)
    return norm(np.cross(p2-p1, p1-p3))/norm(p2-p1)



#array of nodes
parser = GraphMLParser()
map = parser.parse('Test_track.graphml')
x=[]
y=[]
for node in map.nodes():
    x.append(node['d0'])
    y.append(node['d1'])
x = np.array(x).astype(float)
y = np.array(y).astype(float)
map_arr=[[x,y]for x,y in zip(x,y)]

#plot nodes
my_graph = {}
G = nx.read_graphml('Test_track.graphml')
for node in G.nodes(data=True):
    my_graph[node[0]] = [node[1]["x"], node[1]["y"]]
nx.draw(G, pos=my_graph,with_labels=True)



data = np.load('data.npy',allow_pickle=True)[1:]
error_array=[]
for x_choose in data:
    dist_arr = euclidean_distances([[x_choose[0],x_choose[1]]], map_arr)
    p1 = map_arr[np.argmin(dist_arr)]
    dist_arr[0][np.argmin(dist_arr)]=999
    p2 = map_arr[np.argmin(dist_arr)]
    error_array.append(cal_distance(p1,p2,x_choose))

error_array=np.asarray(error_array)    
print(error_array.shape)
print(np.max(error_array))
print(np.mean(error_array))
print(np.min(error_array))

print((error_array<0.1).sum())

# for point in data:
#     plt.plot(point[0],point[1], marker="o",markerfacecolor='red', markersize=12)


plt.show()
# trajectory = ["38", "39", "40", "41", "42", "43", "44", "18", "19",\
            #   "13", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "2", "9",\
            #   "5", "76", "77", "78", "79", "80", "81", "82", "83", "84", "85", "86", "87", "23", "28", \
            #   "24", "103", "4", "9",\
            #   "1", "60", "61", "62", "63", "64", "65", "66", "67", "68", "69", "70", "71", "14", "19",\
            #   "15", "72", "73", "8", \
            #   "9", "3", "104", "25", "28", \
            #   "26", "105", "106", "107", "108", "109", "110", "111"]
# print(len(trajectory))