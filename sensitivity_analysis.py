# -*- coding: utf-8 -*-
"""
Created on Tue Sep 28 14:32:32 2021

@author: flori
"""

import pandas as pd
from helpfunctions import simulate_matrices, get_CI_eigenvector_centrality

m2019_real = pd.read_csv('Data/matrices/2019_real.csv',index_col=0)

simulated_m2019_real = simulate_matrices(m2019_real, 0.1, 100)
        
t = get_CI_eigenvector_centrality(simulated_m2019_real)

