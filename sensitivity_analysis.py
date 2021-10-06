# -*- coding: utf-8 -*-
"""
Created on Tue Sep 28 14:32:32 2021

@author: flori
"""

import pandas as pd
from helpfunctions import simulate_matrices, get_CI_eigenvector_centrality, calc_eigenvec_centrality_sectors

m2019_real = pd.read_csv('Data/matrices/2019_real.csv',index_col=0)
sectors_hit_in_lockdown = ['Travel services', 'Air Transport', 'Restaurants']

m2019_real_corona = m2019_real.drop(sectors_hit_in_lockdown, axis=1).drop(sectors_hit_in_lockdown, axis=0)


m2019_real_eigenvector = calc_eigenvec_centrality_sectors(m2019_real)
m2019_real_corona_eigenvector =calc_eigenvec_centrality_sectors(m2019_real_corona)

simulated_m2019_real = simulate_matrices(m2019_real, 0.1, 100)

t = [simulated_m2019_real[0], simulated_m2019_real[1]]
        
t_CI = get_CI_eigenvector_centrality(simulated_m2019_real, type_centrality = 'right')



calc_eigenvec_centrality_sectors(m2019_real)
calc_eigenvec_centrality_sectors(t[0])
    
l_eigenvec_results = []
for df_matrix in t:
        eigenvec_centrality = calc_eigenvec_centrality_sectors(df_matrix)
        l_eigenvec_results.append(eigenvec_centrality)