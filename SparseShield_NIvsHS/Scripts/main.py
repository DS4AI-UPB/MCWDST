from DomSolver import DomSolver
from networkx.generators.random_graphs import gnm_random_graph
import random as rnd
import time

if __name__ == "__main__":   
    en_pair = (978, 10217)
    G = gnm_random_graph(en_pair[0], en_pair[1], seed=None, directed=True)
    E = []
    for e in G.edges:
        E.append((e[0], e[1], rnd.randint(1,1)))
    G.add_weighted_edges_from(E)

    solver = DomSolver(G, [0], 10)
    solver.run()
    # print(solver.get_rank())
    print(solver.get_best_nodes(10))