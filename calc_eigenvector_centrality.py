
from helpfunctions import normalize_matrix_rows, calc_eigenvec_centrality_sectors, turn_df_to_networkx, remove_isolated_sectors, table_eigenvec
import pandas as pd
import networkx as nx
import sys
import numpy as np
import math

# load in the nominal and real values for 2016
m2016_nominal = pd.read_csv('Data/matrices/2016_nominal.csv',index_col=0)
m2016_nominal_clean = remove_isolated_sectors(m2016_nominal)
m2016_nominal_normalized = normalize_matrix_rows(m2016_nominal_clean)

#
m2016_real = pd.read_csv('Data/matrices/2016_real.csv',index_col=0)
m2016_real_clean = remove_isolated_sectors(m2016_real)
m2016_real_normalized = normalize_matrix_rows(m2016_real_clean)



# illustrate differences; 
df_eigenvec_2016_nominal_right =pd.DataFrame(calc_eigenvec_centrality_sectors(m2016_nominal_clean, 'right').items())
df_eigenvec_2016_nominal_right_normalized = pd.DataFrame(calc_eigenvec_centrality_sectors(m2016_nominal_normalized, 'right').items())

df_eigenvec_2016_nominal_right.columns = ['sector', 'value']
df_eigenvec_2016_nominal_right_normalized.columns = ['sector', 'value']


df_eigenvec_2016_nominal_right.sort_values(by=['value'], ascending = False).head(5)
df_eigenvec_2016_nominal_right_normalized.sort_values(by=['value'], ascending = False).head(5)



years = ['2015', '2016', '2017', '2018', '2019']



def visualize_top_x_sectors(years, type_eigenvec,type_matrix, x, top):
    
    l_df_top_x_sectors = []
    
    for year in years:
        
        mYear = pd.read_csv('Data/matrices/' + year + '_' +type_matrix + '.csv', index_col = 0)
        mYear_clean = remove_isolated_sectors(mYear)
        
        mYear_normalized = normalize_matrix_rows(mYear_clean)
                
        eigenvec = calc_eigenvec_centrality_sectors(mYear_normalized, type_eigenvec)
        df_eigenvec = pd.DataFrame(eigenvec.items())
        df_eigenvec.columns = ['sector_' + year, 'value_' + year]
        
        df_eigenvec_sorted = df_eigenvec.sort_values(by=['value_' + year], ascending = False)
        
        if top:
            sectors = df_eigenvec_sorted.head(x).reset_index(drop=True)
        else:
            sectors = df_eigenvec_sorted.tail(x).reset_index(drop=True)
            
        l_df_top_x_sectors.append(sectors['sector_'+year])
        
    df_top_x_sectors_years = pd.concat(l_df_top_x_sectors, axis = 1)
    return df_top_x_sectors_years
    



# get the eigenvector centrality - right (outward)
eigenvec_nominal_right = calc_eigenvec_centrality_sectors(m2016_nominal_normalized, 'right')
eigenvec_real_right = calc_eigenvec_centrality_sectors(m2016_real_normalized, 'right')


# tables
table_eigenvec(eigenvec_nominal_right).sort_values(by = ['value'], ascending=False).head(5)
table_eigenvec(eigenvec_real_right).sort_values(by = ['value'], ascending=False).head(5)


# visualize: top 5 over years, real and nominal
df_top_5_sectors_years_real = round(visualize_top_x_sectors(years, 'right', 'real', 5, top = True), 4)
df_top_5_sectors_years_nominal = round(visualize_top_x_sectors(years, 'right', 'nominal', 5, top = True),4)

df_bottom_5_sectors_years_nominal = round(visualize_top_x_sectors(years, 'right', 'real', 5, top = False), 4)
df_bottom_5_sectors_years_real = round(visualize_top_x_sectors(years, 'right', 'real', 5, top = False), 4)

print(df_bottom_5_sectors_years_nominal.to_latex())
print(df_bottom_5_sectors_years_real.to_latex())

df_top_77_sectors_years_nominal = round(visualize_top_x_sectors(years, 'right', 'nominal', 80, top = True), 4)
df_top_77_sectors_years_nominal.index = range(1,77+1)
print(df_top_77_sectors_years_nominal.to_latex())