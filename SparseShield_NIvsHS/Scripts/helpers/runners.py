from os import system
from joblib import Parallel, delayed

def run_against_config(results_path, nodes_to_cut, algorithm_name, graph_file, seed_file, just_solve):
    output_name = results_path + "result_" + \
                str(nodes_to_cut) + "_" + algorithm_name + "_" + \
                graph_file.replace('.pkl', '') + ".json"
    script_to_run = "python run_solver.py graphs/" + \
                graph_file + " seeds/" + seed_file + " "
    arguments = str(nodes_to_cut) + " " + \
                algorithm_name + " --outfile " + output_name + \
                " --just_solve " + str(1 if just_solve else 0)
    full_command = script_to_run + arguments

    print(full_command)
    system(full_command)

def run_solver_against_configs(results_path='results/', graph_file='fromData.pkl', seed_file='seed.csv', startNumber=10, endNumber=1000, step=10, algorithms_to_run=['Random', 'Degree', 'SparseShield', 'Dom'], just_solve=True, num_threads = 22):
    configs = list([(nodes_to_cut, algorithm_name) for nodes_to_cut in range(startNumber, endNumber, step) for algorithm_name in algorithms_to_run])

    Parallel(n_jobs=num_threads)(
            delayed(run_against_config)(results_path, nodes_to_cut, algorithm_name, graph_file, seed_file, just_solve) for (nodes_to_cut, algorithm_name) in configs)
            
