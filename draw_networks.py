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

# load in the nominal values for 2019, calc eigenvector
m2016_nominal = pd.read_csv('Data/matrices/2016_nominal.csv',index_col=0)
#m2016_nominal_normalized = normalize_matrix_rows(m2016_nominal)


### Visualize the real (2016) network
networkx_m2016_nominal = turn_df_to_networkx(m2016_nominal)


labels = nx.get_edge_attributes(networkx_m2016_nominal,'weight')
pos=nx.spring_layout(networkx_m2016_nominal, k=15, iterations = 20) 

pos_attrs = {}
for node, coords in pos.items():
    x = coords[0]
    y = coords[1]
    
    if y <0:
        y_adjustment = -0.05
    else:
        y_adjustment= 0.05
        
    if x <0:
        x_adjustment = -0.05
    else:
        x_adjustment= 0.05
    
    pos_attrs[node] = (x + x_adjustment, y + y_adjustment)


widths = nx.get_edge_attributes(networkx_m2016_nominal, 'weight')
nodelist = networkx_m2016_nominal.nodes()
edgewidths = [element/500 for element in widths.values() ]

nx.draw_networkx_nodes(networkx_m2016_nominal,
                       pos,
                       nodelist=nodelist,
                       node_size=300,
                       node_color='lightblue',
                       edgecolors='none',
                       alpha=0.8)
nx.draw_networkx_edges(networkx_m2016_nominal,
                       pos,
                       edgelist = widths.keys(),
                       width=edgewidths,
                       edge_color='orange',
                       alpha=0.7)
nx.draw_networkx_labels(networkx_m2016_nominal, pos=pos_attrs,
                        labels=dict(zip(nodelist,nodelist)),
                        font_color='black',
                        font_family="monospace",
                        font_size=10)