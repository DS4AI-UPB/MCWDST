import networkx as nx
import pickle
import json
import os

from os import listdir
from os.path import isfile, join
from networkx.utils import open_file

user_list_property = 'UniqueUsers'
user_count_property = 'UniqueUsersCount'

number_of_nodes = 2789474.0
active_factor = 0.5
active_multiplier = active_factor * (1 / (number_of_nodes))

def get_files(data_folder):
    only_files = [f for f in listdir(data_folder) if isfile(join(data_folder, f))]

    print(only_files[:3])

    return only_files

def parse_file(file_name, data_folder, G):
    with open(data_folder + '/' + file_name, 'r') as json_file:
        data = json.load(json_file)
        
        user_list = data[user_list_property]
        initial_user = int(file_name.replace('dump', '').replace('.json', ''))
        user_count = int(data[user_count_property]) + 0.0
        edge_w = active_multiplier * user_count

        for user_id in user_list:
            G.add_edge(initial_user, user_id, weight = edge_w )

def generate_graph_from_files(data_folder, graph_dump_path):
    G = nx.DiGraph()
    only_files = get_files(data_folder)

    for file_name in only_files:
        parse_file(file_name, data_folder, G)

    save_graph_to_file(G, graph_dump_path)

    print(len(list(G.nodes)))
    print(len(list(G.edges)))

    return G

def load_graph_from_file(graph_dump_path):
    G_loaded = None

    with open(graph_dump_path, 'rb') as f:
        G_loaded = pickle.load(f)

    return G_loaded

def save_graph_to_file(G, save_path):
    with open(save_path, "wb") as output_file:
        pickle.dump(G, output_file, protocol=pickle.HIGHEST_PROTOCOL)

def get_nodes_by_degree(G):
    degrees = {}

    for (node, degree) in G.degree():
        if degree in degrees:
            degrees[degree].append(node)
        else:
            degrees[degree] = [node]

    return degrees

def save_graph_named_by_size(G, graph_dump_path, explicit_name = None):
    file_name = graph_dump_path.split('\\')[-1]
    save_path = graph_dump_path.replace(file_name, '')

    if (explicit_name == None):
        num_nodes = len(list(G.nodes))
        num_edges = len(list(G.edges))
        save_path += "[" + str(num_nodes) + "][" + str(num_edges) + "]" + file_name
    
    else:
        save_path = explicit_name
    
    save_graph_to_file(G, save_path)

def get_stats_for_nodes(G):
    degrees = get_nodes_by_degree(G)
    degree_values = list(degrees.keys())
    max_degree = max(degree_values) + 0.0
    min_degree = min(degree_values) + 0.0
    avg_degree = (sum(degree_values)  + 0.0)/(len(degree_values) + 0.0)

    return (degrees, max_degree, min_degree, avg_degree)

def analyze_graph(degrees, max_degree, min_degree, avg_degree, high_ration, low_ratio, avg_ratio, above_avg_ratio):
    high_degree_count = sum([len(nodes) if (degree > high_ration * max_degree) else 0 for (degree, nodes) in degrees.items()])
    low_degree_count = sum([len(nodes) if (degree < low_ratio * min_degree) else 0 for (degree, nodes) in degrees.items()])
    avg_degree_count = sum([len(nodes) if (abs(avg_degree - degree) / avg_degree < avg_ratio) else 0 for (degree, nodes) in degrees.items()])
    nodes_above_avg_degree_count = sum([len(nodes) if (degree > above_avg_ratio * avg_degree) else 0 for (degree, nodes) in degrees.items()])

    return (high_degree_count, low_degree_count, avg_degree_count, nodes_above_avg_degree_count)

def print_stats(high_degree_count, low_degree_count, avg_degree_count, nodes_above_avg_degree_count, high_ration, low_ratio, avg_ratio, above_avg_ratio, max_degree, min_degree, avg_degree, G):
    print(high_degree_count, "nodes having the degree at least ",high_ration, " of the maximum degree which is", max_degree)
    print(low_degree_count, "nodes having the degree at most ", low_ratio," of the minimum degree which is", min_degree)
    print(avg_degree_count, "nodes having the degree at around ", avg_ratio, " of the avg degree which is", avg_degree)
    print(nodes_above_avg_degree_count, "nodes having the degree at least", above_avg_ratio, " of the avg degree which is", above_avg_ratio * avg_degree)
    print(len(G.nodes), "nodes in total")