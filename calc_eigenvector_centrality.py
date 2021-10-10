
from helpfunctions import normalize_matrix_rows, calc_eigenvec_centrality_sectors, turn_df_to_networkx
import pandas as pd
import networkx as nx
import sys
import numpy as np
import math

# load in the nominal and real values for 2016
m2016_nominal = pd.read_csv('Data/matrices/2016_nominal.csv',index_col=0)
m2016_nominal_normalized = normalize_matrix_rows(m2016_nominal)


# illustrate differences; 
df_eigenvec_2016_nominal_right =pd.DataFrame(calc_eigenvec_centrality_sectors(m2016_nominal, 'right').items())
df_eigenvec_2016_nominal_right_normalized = pd.DataFrame(calc_eigenvec_centrality_sectors(m2016_nominal_normalized, 'right').items())

df_eigenvec_2016_nominal_right.columns = ['sector', 'value']
df_eigenvec_2016_nominal_right_normalized.columns = ['sector', 'value']


df_eigenvec_2016_nominal_right.sort_values(by=['value'], ascending = False).head(5)
df_eigenvec_2016_nominal_right_normalized.sort_values(by=['value'], ascending = False).head(5)



years = ['2015', '2016', '2017', '2018', '2019']

def visualize_top_x_sectors(years, type_eigenvec,type_matrix, x):
    
    l_df_top_x_sectors = []
    
    for year in years:
        
        mYear = pd.read_csv('Data/matrices/' + year + '_' +type_matrix + '.csv', index_col = 0)
        mYear_normalized = normalize_matrix_rows(mYear)
        
        eigenvec = calc_eigenvec_centrality_sectors(mYear_normalized, type_eigenvec)
        df_eigenvec = pd.DataFrame(eigenvec.items())
        df_eigenvec.columns = ['sector_' + year, 'value_' + year]
        
        df_eigenvec_sorted = df_eigenvec.sort_values(by=['value_' + year], ascending = False)
        
        top_sectors_eigenvec = df_eigenvec_sorted.head(x).reset_index(drop=True)
        l_df_top_x_sectors.append(top_sectors_eigenvec)
        
    df_top_x_sectors_years = pd.concat(l_df_top_x_sectors, axis = 1)
    return df_top_x_sectors_years
    


# normalize these (row sums)
m2016_nominal_normalized = normalize_matrix_rows(m2016_nominal)
m2016_real_normalized = normalize_matrix_rows(m2016_real)


# get the eigenvector centrality - right (outward)
eigenvec_nominal_right = calc_eigenvec_centrality_sectors(m2016_nominal_normalized, 'right')
eigenvec_real_right = calc_eigenvec_centrality_sectors(m2016_real_normalized, 'right')


# get the eigenvector centrality - left (inward)
eigenvec_nominal_left = calc_eigenvec_centrality_sectors(m2016_nominal_normalized, 'left')
eigenvec_real_left = calc_eigenvec_centrality_sectors(m2016_real_normalized, 'left')

eigenvec_nominal_right.items()
# Put all the results together, round to 4 digits, create dataframe
l_eigenvectors_nominal_real_2016 = [eigenvec_nominal_right, 
                                    eigenvec_real_right,
                                    eigenvec_nominal_left,
                                    eigenvec_real_left]

for dict_value in l_eigenvectors_nominal_real_2016:
    for k, v in dict_value.items():
        dict_value[k] = round(v, 20)
        
# use this dataframe for table in latex        
df_eigenvectors_nominal_real_2016 = pd.DataFrame.from_records(l_eigenvectors_nominal_real_2016).transpose()
df_eigenvectors_nominal_real_2016.columns = [ 'nominal_right','real_right', 'nominal_left', 'real_left']
df_eigenvectors_nominal_real_2016.sort_values(by=["nominal_right"], ascending = False) 


# visualize: top 5 over years, real and nominal
df_top_5_sectors_years_real = round(visualize_top_x_sectors(years, 'right', 'real', 5), 4)
df_top_5_sectors_years_nominal = round(visualize_top_x_sectors(years, 'right', 'nominal', 5),4)



