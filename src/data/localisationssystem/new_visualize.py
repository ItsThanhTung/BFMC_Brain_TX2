import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

G = nx.read_graphml('Test_track.graphml')
my_graph = {}

node_idx = []

for node in G.nodes(data=True):
    my_graph[node[0]] = [node[1]["x"], node[1]["y"]]
nx.draw(G, pos=my_graph,with_labels=True)
data = np.load('data.npy',allow_pickle=True)[1:]
for point in data:
    plt.plot(point[0],point[1], marker="o",markerfacecolor='red', markersize=12)


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