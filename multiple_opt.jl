using CSV
using DataFrames
using DataFramesMeta
using LinearAlgebra
using LightGraphs
using BlackBoxOptim
using Statistics

# in 2019, banking is ranked 1
# question to answer: what to do to make banking increase one rank

## load data
data_path = joinpath(@__DIR__, "Data", "Matrices", "2016_nominal.csv")
df = CSV.read(data_path, DataFrame)
@select!(df, $(Not("Column1")))



# save column / row names in order
col_names = names(df)

# get column and row index of banking
const bank_idx = findall(col_names .== "Banking")[1]

## define helper functions

function normalize_rows_matrix(A)
    rowSums = sum(A, dims=2)
    normalized_matrix = A ./rowSums
    replace!(normalized_matrix, NaN=>0)
    return normalized_matrix
end

function normalize_rows_df(df)
    rowSums = sum.(eachrow(df))
    normalized_df = df ./rowSums

    replace_nan!(v::AbstractVector) = map!(x -> isnan(x) ? zero(x) : x, v, v)

    df_normalized_noNaN = ifelse.(isnan.(normalized_df), 0, normalized_df)
    return df_normalized_noNaN
end


function calc_eigenvec_centrality(A, type_centrality)

    if type_centrality == "left"
        A = transpose(A)
    end
    K = size(A, 1)
    k = 1
    eigen_result = eigen(A)
    eigenvectors = eigen_result.vectors[:,K-k+1:K]

    return convert(Vector{Float64}, vec(eigenvectors)) 
end

        
function get_distance_to_max_v(vs)
    max_v = maximum(vs)
    return max_v .- vs
end

function get_sector_ranked_nth(vs, n)
    return sortperm(vs, rev=true)[n]
end

function construct_A(A, x; opt = "all")
    if opt == "all"
        if length(x) != (80+79)
            println("x dimension incorrect")
        end
        A[bank_idx,:] = x[1:80]
        A[1:end .!= bank_idx, bank_idx] = x[81:end]
    elseif opt == "inputs"
        if length(x) != 80
            println("x dimension incorrect")
        end
        A[bank_idx,:] = x
    end
    return A
end

# find sector idx ranked one higher than banking
function find_next_rank_idx(vs)
    for i in 1:length(vs)
        rank_idx = get_sector_ranked_nth(vs, i)
        if rank_idx == bank_idx
            return get_sector_ranked_nth(vs, i-1)
        end
    end
end

# function to initialize all objects for optimization
function initialize_objects(df, budget, bank_idx, normalize = true)
    A = Matrix(df);

    if normalize
        A_norm = normalize_rows_matrix(A)
        vs_old = calc_eigenvec_centrality(A_norm, "right"); 
    else 
        vs_old = calc_eigenvec_centrality(A, "right")
    end
    
    bank_rank = get_bank_rank(vs_old, bank_idx);
    println("bank rank = $bank_rank")
    
    return A, vs_old, bank_rank, budget
end

# find rank idx based on banking rank
function get_bank_rank(vs, bank_idx)
    for i in 1:length(vs)
        rank_idx = get_sector_ranked_nth(vs, i)
        if rank_idx == bank_idx
            return i
        end
    end
end

# find vs of the sector ranked above bank_rank
function get_v_of_next_rank(vs, bank_rank)
    return vs[get_sector_ranked_nth(vs, bank_rank-1)]
end

# check if budget constraint hold after having obtained results
function check_budget_constraint(results, budget)

    # compute total costs of proposed solution
    total_costs = sum(best_candidate(results))

    # output
    if total_costs > budget
        println("budget constraint violated\n total costs =  $total_costs\n budget = $budget")
    
    else
        println("budget constraint holds\n total costs =  $total_costs\n budget = $budget")
    end
end

## optimize naive objective function with budget constraint

function naive_objective_w_budget(x, bank_idx, bank_rank, vs_old, A, budget, normalize, λb = 0.2)

    # construct A based on xs
    A_new = construct_A(deepcopy(A), x; opt = "inputs")

    if normalize
        A_new = normalize_rows_matrix(A_new)
    end 
    # get new eigenvector centralities
    vs_new = calc_eigenvec_centrality(A_new, "right") 

    # get eigenvector centrality of the sector in next rank
    v_next_rank = get_v_of_next_rank(vs_new, bank_rank)

    # define objective function
    obj = (1-λb) * (1e4 * max(0, (v_next_rank - vs_new[bank_idx])))
    budget_constraint = λb * max(0, sum(x) - budget)^2

    # hand over parameters
    for i in 1:length(vs_old)
        vs_old[i] = vs_new[i]
    end

    return obj + budget_constraint
end

function repeated_spsa(n_runs, objective_func, bank_idx, bank_rank, vs_old, A, budget, λb,
    SearchRange = (0.0, 5000.0), 
    NumDimensions=80 , 
    MaxSteps = 30000 )

    results = Array{Any}(undef,NumDimensions , n_runs)
    fill!(results,NaN)

    Threads.@threads for i = 1:n_runs
        result = bboptimize( x -> objective_func(x, bank_idx, bank_rank, vs_old, A, budget, λb);
                SearchRange = SearchRange,
                NumDimensions = NumDimensions,
                MaxSteps = MaxSteps,
                Method = :simultaneous_perturbation_stochastic_approximation,NThreads=Threads.nthreads()-2);

        result_param = best_candidate(result)
        results[:,i] = result_param
    end

    return results
end




# init parameters and objects
previous_total_x = sum(df[bank_idx, :]);

# now with normalize = True; A = unnormalized, vs_old = from normalized matrix
A, vs_old, bank_rank, budget = initialize_objects(df, previous_total_x, bank_idx);

# save vs_old for evaluation of results
vs_original = deepcopy(vs_old);

# put the constraints in place
constraint = (0.0,5000.0)
constraints = [constraint for i in 1:80]


# we have to pick year data where banking is not highly ranked
# otherwise problem if banking is already rank 1, or if it has the same eigenvector centrality as rank 1
res_naive = bboptimize(x -> naive_objective_w_budget(x, bank_idx, bank_rank, vs_old, A, budget,true, 0.5); # put lambda_b = 0.5
                SearchRange = constraints,
                NumDimensions = 80,
                MaxSteps = 30000,
                Method = :simultaneous_perturbation_stochastic_approximation,NThreads=Threads.nthreads()-2);

best_candidate(res_naive)

# check results
check_budget_constraint(res_naive, budget)

hcat(best_candidate(res_naive), A[bank_idx,:], col_names)

DataFrame(original = A_normalized[bank_idx,:],
          result = best_candidate(res_naive),
          sector = col_names)


# get top 10 sectors in terms of eigenvector centrality
A_result = construct_A(copy(A_normalized), best_candidate(res_naive), opt = "inputs");
vs_result = calc_eigenvec_centrality(A_result, "right");

vs_original_names[]


vs_original_names = hcat(col_names, vs_original)
vs_result_names = hcat(col_names, vs_result)

top10_original = [get_sector_ranked_nth(vs_original, i) for i in 1:10]
top10_result = [get_sector_ranked_nth(vs_result, i) for i in 1:10]

    

top10_original = [vs_original_names[get_sector_ranked_nth(vs_original, i),1:2] for i in 1:10]
top10_result = [vs_result_names[get_sector_ranked_nth(vs_result, i),1:2] for i in 1:10]

hcat(top10_original, top10_result)






###############

results = repeated_spsa(100,  naive_objective_w_budget, bank_idx, bank_rank, vs_old, A, budget, 0.2)

average_row_values = mean(results, dims= 2)
sd_row_values = std(results, dims = 2)

CI_lower_row_values = average_row_values - (1.96* sd_row_values)
CI_upper_row_values = average_row_values + (1.96* sd_row_values)

hcat(average_row_values,sd_row_values,CI_lower_row_values, CI_upper_row_values  )