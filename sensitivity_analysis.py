# -*- coding: utf-8 -*-
"""
Created on Tue Sep 28 14:32:32 2021

@author: flori
"""

import pandas as pd
from helpfunctions import simulate_matrices, get_CI_eigenvector_centrality, calc_eigenvec_centrality_sectors, normalize_matrix_rows


m2019_real = pd.read_csv('Data/matrices/2019_real.csv',index_col=0)
m2019_real_normalized = normalize_matrix_rows(m2019_real)

# which are hit in lockdown
sectors_hit_in_lockdown = ['Travel services', 'Air Transport', 'Restaurants']

m2019_real_corona = m2019_real.drop(sectors_hit_in_lockdown, axis=1).drop(sectors_hit_in_lockdown, axis=0)
m2019_real_corona_normalized = normalize_matrix_rows(m2019_real_corona)


# check each 
m2019_real_eigenvector = calc_eigenvec_centrality_sectors(m2019_real_normalized, 'left')
m2019_real_corona_eigenvector =calc_eigenvec_centrality_sectors(m2019_real_corona_normalized, 'left')


m2019_real_normalized
simulated_m2019_real = simulate_matrices(m2019_real, 0.1, 100, keep_zero=True)


matrix_test = simulated_m2019_real[1]
matrix_test_normalized = normalize_matrix_rows(matrix_test)

calc_eigenvec_centrality_sectors(matrix_test_normalized, 'left')

CI_eigenvec_simulated_m2019_real = get_CI_eigenvector_centrality(simulated_m2019_real, 'left')

