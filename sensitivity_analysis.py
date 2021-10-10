# -*- coding: utf-8 -*-
"""
Created on Tue Sep 28 14:32:32 2021

@author: flori
"""

import pandas as pd
from helpfunctions import simulate_matrices, get_CI_eigenvector_centrality, calc_eigenvec_centrality_sectors, normalize_matrix_rows


# real 2019, 
m2019_real = pd.read_csv('Data/matrices/2019_real.csv',index_col=0)




# which are hit in lockdown
sectors_hit_in_lockdown = ['Travel services', 'Air Transport', 'Restaurants']

# drop these sectors from lockdown
m2019_real_corona = m2019_real.drop(sectors_hit_in_lockdown, axis=1).drop(sectors_hit_in_lockdown, axis=0)
m2019_real_corona_normalized = normalize_matrix_rows(m2019_real_corona)


# check each 
m2019_real_eigenvector = calc_eigenvec_centrality_sectors(m2019_real, 'right', normalize = False,)
m2019_real_corona_eigenvector =calc_eigenvec_centrality_sectors(m2019_real_corona_normalized, 'right')

# create dataframes
df_2019_real_eigenvector  = pd.DataFrame(m2019_real_eigenvector.items())
df_2019_real_eigenvector.columns = ['sector', 'eigenvec']

df_2019_real_corona_eigenvector  = pd.DataFrame(m2019_real_corona_eigenvector.items())
df_2019_real_corona_eigenvector.columns = ['sector', 'eigenvec']


# check top x sectors - travel services dissapears
x = 10
df_2019_real_top_sectors = df_2019_real_eigenvector.sort_values(by=['eigenvec'],ascending = False).head(x)
df_2019_real_corona_top_sectors = df_2019_real_corona_eigenvector.sort_values(by=['eigenvec'],ascending = False).head(x)


### check how prone to measure errors - first, which sectors in general are most important
simulated_m2019_real_keepzero = simulate_matrices(m2019_real_normalized, 0.1, 100, keep_zero=True)
simulated_m2019_real_changezero = simulate_matrices(m2019_real_normalized, 0.1, 100, keep_zero=False)

# calc the confidence intervals
CI_eigenvec_simulated_m2019_real_keepzero = get_CI_eigenvector_centrality(simulated_m2019_real_keepzero, 'right').sort_values(by=['avg'], ascending=False)
CI_eigenvec_simulated_m2019_real_changezero = get_CI_eigenvector_centrality(simulated_m2019_real_changezero, 'right').sort_values(by=['avg'], ascending=False)



years = ['2015', '2016', '2017', '2018', '2019']

def visualize_top_x_sectors_CI(years, type_matrix,type_eigenvec, x, keep_zero,n_sims = 100, sd_perc_mean = 0.1):
    
    l_df_top_x_sectors_CI = []
    
    for year in years:
        
        mYear = pd.read_csv('Data/matrices/' + year + '_' +type_matrix + '.csv', index_col = 0)
        mYear_normalized = normalize_matrix_rows(mYear)
        simulated_mYear = simulate_matrices(mYear_normalized, sd_perc_mean, n_sims, keep_zero=keep_zero)

        CI_eigenvec_simulated_mYear = get_CI_eigenvector_centrality(simulated_mYear, 'right').sort_values(by=['avg'], ascending=False)
        

        top_sectors_CI = CI_eigenvec_simulated_mYear['avg'].head(x).reset_index(drop=True)
        l_df_top_x_sectors_CI.append(top_sectors_CI)
        
    df_top_x_sectors_years_CI = pd.concat(l_df_top_x_sectors_CI, axis = 1)
    return df_top_x_sectors_years_CI
    
