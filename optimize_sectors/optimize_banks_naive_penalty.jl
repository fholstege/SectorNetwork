using CSV
using Plots


# load in general functions for optimizing
include("optimize_functions.jl")

## load data
data_path = joinpath(dirname(@__DIR__), "Data", "Matrices", "2016_nominal_clean_withRental.csv")
df = CSV.read(data_path, DataFrame)
@select!(df, $(Not("Column1")))

# save column / row names in order
col_names = names(df)

# get column and row index of banking
const bank_idx = findall(col_names .== "Banking")[1]

# init parameters and objects
previous_total_x = sum(df[bank_idx, :]);

# now with normalize = True; A = unnormalized, vs_old = from normalized matrix
A, vs_old, bank_rank, budget = initialize_objects(df, previous_total_x, bank_idx);

# define the initial vector to start with
x_0 = A[bank_idx, :]

# save vs_old for evaluation of results
vs_original = deepcopy(vs_old);

# put the constraints in place
constraint = (0.0,25000.0)

# save the results
list_obj_values = []
list_constraint_values = []

steps = 200000
λb = 0.5

iterator = 0

# get result of naive objective with budget
res_naive = bboptimize(x -> naive_objective_w_penalty(x, bank_idx, bank_rank, vs_old, A, budget, true, list_obj_values, list_constraint_values, iterator, vs_original, x_0, λb, false); 
                x0 = x_0,
                SearchRange = constraint,
                NumDimensions = 78,
                MaxSteps = steps,
                Method = :simultaneous_perturbation_stochastic_approximation);


# plot the objective and constraint




x = 1:length(list_obj_values[1:2:end])
objective_score = list_obj_values[1:2:end]

x = x[3000:end]
objective_score = objective_score[3000:end]

plot(x, objective_score)
plot!(xlabel = "Steps")
plot!(ylabel = "Objective Function Value")
plot!(legend = false)


png("objective_func_complete")
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

println("original rank: $bank_rank -- new rank: $bank_rank_new")

# the sectors ones around banking 
top_around_banking_original = [vs_original_names[get_sector_ranked_nth(vs_original, i),1:2] for i in bank_rank-K_up:bank_rank+K_low]
top_around_banking_new = [vs_result_names[get_sector_ranked_nth(vs_result, i),1:2] for i in bank_rank_new-K_up:bank_rank_new+K_low]




        
results, ranks = repeated_spsa(10, naive_objective_w_penalty, 
            bank_idx, bank_rank, vs_old, A, budget, true, iterator, vs_original, x_0, λb , false,
                        (0.0, 25000.0), 
                        78, 200000)

# get confidence bands on Xs

using Latexify

m = vec(mean(results, dims = 2))
s = vec(std(results, dims = 2))


output_df = DataFrame(sector1 = names(df)[1:39], m1 = m[1:39], s1 = s[1:39], 
sector2 = names(df)[40:end], m2 = m[40:end], s2 = s[40:end])
  
                        
latextabular(Array(output_df), latex = false, booktabs = true, fmt = "%.2f")

# summarize ranks

mean(ranks)

std(ranks)


# output of single run
# using Latexify

# h = A_result[bank_idx, :] .- x_0


# output_df = DataFrame(sector1 = names(df)[1:39], x1 = h[1:39],
#                       sector2 = names(df)[40:end], x2 = h[40:end])

# latextabular(Array(output_df), latex = false, booktabs = true, fmt = "%.2f")


