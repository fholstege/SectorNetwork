# -*- coding: utf-8 -*-
"""
Created on Tue Sep 28 14:32:32 2021

@author: flori
"""

import pandas as pd
from helpfunctions import simulate_matrices, get_CI_eigenvector_centrality, calc_eigenvec_centrality_sectors, normalize_matrix_rows, remove_isolated_sectors, table_eigenvec


# nominal 2019, clean, normalized
m2019_nominal = pd.read_csv('Data/matrices/2016_nominal.csv',index_col=0)
m2019_nominal_clean = remove_isolated_sectors(m2019_nominal)
m2019_nominal_normalized = normalize_matrix_rows(m2019_nominal_clean)


# which are hit in lockdown
sectors_hit_in_lockdown = ['Travel services', 'Air Transport', 'Restaurants']

# drop these sectors from lockdown
m2019_nominal_corona = m2019_nominal_clean.drop(sectors_hit_in_lockdown, axis=1).drop(sectors_hit_in_lockdown, axis=0)
m2019_nominal_corona_normalized = normalize_matrix_rows(m2019_nominal_corona)


# check each 
m2019_nominal_eigenvector = calc_eigenvec_centrality_sectors(m2019_nominal_clean, 'right')
m2019_nominal_corona_eigenvector =calc_eigenvec_centrality_sectors(m2019_nominal_corona_normalized, 'right')

table_eigenvec(m2019_nominal_eigenvector).sort_values(by = ['value'], ascending = False).head(10)
table_eigenvec(m2019_nominal_corona_eigenvector).sort_values(by = ['value'], ascending = False).head(10)


########## robustness measurement error

sd_1 = 5/1.96
sd_2 = 10/1.96

### check how prone to measure errors - first, which sectors in general are most important
simulated_m2019_p0_0_sd_5 = simulate_matrices(abs(m2019_nominal_clean), sd_1, 100, 0)
simulated_m2019_p0_10_sd_5 = simulate_matrices(m2019_nominal_clean,sd_1, 100, 0.1)
simulated_m2019_p0_0_sd_10 = simulate_matrices(m2019_nominal_clean, sd_2, 100, 0)
simulated_m2019_p0_10_sd_10 = simulate_matrices(m2019_nominal_clean,sd_2, 100, 0.1)



# calc the confidence intervals
CI_eigenvec_simulated_m2019_p0_0_sd_5 = get_CI_eigenvector_centrality(simulated_m2019_p0_0_sd_5, 'right').sort_values(by=['avg'], ascending=False)
CI_eigenvec_simulated_m2019_p0_10_sd_5 = get_CI_eigenvector_centrality(simulated_m2019_p0_10_sd_5, 'right').sort_values(by=['avg'], ascending=False)
CI_eigenvec_simulated_m2019_p0_0_sd_10 = get_CI_eigenvector_centrality(simulated_m2019_p0_0_sd_10, 'right').sort_values(by=['avg'], ascending=False)
CI_eigenvec_simulated_m2019_p0_10_sd_10 = get_CI_eigenvector_centrality(simulated_m2019_p0_10_sd_10, 'right').sort_values(by=['avg'], ascending=False)



years = ['2015', '2016', '2017', '2018', '2019']

def visualize_top_x_sectors_CI(years, type_matrix,type_eigenvec, x, sd, p_0,n_sims=100):
    
    l_df_top_x_sectors_CI = []
    
    for year in years:
        print('currently on year: ' + year)
        
        mYear = pd.read_csv('Data/matrices/' + year + '_' +type_matrix + '.csv', index_col = 0)
        mYear_clean = abs(remove_isolated_sectors(mYear))
        print('busy simulating...')
        simulated_mYear = simulate_matrices(mYear_clean, sd, n_sims, p_0)

        CI_eigenvec_simulated_mYear = get_CI_eigenvector_centrality(simulated_mYear, type_eigenvec).sort_values(by=['avg'], ascending=False)
        

        top_sectors_CI = CI_eigenvec_simulated_mYear.head(x)
        entry = top_sectors_CI.index.map(str) +': ' + round(top_sectors_CI['avg'],2).map(str) + ' [' + round(top_sectors_CI['lower_CI'],2).map(str) + '-' + round(top_sectors_CI['upper_CI'],2).map(str) + ']' 

        l_df_top_x_sectors_CI.append(entry.reset_index(drop=True))
        
    df_top_x_sectors_years_CI = pd.concat(l_df_top_x_sectors_CI, axis = 1)
    return df_top_x_sectors_years_CI
    

p_0 = 0
df_top_x_sectors_CI_p0_0_sd_5 = visualize_top_x_sectors_CI(years, 'nominal', 'right', 5, sd_1, p_0)
print(df_top_x_sectors_CI_p0_0_sd_5.to_latex())