# -*- coding: utf-8 -*-
"""
Created on Tue Sep 28 16:24:30 2021

@author: flori
"""
from helpfunctions import normalize_matrix_rows, calc_eigenvec_centrality_sectors, turn_df_to_networkx
import pandas as pd
import networkx as nx
import sys
import numpy as np
import math

# load in the real values for 2019, calc eigenvector
m2019_real = pd.read_csv('Data/matrices/2019_real.csv',index_col=0)
m2019_real_eigenvector = calc_eigenvec_centrality_sectors(m2019_real)

### Visualize the real (2019) network

networkx_m2019_real = turn_df_to_networkx(m2019_real)


labels = nx.get_edge_attributes(networkx_m2019_real,'weight')
pos=nx.spring_layout(networkx_m2019_real)#, k=8/math.sqrt(networkx_m2019_real.order())) 

isolates = nx.isolates(networkx_m2019_real)
networkx_m2019_real.remove_nodes_from(list(isolates))


widths = nx.get_edge_attributes(networkx_m2019_real, 'weight')
nodelist = networkx_m2019_real.nodes()
nodesizes = list(m2019_real_eigenvector.values())[:-1]
nodesizes = [element * 20000 for element in nodesizes]
edgewidths = [element*10 for element in widths.values() ]

nx.draw_networkx_nodes(networkx_m2019_real,
                       pos,
                       nodelist=nodelist,
                       node_size=nodesizes,
                       node_color='lightblue',
                       edgecolors='black',
                       alpha=0.7)
nx.draw_networkx_edges(networkx_m2019_real,
                       pos,
                       edgelist = widths.keys(),
                       width=edgewidths,
                       edge_color='red',
                       alpha=0.7)
nx.draw_networkx_labels(networkx_m2019_real, pos=pos,
                        labels=dict(zip(nodelist,nodelist)),
                        font_color='black',
                        font_family="sans-serif",
                        font_size=12)