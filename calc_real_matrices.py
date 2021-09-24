# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 16:27:37 2021

@author: flori
"""


from helpfunctions import load_matrix, calc_real_matrices


m2015_nom = load_matrix('Nominal', 2015)
m2016_nom = load_matrix('Nominal', 2016)
m2017_nom = load_matrix('Nominal', 2017)
m2018_nom = load_matrix('Nominal', 2018)
m2019_nom = load_matrix('Nominal', 2019)

m2016_previous_year = load_matrix('Real', 2016)
m2017_previous_year = load_matrix('Real', 2017)
m2018_previous_year = load_matrix('Real', 2018)
m2019_previous_year = load_matrix('Real', 2019)


l_nominal_matrices = [m2015_nom, m2016_nom, m2017_nom, m2018_nom, m2019_nom]
l_previous_year_matrices = [m2016_previous_year, m2017_previous_year, m2018_previous_year, m2019_previous_year]

l_real_matrices = calc_real_matrices(l_nominal_matrices, l_previous_year_matrices)

m2015_real = l_real_matrices[0]
m2016_real = l_real_matrices[1]
m2017_real = l_real_matrices[2]
m2018_real = l_real_matrices[3]
m2019_real = l_real_matrices[4]

m2015_nom.to_csv('Data/Matrices/2015_nominal.csv')
m2016_nom.to_csv('Data/Matrices/2016_nominal.csv')
m2017_nom.to_csv('Data/Matrices/2017_nominal.csv')
m2018_nom.to_csv('Data/Matrices/2018_nominal.csv')
m2019_nom.to_csv('Data/Matrices/2019_nominal.csv')

m2015_real.to_csv('Data/Matrices/2015_real.csv')
m2016_real.to_csv('Data/Matrices/2016_real.csv')
m2017_real.to_csv('Data/Matrices/2017_real.csv')
m2018_real.to_csv('Data/Matrices/2018_real.csv')
m2019_real.to_csv('Data/Matrices/2019_real.csv')




