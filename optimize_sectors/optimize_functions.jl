using DataFrames
using DataFramesMeta
using LinearAlgebra
using LightGraphs
using BlackBoxOptim
using Statistics

# normalizes the rows of a matrix
function normalize_rows_matrix(A)
    rowSums = sum(A, dims=2)
    normalized_matrix = A ./rowSums
    replace!(normalized_matrix, NaN=>0)
    return normalized_matrix
end

# calculate the eigenvector centrality of a directed graph
function calc_eigenvec_centrality(A, type_centrality, normalize)

    if type_centrality == "left"
        A = transpose(A)
    end

    K = size(A, 1)
    k = 1
    eigen_result = eigen(A)
    eigenvectors = eigen_result.vectors[:,K-k+1:K]

    return convert(Vector{Float64}, vec(eigenvectors)) 
end

# get the distance to the max vector
function get_distance_to_max_v(vs)
    max_v = maximum(vs)
    return max_v .- vs
end

# get the sector ranked n 
function get_sector_ranked_nth(vs, n)
    return sortperm(vs, rev=true)[n]
end

# construct the A matrix
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

function naive_objective(x, bank_idx, bank_rank, vs_old, A,  normalize, list_obj_values, λb = 0.2, use_abs_diff = false)
     # construct A based on xs
     A_new = construct_A(deepcopy(A), x; opt = "inputs")

     if normalize
         A_new = normalize_rows_matrix(A_new)
     end 
     # get new eigenvector centralities
     vs_new = calc_eigenvec_centrality(A_new, "right") 
 
     # get eigenvector centrality of the sector in next rank
     v_next_rank = get_v_of_next_rank(vs_new, bank_rank)

     # eigenvec difference
    eigenvec_diff = v_next_rank - vs_new[bank_idx]

    if use_abs_diff
        eigenvec_diff = abs(eigenvec_diff)
    end 
 
     # define objective function
     obj = (1-λb) * (1e4 * max(0, (eigenvec_diff)))
 
     # save score objective function
     push!(list_obj_values, obj)     
 
     # hand over parameters
     for i in 1:length(vs_old)
         vs_old[i] = vs_new[i]
     end
 
     return obj 
 end
 


function naive_objective_w_budget(x, bank_idx, bank_rank, vs_old, A, budget, normalize,  list_obj_values, list_constraint_values, λb = 0.2, use_abs_diff = false)

    # construct A based on xs
    A_new = construct_A(deepcopy(A), x; opt = "inputs")

    if normalize
        A_new = normalize_rows_matrix(A_new)
    end 
    # get new eigenvector centralities
    vs_new = calc_eigenvec_centrality(A_new, "right") 

    # get eigenvector centrality of the sector in next rank
    v_next_rank = get_v_of_next_rank(vs_new, bank_rank)

    # eigenvec difference
    eigenvec_diff = v_next_rank - vs_new[bank_idx]

    if use_abs_diff
        eigenvec_diff = abs(eigenvec_diff)
    end 

    # define objective function
    obj = (1-λb) * (1e4 * max(0, eigenvec_diff))
    budget_constraint = λb * max(0, sum(x) - budget)^2

    push!(list_obj_values, obj)
    push!(list_constraint_values, budget_constraint) 
    

    # hand over parameters
    for i in 1:length(vs_old)
        vs_old[i] = vs_new[i]
    end

    return obj + budget_constraint
end



# repeat the SPSA n_runs times 
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

