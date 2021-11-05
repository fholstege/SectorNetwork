using CSV
using DataFrames
using DataFramesMeta
using LinearAlgebra
using LightGraphs
using BlackBoxOptim

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

function get_eigen_centrality(A)
    return eigenvector_centrality(SimpleDiGraph(A))
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
function initialize_objects(df, budget, bank_idx)
    A = Matrix(df);
    vs_old = get_eigen_centrality(A); 
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

function naive_objective_w_budget(x, bank_idx, bank_rank, vs_old, A, budget, λb = 0.2)

    # construct A based on xs
    A_new = construct_A(deepcopy(A), x; opt = "inputs")

    # get new eigenvector centralities
    vs_new = get_eigen_centrality(A_new) 

    # get eigenvector centrality of the sector in next rank
    v_next_rank = get_v_of_next_rank(vs_new, bank_rank)

    # define objective function
    # obj = (1-λb) * (1e4 * max(0, (v_next_rank - vs_new[bank_idx])))
    # do not take max, because we want bank > next rank not equal!
    # we want the minimal changes, thus the budget constraint
    obj = (1-λb) * 1e4 * (v_next_rank - vs_new[bank_idx])

    budget_constraint = λb * max(0, sum(x) - budget)^2

    # hand over parameters
    for i in 1:length(vs_old)
        vs_old[i] = vs_new[i]
    end

    return obj + budget_constraint
end

# init parameters and objects
previous_total_x = sum(df[bank_idx, :]);

A, vs_old, bank_rank, budget = initialize_objects(df, previous_total_x, bank_idx);

# save vs_old for evaluation of results
vs_original = deepcopy(vs_old);

    # pick year data where banking is not highly ranked
    # otherwise problem if banking is already rank 1


res_naive = bboptimize(x -> naive_objective_w_budget(x, bank_idx, bank_rank, vs_old, A, budget, 0.4);
                SearchRange = (0.0,5000.0),
                NumDimensions = 80,
                MaxSteps = 30000,
                Method = :simultaneous_perturbation_stochastic_approximation,NThreads=Threads.nthreads()-2);

# check results
check_budget_constraint(res_naive, budget)

hcat(best_candidate(res_naive), A[bank_idx,:], col_names)

DataFrame(original = A[bank_idx,:],
          result = best_candidate(res_naive),
          sector = col_names)


# get top 10 sectors in terms of eigenvector centrality
A_result = construct_A(copy(A), best_candidate(res_naive), opt = "inputs");
vs_result = get_eigen_centrality(A_result);

top10_original = [get_sector_ranked_nth(vs_original, i) for i in 1:10]
top10_result = [get_sector_ranked_nth(vs_result, i) for i in 1:10]

hcat(top10_original, top10_result)


top10_original = [vs_original[get_sector_ranked_nth(vs_original, i)] for i in 1:10]
top10_result = [vs_original[get_sector_ranked_nth(vs_result, i)] for i in 1:10]

hcat(top10_original, top10_result)



## optimize naive objective with budget and additional penalties

function penalty_objective(x, bank_idx, bank_rank, vs_old, A, budget, λb = 0.2)

    # retrieve initial xs
    x_init = A[bank_idx, :]

    # construct A based on xs
    A_new = construct_A(copy(A), x; opt = "inputs")

    # get new eigenvector centralities
    vs_new = get_eigen_centrality(A_new) 

    # get eigenvector centrality of the sector in next rank
    v_next_rank = get_v_of_next_rank(vs_new, bank_rank)

    # define objective function
    obj = (1-λb) * (1e4 * max(0, (v_next_rank - vs_new[bank_idx])))^2 
    budget_constraint = λb * max(0, sum(x) - budget)^2

    # try to ensure other eigenvec centralities do not vary much
    penalty_v = sum(vs_new[1:end .!= bank_idx] .- vs_old[1:end .!= bank_idx])
    # penalize X - X_0, to ensure xs do not change too much from original A
    penalty_x = sum(x .- x_init)

    # hand over parameters
    for i in 1:length(vs_old)
        vs_old[i] = vs_new[i]
    end

    return obj + budget_constraint + penalty_v + penalty_x
end

# init parameters and objects
previous_total_x = sum(df[bank_idx, :]);

A, vs_old, bank_rank, budget = initialize_objects(df, previous_total_x, bank_idx);

# save vs_old for evaluation of results
vs_original = deepcopy(vs_old);

res_penalty = bboptimize(x -> penalty_objective(x, bank_idx, bank_rank, vs_old, A, budget, 0.2);
                SearchRange = (0.0,5000.0),
                NumDimensions = 80,
                MaxSteps = 30000,
                Method = :simultaneous_perturbation_stochastic_approximation,NThreads=Threads.nthreads()-2);

# check results
check_budget_constraint(res_penalty, budget)

DataFrame(original = A[bank_idx,:],
          result = best_candidate(res_penalty),
          sector = col_names)



# todos:
# - decide which year to use so that banking does not have the same eigenvector centrality as the rank 1 sector
# - look at repeated_bboptimize to get a distribution 



# can use repeated_bboptimize to run XXXX times the whole simulation and aggregate results -> mean, variance?

# function to assemble new A from found x
function assemble_final_A(A, results, bank_idx, opt_all = true)

    if opt_all
        # replace found row entries for banking
        B[51,:] = best_candidate(res)[1:80]

        # replace found col entries for banking
        # accounting for diagonal entry
        col_replacement = best_candidate(res)[81:end][1:(bank_idx-1)]
        append!(col_replacement, best_candidate(res)[bank_idx])
        append!(col_replacement, best_candidate(res)[81:end][bank_idx:end])
        B[:,51] = col_replacement
    else
        # replace found row entries for banking
        B[51,:] = best_candidate(res)[1:80]

        # CHECK IF COL OR ROW ENTRIES ARE THE INPUTS
    end
    return B
end
