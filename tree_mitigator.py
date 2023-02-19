from copy import deepcopy
from graphviz import Digraph
import os
import statistics

# os.environ["PATH"] += os.pathsep + 'C:\Program Files\Graphviz\\bin'

BAD_CHARS_HUMAN = '() '
BAD_CHARS_DATASET = '[]\','


def get_tree_area(src, dictionary):
    visited = set()

    dfs(src, visited, dictionary)

    return len(visited)


def dfs(src, visited, dictionary):
    visited.add(src)

    if src not in dictionary:
        return
    for n in dictionary[src]:
        if n not in visited:
            dfs(n, visited, dictionary)


def get_max_height(src, dictionary):
    if src not in dictionary:
        return 0
    max_height = -1
    for n in dictionary[src]:
        max_height = max(max_height, get_max_height(n, dictionary))
    return max_height + 1


def compute_score_per_node(src, root, neighbors_dictionary, timestamps_dictionary):
    max_height_root = get_max_height(
        root, neighbors_dictionary)
    max_height_src = get_max_height(
        src, neighbors_dictionary)

    total_area = get_tree_area(
        root, neighbors_dictionary)
    current_area = get_tree_area(src, neighbors_dictionary)

    dict_timestamps_sorted = sorted(
        timestamps_dictionary.items(), key=lambda item: item[1])

    max_timestamp = dict_timestamps_sorted[-1][1]
    min_timestamp = dict_timestamps_sorted[1][1]


    timestamps_dictionary_copy = {}

    for t in timestamps_dictionary:
        try:
            if max_timestamp == min_timestamp:
                timestamps_dictionary_copy[t] = 0.5
            else:
                timestamps_dictionary_copy[t] = 1 - (timestamps_dictionary[t] - min_timestamp) / (max_timestamp - min_timestamp)
        except:
            print(timestamps_dictionary[t], min_timestamp, max_timestamp)


    neighbors_timestamps = [timestamps_dictionary_copy[n]
                            for n in neighbors_dictionary[src]] if src in neighbors_dictionary else [0]

    s1 = float(max_height_src/max_height_root)
    s2 = float(current_area/total_area)
    s3 = float(statistics.median(neighbors_timestamps))
    # print(src, s1, s2, s3)
    return s1+s2+s3

# code for app as we must parse text from the input textbox.
def build_tree_dataset(content):
    neighbors_dict = {}
    timestamps_dict = {}

    lines = content.splitlines()

    first_iter = True
    for line in lines:
        # split by "->"
        pairs = line.split('->')
        # remove "\n"
        pairs[1] = pairs[1][:-1]
        # remove useless chars
        pairs[0] = pairs[0].translate(
            {ord(i): None for i in BAD_CHARS_DATASET})
        pairs[1] = pairs[1].translate(
            {ord(i): None for i in BAD_CHARS_DATASET})
        # split by whitespace
        pairs[0] = pairs[0].split()
        pairs[1] = pairs[1].split()

        if first_iter:
            root = pairs[1][0]
            first_iter = False

        # get values
        id_src = pairs[0][0]
        id_dst = pairs[1][0]
        timestamp = pairs[1][2]

        if id_src not in neighbors_dict:
            neighbors_dict[id_src] = [id_dst]
        else:
            neighbors_dict[id_src].append(id_dst)
        timestamps_dict[id_dst] = float(timestamp)

    return (neighbors_dict, timestamps_dict, root)

# code for testing: no text parsing required, directly build the tree from a graph.
def build_tree_dataset2(E):
    neighbors_dict = {}
    timestamps_dict = {}
    root = -1
    first_iter = True
    for elem in E:
        if first_iter:
            root = elem[0]
            first_iter = False

        # get values
        id_src = elem[0]
        id_dst = elem[1]
        timestamp = elem[2]

        if id_src not in neighbors_dict:
            neighbors_dict[id_src] = [id_dst]
        else:
            neighbors_dict[id_src].append(id_dst)
        timestamps_dict[id_dst] = float(timestamp)

    return (neighbors_dict, timestamps_dict, root)


def build_tree_human(content):
    neighbors_dict = {}
    timestamps_dict = {}

    lines = content.splitlines()

    first_iter = True
    for line in lines:
        # split by "->"
        pairs = line.split('->')
        # remove "\n"
        pairs[1] = pairs[1][:-1] if pairs[1][-1] == '\n' else pairs[1]
        if first_iter:
            root = pairs[0]
            first_iter = False

        # remove useless chars
        pairs[1] = pairs[1].translate({ord(i): None for i in BAD_CHARS_HUMAN})
        pairs_result = pairs[1].split(',')

        # split by whitespace
        pairs[1] = pairs[1].split()

        # get values
        id_src = pairs[0]
        id_dst = pairs_result[0]
        timestamp = pairs_result[1]

        if id_src not in neighbors_dict:
            neighbors_dict[id_src] = [id_dst]
        else:
            neighbors_dict[id_src].append(id_dst)
        timestamps_dict[id_dst] = float(timestamp)
    # print(neighbors_dict, timestamps_dict, root)
    return (neighbors_dict, timestamps_dict, root)


def to_graphviz(content, human, rename):
    graph = Digraph()

    nd, td, root = build_tree_human(
        content) if human else build_tree_dataset(content)

    if human:
        nd['ROOT'] = root
        td[root] = 0

    for node in nd:
        for neigh in nd[node]:
            graph.edge(node, str(neigh), label=str(td[neigh]))

    graph.render(rename, view=False, format='png')

    return (nd, td, root)
