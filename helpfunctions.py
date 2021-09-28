import pandas as pd
import numpy as np
import scipy.linalg as la
import networkx as nx




def load_matrix(matrix_type, year):
    
    # define sheet name
    sheet_name = str(year) + '_' + matrix_type

    # gather data
    df_sectors_2015 = pd.read_excel('Data/Input_Output_2015_2019_Nominal_Real_updated.xlsx', 
                                sheet_name=sheet_name,
                                index_col=0)
    
    # get relevant rows and columns
    matrix_sectors =  df_sectors_2015.iloc[0:80,0:80]
    
    return matrix_sectors

def calc_price_change_matrix(nominal_matrix, previous_year_price_matrix):
    
    price_change = (nominal_matrix - previous_year_price_matrix)/(previous_year_price_matrix)
    price_change_formatted = price_change.replace(np.nan,0)
    
    return price_change_formatted + 1




def calc_real_matrices(l_nominal_matrices, l_previous_year_prices_matrices):
    
    n_matrices = len(l_nominal_matrices)
    real_matrices = []
    
    for i in range(0,n_matrices):

        
        if i == 0:
            real_matrix = l_nominal_matrices[i]
            real_matrices.append(real_matrix)
        else:
            
            
            for j in range(0, i ):

                previous_year_price_matrix = l_previous_year_prices_matrices[j]
                nominal_matrix = l_nominal_matrices[j+1]

                
                price_change_matrix = calc_price_change_matrix(nominal_matrix, previous_year_price_matrix)

            if i==1:
                price_change_matrix_years = price_change_matrix
            else:
                price_change_matrix_years = price_change_matrix_years * price_change_matrix

            current_nominal_matrix = l_nominal_matrices[i]
            
       
            
            real_matrix = current_nominal_matrix.div(price_change_matrix_years)
            real_matrices.append(real_matrix)
        
    return real_matrices


def turn_df_to_networkx(df_sectors):
    networkx_sectors = nx.from_pandas_adjacency(df_sectors)
    return networkx_sectors

def calc_eigenvec_centrality_sectors(df_sectors):
    networkx_sectors = turn_df_to_networkx(df_sectors)
    
    eigenvector_centrality_sectors = nx.eigenvector_centrality_numpy(networkx_sectors)
    
    return eigenvector_centrality_sectors

def normalize_matrix_rows(df_sectors):
    rowSums_sectors = df_sectors.sum(axis=1)

    df_sectors_normalized = df_sectors.div(rowSums_sectors, axis=0)
    df_sectors_normalized= df_sectors_normalized.replace(np.nan,0)
    
    return df_sectors_normalized
    


