# -*- coding: utf-8 -*-
"""
Created on Tue Sep 28 11:56:08 2021

@author: flori
"""
import numpy as np


def est_G(Theta, Y, c):
    """
    

    Parameters
    ----------
    Theta : list
        set of parameters.
    Y : function
        the objective function .
    c : float
        distance for the spsa estimator.

    Returns
    -------
    est_G : numpy array
        estimated gradient.

    """
    
    dimensions = len(Theta)
    Delta = np.random.choice([-1,1], size = dimensions)
    
    est_G = np.array([ (Y(Theta + c*Delta) - Y(Theta -  c*Delta)) / (2*c*Delta[i]) for i in range(dimensions) ])
    return est_G


def SPSA_estimator(K, Theta_start, a, r, Y):
    """
    

    Parameters
    ----------
    K : integer
        number of iterations for the SPSA estimator.
    Theta_start : list
        starting values of theta.
    a : float
        determines the epsilon for SPSA .
    r : float
        determines the steps taken when G is estimated.

    Returns
    -------
    Theta : numpy array of lists
        all the tried values of theta .

    """
    
    # get dimensions in theta
    dimension_Theta = len(Theta_start)
    
    # stores the trajectory of theta
    Theta = np.zeros((K,dimension_Theta)) 
    
    # set starting value of theta
    Theta[0] = Theta_start
    
    epsilon = lambda k: a / (1+k)
    c = lambda k: 1/(1+k)**r
    
    for k in range(K-1):
        G = est_G(Theta[k],Y, c(k))
        Theta[k+1] = Theta[k] + epsilon(k) * (-G)
        
    return Theta 

    


