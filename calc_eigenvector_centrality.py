
from helpfunctions import normalize_matrix_rows, calc_eigenvec_centrality_sectors, turn_df_to_networkx
import pandas as pd
import networkx as nx
import sys
import numpy as np
import math

m2019_nominal = pd.read_csv('Data/matrices/2019_nominal.csv',index_col=0)
m2019_real = pd.read_csv('Data/matrices/2019_real.csv',index_col=0)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

m2019_nominal_normalized = normalize_matrix_rows(m2019_nominal)
m2019_real_normalized = normalize_matrix_rows(m2019_real)


m2019_nominal_normalized_eigenvector = calc_eigenvec_centrality_sectors(m2019_nominal_normalized)
m2019_real_normalized_eigenvector = calc_eigenvec_centrality_sectors(m2019_real_normalized)
m2019_nominal_eigenvector = calc_eigenvec_centrality_sectors(m2019_nominal)
m2019_real_eigenvector = calc_eigenvec_centrality_sectors(m2019_real)


networkx_m2019_real = turn_df_to_networkx(m2019_real)
networkx_m2019_real_normalized = turn_df_to_networkx(m2019_real_normalized)

labels = nx.get_edge_attributes(networkx_m2019_real_normalized,'weight')
pos=nx.spring_layout(networkx_m2019_real_normalized, k=6/math.sqrt(networkx_m2019_real_normalized.order())) 

isolates = nx.isolates(networkx_m2019_real_normalized)
networkx_m2019_real_normalized.remove_nodes_from(list(isolates))


widths = nx.get_edge_attributes(networkx_m2019_real_normalized, 'weight')
nodelist = networkx_m2019_real_normalized.nodes()
nodesizes = list(m2019_real_normalized_eigenvector.values())[:-1]
nodesizes = [element * 20000 for element in nodesizes]
edgewidths = [element*10 for element in widths.values() ]

nx.draw_networkx_nodes(networkx_m2019_real_normalized,
                       pos,
                       nodelist=nodelist,
                       node_size=nodesizes,
                       node_color='lightgreen',
                       alpha=0.7)
nx.draw_networkx_edges(networkx_m2019_real_normalized,
                       pos,
                       edgelist = widths.keys(),
                       width=edgewidths,
                       edge_color='blue',
                       alpha=0.7)
nx.draw_networkx_labels(networkx_m2019_real_normalized, pos=pos,
                        labels=dict(zip(nodelist,nodelist)),
                        font_color='black')