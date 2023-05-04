from MapVisualize import MapVisualize, graph2arr
import time
import matplotlib.pyplot as plt
import networkx as nx
import joblib
def main():
    # G = nx.read_graphml('Test_track.graphml', node_type=int)
    # paths = list(nx.all_simple_paths(G, 38, 111))
    # print(len(paths))
    raw_data = joblib.load('/home/topo/code/new_loc/localisationsystemserver/data_17_43.pkl')
    print(len(raw_data))
    raw_data = [i for i in raw_data if not(i[0] == 0 and i[1] == 0)]
    print(len(raw_data))
    graph  =  graph2arr ('Test_track.graphml' ,allow_duplicates=True)
    map_vis  =  MapVisualize (graph,  'Track_Test_White.png' )
    map_vis.plot_w_interval(raw_data,color= 'red' ,save= True ,interval= 0.05)
    plt.pause(5)
if __name__ ==   '__main__' :
    main()