
from helpfunctions import normalize_matrix_rows, calc_eigenvec_centrality_sectors
import pandas as pd
import networkx as nx

m2019_nominal = pd.read_csv('Data/matrices/2019_nominal.csv',index_col=0)
m2019_real = pd.read_csv('Data/matrices/2019_real.csv',index_col=0)


m2019_nominal_normalized = normalize_matrix_rows(m2019_nominal)
m2019_real_normalized = normalize_matrix_rows(m2019_real)


m2019_nominal_normalized_eigenvector = calc_eigenvec_centrality_sectors(m2019_nominal_normalized)
m2019_real_normalized_eigenvector = calc_eigenvec_centrality_sectors(m2019_real_normalized)
m2019_nominal_eigenvector = calc_eigenvec_centrality_sectors(m2019_nominal)
m2019_real_eigenvector = calc_eigenvec_centrality_sectors(m2019_real)

