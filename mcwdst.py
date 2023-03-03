# coding: utf-8

__author__      = "Ciprian-Octavian Truică, Elena-Simona Apostol"
__copyright__   = "Copyright 2021, University Politehnica of Bucharest"
__license__     = "GNU GPL"
__version__     = "0.1"
__email__       = "{ciprian.truica,elena.apostol}@upb.ro"
__status__      = "Development"


import networkx as nx
import matplotlib.pyplot as plt
import tree_mitigator
from networkx.generators.random_graphs import gnm_random_graph
import random as rnd
import time
from SparseShield_NIvsHS.Scripts.DomSolver import DomSolver
from SparseShield_NIvsHS.Scripts.SparseShieldSolver import SparseShieldSolver
from SparseShield_NIvsHS.Scripts.NetShieldSolver import NetShieldSolver

def cost(E, ns, ne):
    ct = 0
    Ec = E
    start_node = ns 
    while start_node != ne:
        for e in E:
            u, v, c = e
            if start_node == v:
                ct += c
                start_node = u
                break
    # print("total cost", ns, ne, ct)
    return ct

def mcdsta(E, r):
    Vt = [r]
    Et = []
    Vc = [r] # current nodes
    # current edges
    Ec = []
    for e in E:
        u, v, c = e
        if v != r:
            Ec.append(e)
    while Vc:
        Vn = [] # new nodes to be added to Vt
        En = [] # new edges to be added to Et

        for n in Vc:
            for e in Ec:
                u, v, c = e
                if n == u and v not in Vt:
                    Et.append(e)
                    Vt.append(v)
                    Vn.append(v)
                    En.append(e)
                if n == u and v in Vt:
                    Cru = cost(Et, u, r)
                    Crv = cost(Et, v, r)
                    if Crv >= Cru + c:
                        # find the existing edge that holds 
                        for ee in Et:
                            if v == ee[1]:
                                x = ee
                        Et.remove(x)
                        Et.append(e)
                        En.append(e)
        Vc = Vn
        for e in En:
            if e in Ec:
                Ec.remove(e)

    # print(Vc)
    # print(Ec)
    # print(Et)
    return Et


if __name__ == "__main__":
    for en_pair in [(978, 10217), (5210, 49124), (10210, 89124), ]:
        G = gnm_random_graph(en_pair[0], en_pair[1], seed=None, directed=True)
        E = []
        for e in G.edges:
            E.append((e[0], e[1], rnd.randint(1,100)))
            # E.append((e[0], e[1], 1))
        G.add_weighted_edges_from(E)


        seeds = rnd.sample(list(G.nodes), int(en_pair[0]*0.1))

        start_time = time.time()
        Et = mcdsta(E, 0)
        end_time = time.time()

        print('Time tree construct', (end_time-start_time))

        start_time = time.time()
        (nd, td, root) = tree_mitigator.build_tree_dataset2(Et)

        node_top = []

        node_scores = {i: 0 for i in td}

        for n in node_scores:
            node_scores[n] = tree_mitigator.compute_score_per_node(n, root, nd, td)

        node_scores_sorted = sorted(node_scores.items(), key=lambda item: item[1], reverse=True)
        end_time = time.time()
        print('Time mitigation', (end_time-start_time))      
        print([k for k in node_scores][:10])
        print(len(node_scores))
        print('====================================')

        start_time = time.time()
        solver = SparseShieldSolver(G, seeds, k=len(seeds))
        nodes = solver.sparse_shield()
        end_time = time.time()
        

        print('SparseShield', (end_time-start_time))
        print('SparseShield Nodes')
        print(len(nodes))
        print('====================================')

        start_time = time.time()
        solver = NetShieldSolver(G, seeds, k=len(seeds))
        nodes = solver.net_shield()
        end_time = time.time()
        

        print('NetShield', (end_time-start_time))
        print('NetShield Nodes')
        print(len(nodes))
        print('====================================')
