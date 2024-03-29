import pandas as pd
import numpy as np
import scipy.linalg as la
import networkx as nx
import matplotlib.pyplot as plt 
import math

import readline
for i in range(readline.get_current_history_length()):
    print (readline.get_history_item(i + 1))

"""
Part 1: Loading matrices, and turning them from nominal to real
"""

# drop the ones
# check simulated matrices

def table_eigenvec(eigenvec_result):
    
    df_eigenvec = pd.DataFrame(eigenvec_result.items())
    df_eigenvec.columns = ['sector', 'value']
    
    return df_eigenvec


def remove_isolated_sectors(df):
    
    remove_rows = []
    
    
    for index, row in df.iterrows():
        n_non_zero_row = np.count_nonzero(row)
        
        if n_non_zero_row <= 1:
            
            remove_rows.append(index)

    df_rows_removed = df.drop(remove_rows, axis = 1).drop(remove_rows, axis = 0)

    remove_columns = []
    
    for col in df_rows_removed:
        
        n_non_zero_col = np.count_nonzero(df_rows_removed[col])
        
        if n_non_zero_col <= 1:
            
            remove_columns.append(col)
        
    df_cols_removed = df_rows_removed.drop(remove_columns, axis = 1).drop(remove_columns, axis = 0)
    
    return df_cols_removed


def load_matrix(matrix_type, year):
    """
    

    Parameters
    ----------
    matrix_type : string
        'real' or 'nominal'.
    year : int
        2015-2019.

    Returns
    -------
    matrix_sectors : dataframe
        80x80, all sectors.

    """
    
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
    """
    

    Parameters
    ----------
    nominal_matrix : dataframe
        matrix with nominal input-output.
    previous_year_price_matrix : dataframe
        matrix, same year as 'nominal_matrix', but in previous year prices.

    Returns
    -------
    dataframe
        matrix with the price changes between years.

    """
    
    # calc the price change, fill in nan's with zero
    price_change = (nominal_matrix - previous_year_price_matrix)/(previous_year_price_matrix)
    price_change_formatted = price_change.replace(np.nan,0)
    
    return price_change_formatted + 1




def calc_real_matrices(l_nominal_matrices, l_previous_year_prices_matrices):
    """
    

    Parameters
    ----------
    l_nominal_matrices : list
        each element is a dataframe with the input-output matrix in nominal prices.
    l_previous_year_prices_matrices : list
        each element is a dataframe with the input-output matrix in prices of the previous year.

    Returns
    -------
    real_matrices : list
        all the real matrices for the years.

    """
    
    # get n of matrices, list of real matrices
    n_matrices = len(l_nominal_matrices)
    real_matrices = []
    
    # loop over each
    for i in range(0,n_matrices):
        
        # for first, use as base year
        if i == 0:
            real_matrix = l_nominal_matrices[i]
            real_matrices.append(real_matrix)
        else:
            
            # calculate for each year the price change
            for j in range(0, i ):

                previous_year_price_matrix = l_previous_year_prices_matrices[j]
                nominal_matrix = l_nominal_matrices[j+1]
                price_change_matrix = calc_price_change_matrix(nominal_matrix, previous_year_price_matrix)

            # if multiple years, combine the price changes
            if i==1:
                price_change_matrix_years = price_change_matrix
            else:
                price_change_matrix_years = price_change_matrix_years * price_change_matrix

            # divide the nominal prices by the price change factor, get real matrix
            current_nominal_matrix = l_nominal_matrices[i]
            real_matrix = current_nominal_matrix.div(price_change_matrix_years)
            real_matrices.append(real_matrix)
        
    return real_matrices

"""
Part 2:functions for normalizing the matrix, and calculating the eigenvector centrality
"""

def turn_df_to_networkx(df_sectors):
    networkx_sectors = nx.from_pandas_adjacency(df_sectors,  nx.DiGraph)
    return networkx_sectors

def calc_eigenvec_centrality_sectors(df_sectors, type_centrality,  weight='weight'):
    
    # turn df to networkx
    networkx_sectors = turn_df_to_networkx(df_sectors)
    
    # by default, python does right vector eigencentrality
    if type_centrality == 'left':
        networkx_sectors = networkx_sectors.reverse()
    
    # use networkx function to calculate the eigenvector centrality
    eigenvector_centrality_sectors = nx.eigenvector_centrality_numpy(networkx_sectors, weight = weight)
    
    return eigenvector_centrality_sectors

def normalize_matrix_rows(df_sectors):
    # get row sums
    rowSums_sectors = df_sectors.sum(axis=1)
    
    # divide by row sum
    df_sectors_normalized = df_sectors.div(rowSums_sectors, axis=0)
    df_sectors_normalized= df_sectors_normalized.replace(np.nan,0)
    
    return df_sectors_normalized
    

"""
Part 3:functions for simulating matrices
"""

def simulate_matrices(base_matrix, sd, n_matrices, p_0):
    """
    

    Parameters
    ----------
    base_matrix : dataframe
        dataframe as given - values taken as mean.
    sd : float
        millions for the sd

    Returns
    -------
    l_simulated_matrices.
        list of dataframes, each a simulatedmatrix

    """
    
    # list - each a numpy array of the simulated values for a cell
    l_simulated_values = []
    
    # list - each a dataframe 
    l_simulated_matrices = []
    
    # get number of entries
    n_entries = base_matrix.shape[0]
    
    # get name of indeces
    indeces = base_matrix.index
    
    # loop over each cell
    for rowIndex, row in base_matrix.iterrows(): #iterate over rows
        for columnIndex, mean_value in row.items():
            
            sd_simulation = sd


            simulated_values_cell = []
                
            for i in range(0, n_matrices):
                
                simulated_value_cell = np.random.normal(mean_value, sd_simulation, None)

                
                if mean_value == 0:
                    biased_coin_flip = np.random.binomial(1,p_0,None)
                    
                    if biased_coin_flip ==0:
                        simulated_value_cell = 0
                
                    
                # accept reject
                while simulated_value_cell < 0:
                    simulated_value_cell = np.random.normal(mean_value, sd_simulation, None)
                    
                simulated_values_cell.append(simulated_value_cell)
                
            # simulate values of this cell            
            l_simulated_values.append(simulated_values_cell)
            
    df_simulations = pd.DataFrame.from_records(l_simulated_values)
    
    # create matrix based on the simulated values
    for i in range(0, n_matrices):
        
        simulation_result = df_simulations.iloc[:,i].values.reshape(n_entries,n_entries)
        simulated_matrix = pd.DataFrame(simulation_result)
        simulated_matrix.index = indeces
        simulated_matrix.columns = indeces
        l_simulated_matrices.append(simulated_matrix)
    
    return l_simulated_matrices



def get_CI_eigenvector_centrality(l_simulated_matrices, type_centrality, normalize = True):
    """
    

    Parameters
    ----------
    l_simulated_matrices : list 
        list of simulated matrices from 'simualte matrices'
        

    Returns
    -------
    df_CI_eigenvector_centrality : dataframe
        mean, CI per eigenvector centrality.

    """
    
    l_eigenvec_results = []
    for df_matrix in l_simulated_matrices:
        
        if normalize:
            df_matrix = normalize_matrix_rows(df_matrix)
            
        eigenvec_centrality = calc_eigenvec_centrality_sectors(df_matrix, type_centrality)
        l_eigenvec_results.append(eigenvec_centrality)
    
    df_eigenvec_results = pd.DataFrame(l_eigenvec_results).transpose()
    
    avg = df_eigenvec_results.mean(axis=1)
    std = df_eigenvec_results.std(axis=1)
    lower_CI = avg - (std*1.96)
    upper_CI = avg + (std*1.96)
    
    lower_CI = lower_CI.apply(lambda x: x if x>0 else 0)
    
    df_CI_eigenvector_centrality = pd.concat([avg, lower_CI, upper_CI], axis=1)
    df_CI_eigenvector_centrality.columns = ['avg', 'lower_CI', 'upper_CI']
    
    
    return df_CI_eigenvector_centrality
            

  
    
    
    
