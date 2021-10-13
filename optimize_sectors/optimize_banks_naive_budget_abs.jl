using CSV
using Plots


# load in general functions for optimizing
include("optimize_functions.jl")

## load data
data_path = joinpath(dirname(@__DIR__), "Data", "Matrices", "2016_nominal_clean.csv")
df = CSV.read(data_path, DataFrame)
@select!(df, $(Not("Column1")))

# save column / row names in order
col_names = names(df)

# get column and row index of banking
const bank_idx = findall(col_names .== "Banking")[1]

# init parameters and objects
previous_total_x = sum(df[bank_idx, :]);






# now with normalize = True; A = unnormalized, vs_old = from normalized matrix
A, vs_old, bank_rank, budget = initialize_objects(df, previous_total_x, bank_idx,true,"right");




# define the initial vector to start with
x_0 = A[bank_idx, :]

# save vs_old for evaluation of results
vs_original = deepcopy(vs_old);

# put the constraints in place
constraint = (0.0,5000.0)

# save the results
list_obj_values = []
list_constraint_values = []

steps = 10
λb = 0.5

# get result of naive objective with budget
res_naive = bboptimize(x -> naive_objective_w_budget(x, bank_idx, bank_rank, vs_old, A, budget, true,  list_obj_values,list_constraint_values ,λb, true ); 
                x0 = x_0,
                SearchRange = constraint,
                NumDimensions = 80,
                MaxSteps = steps,
                Method = :simultaneous_perturbation_stochastic_approximation,NThreads=Threads.nthreads()-2);

# plot the objective and constraint
x = 1:length(list_obj_values)
objective_score = list_obj_values
constraint_score = list_constraint_values

plot(x, objective_score)
plot(x, constraint_score)


#### Check the following:


 # 1 ) Is the budget constraint fulfilled?
 check_budget_constraint(res_naive, budget)


 # 2) what are the ranked eigenvec centralities?

 
# get new A, new eigenvec centralities 
A_result = construct_A(copy(A), best_candidate(res_naive), opt = "inputs");
vs_result = calc_eigenvec_centrality(normalize_rows_matrix(A_result), "right");

# get original eigenvec centralities and names
vs_original_names = hcat(col_names, vs_original)
vs_result_names = hcat(col_names, vs_result)

# show the K results around banking 
K_up = 2
K_low = 2

# what is the eigenvec centrality of banking?
vs_result_names[bank_idx, :]

# What is the new rank of banking? 
bank_rank_new = get_bank_rank(vs_result, bank_idx);

# the sectors ones around banking 
top_around_banking_original = [vs_original_names[get_sector_ranked_nth(vs_original, i),1:2] for i in bank_rank-K_up:bank_rank+K_low]
top_around_banking_new = [vs_result_names[get_sector_ranked_nth(vs_result, i),1:2] for i in bank_rank_new-K_up:bank_rank_new+K_low]
