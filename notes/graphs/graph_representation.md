# Graph Representation

## What it is
A graph is a set of vertices (nodes) connected by edges. Edges can be directed or undirected, weighted or unweighted. The two standard ways to store a graph are an adjacency list and an adjacency matrix.

## When to use
Adjacency list: most problems, especially sparse graphs. Space O(V + E). Adjacency matrix: dense graphs or when you need O(1) edge lookup. Space O(V^2). Edge list: Kruskal's algorithm and Bellman-Ford.

## Python code
    from collections import defaultdict
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)   # remove this line for a directed graph
    # weighted: graph[u].append((v, w))

## Key terms
Degree: number of edges at a node. In-degree and out-degree for directed graphs. Connected graph: every node is reachable from every other. DAG: directed acyclic graph. Tree: connected graph with no cycles and V-1 edges.
