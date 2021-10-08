
from helpfunctions import normalize_matrix_rows, calc_eigenvec_centrality_sectors, turn_df_to_networkx
import pandas as pd
import networkx as nx
import sys
import numpy as np
import math

# load in the nominal and real values for 2019
m2016_nominal = pd.read_csv('Data/matrices/2016_nominal.csv',index_col=0)
m2016_real = pd.read_csv('Data/matrices/2016_real.csv',index_col=0)


# normalize these (row sums)
m2016_nominal_normalized = normalize_matrix_rows(m2016_nominal)
m2016_real_normalized = normalize_matrix_rows(m2016_real)

calc_eigenvec_centrality_sectors(m2016_nominal_normalized, 'left', weight = 'weight')


# calculate the eigenvector for each
m2019_nominal_normalized_eigenvector = calc_eigenvec_centrality_sectors(m2019_nominal_normalized, 'left')
m2019_real_normalized_eigenvector = calc_eigenvec_centrality_sectors(m2019_real_normalized, 'left')


# Put all the results together, round to 4 digits, create dataframe
l_eigenvectors_nominal_real_2019 = [
                                    m2019_nominal_normalized_eigenvector,
                                    m2019_real_normalized_eigenvector]

for dict_value in l_eigenvectors_nominal_real_2019:
    for k, v in dict_value.items():
        dict_value[k] = round(v, 8)
        
# use this dataframe for table in latex        
df_eigenvectors_nominal_real_2019 = pd.DataFrame.from_records(l_eigenvectors_nominal_real_2019).transpose()
df_eigenvectors_nominal_real_2019.columns = [  'nominal_normalized','real_normalized']
