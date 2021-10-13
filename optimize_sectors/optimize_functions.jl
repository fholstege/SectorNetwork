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
function calc_eigenvec_centrality(A, type_centrality)

    if type_centrality == "left"
        A = transpose(A)
    end

    K = size(A, 1)
    k = 1
    eigen_result = eigen(A)
    eigenvectors = eigen_result.vectors[:,K-k+1:K]

    return convert(Vector{Float64}, vec(broadcast(abs, eigenvectors))) 
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
        if length(x) != (78+77)
            println("x dimension incorrect")
        end
        A[bank_idx,:] = x[1:78]
        A[1:end .!= bank_idx, bank_idx] = x[79:end]
    elseif opt == "inputs"
        if length(x) != 78
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

function naive_objective(x, bank_idx, bank_rank, vs_old, A,  normalize, list_obj_values, iterator, λb = 0.2, use_abs_diff = false)
     
    global iterator += 1

    # 2 function evaluations per step
    step_iterator = iterator / 2
    
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
 


function naive_objective_w_budget(x, bank_idx, bank_rank, vs_old, A, budget, normalize,  list_obj_values, list_constraint_values, iterator, vs_initial, x_initial, λb = 0.2, use_abs_diff = false)

    # enforce non-negative values
    x[x .< 0] .= 0

    # update global iterator
    global iterator += 1

    # 2 function evaluations per step
    step_iterator = iterator / 2

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
    # obj = (1-λb) * (1e5 * max(-0.000001, eigenvec_diff))
    # budget_constraint = λb * max(0, sum(x) - budget)^2


    obj = (1e6 * max(-0.001, eigenvec_diff))
    budget_constraint = max(0, sum(x) - budget)^2

    push!(list_obj_values, obj)
    push!(list_constraint_values, budget_constraint) 
    

    # hand over parameters
    for i in 1:length(vs_old)
        vs_old[i] = vs_new[i]
    end

    # optimize one or the other based on steps
    # if step_iterator <= 100.0
    #     fitness = obj
    # else
    #     # reset iterator after 200 steps
    #     if step_iterator == 500.0
    #         println("iterator reset, step $step_iterator")
    #         global iterator = 0
    #     end
    #     fitness = budget_constraint
    # end    

    fitness = obj +  log(step_iterator) * budget_constraint

    return fitness
end


function naive_objective_w_penalty(x, bank_idx, bank_rank, vs_old, A, budget, normalize, list_obj_values, list_constraint_values, iterator, vs_initial, x_initial, λb = 0.2, use_abs_diff = false)

    # enforce non-negative values
    x[x .< 0] .= 0

    # update global iterator
    global iterator += 1

    # 2 function evaluations per step
    step_iterator = iterator / 2

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
    # obj = (1-λb) * (1e5 * max(-0.000001, eigenvec_diff))
    # budget_constraint = λb * max(0, sum(x) - budget)^2


    obj = (1e8 * max(-0.000001, eigenvec_diff))
    budget_constraint = max(0, sum(x) - budget)^2
    
    # try to ensure other eigenvec centralities do not vary much
    # penalty_v = 1 / length(vs_new[1:end .!= bank_idx]) * sum((1e3 .* (vs_new[1:end .!= bank_idx] .- vs_initial[1:end .!= bank_idx])) .^2)
    # penalty_v = 1e4 * norm(((vs_new[1:end .!= bank_idx] .- vs_initial[1:end .!= bank_idx])), 1)



    penalty_v = 1e5 * sum((vs_new[1:end .!= bank_idx] .- vs_initial[1:end .!= bank_idx]) .^2)

    # ensure xs do not change too much from original A
    # penalty_x = max(0, sum(x .- x_initial))^2
    penalty_x = norm(x .- x_initial)^2
    # helps to have sth that changes with each step to indicate
    # SPSA in which direction to go


    push!(list_obj_values, obj)
    push!(list_constraint_values, budget_constraint) 
    

    # hand over parameters
    for i in 1:length(vs_old)
        vs_old[i] = vs_new[i]
    end

    # # optimize one or the other based on steps
    # if step_iterator <= 10000.0
    #     fitness = obj
    # else
    #     # reset iterator after 200 steps
    #     if step_iterator == 500.0
    #         println("iterator reset, step $step_iterator")
    #         global iterator = 0
    #     end
    #     fitness = budget_constraint
    # end    

    # if step_iterator > 20000.0
    #     penalty_x = penalty_x * norm(x)
    # end


    fitness = obj +  log(step_iterator) * budget_constraint + penalty_x


    # println("obj = $obj")
    # println("budget = $(budget_constraint)")
    # # println("penalty_v = $penalty_v")
    # println("penalty_x = $penalty_x")
    # println("log(step) = $(log(step_iterator))")
    # println("step iterator: $step_iterator")
    # println(log(step_iterator) * (budget_constraint  + penalty_v + penalty_x + sum(x)))

    return fitness
end





# repeat the SPSA n_runs times 
function repeated_spsa(n_runs, objective_func, bank_idx, bank_rank, vs_old, A, budget, normalize, iterator, vs_initial, x_initial, λb = 0.2, use_abs_diff = false,
    SearchRange = (0.0, 25000.0), 
    NumDimensions=78, 
    MaxSteps = 200000)

    results = Array{Any}(undef, NumDimensions, n_runs)
    fill!(results,NaN)

    ranks = []

    for i = 1:n_runs

        println("run $i")

        list_obj_values = []
        list_constraint_values = []

        global iterator = 0

        result = bboptimize( x -> objective_func(x, bank_idx, bank_rank, vs_old, A, budget, normalize, list_obj_values, list_constraint_values, iterator, vs_initial, x_initial, λb, use_abs_diff);
                x0 = x_initial,
                SearchRange = SearchRange,
                NumDimensions = NumDimensions,
                MaxSteps = MaxSteps,
                Method = :simultaneous_perturbation_stochastic_approximation,
                NThreads = Threads.nthreads() - 1);

        result_param = best_candidate(result)
        results[:,i] = result_param .- x_initial

        # get new A, new eigenvec centralities 
        A_result = construct_A(copy(A), result_param, opt = "inputs");
        vs_result = calc_eigenvec_centrality(normalize_rows_matrix(A_result), "right");

        # What is the new rank of banking? 
        bank_rank_new = get_bank_rank(vs_result, bank_idx);

        push!(ranks, bank_rank_new);
    end

    return results, ranks
end


