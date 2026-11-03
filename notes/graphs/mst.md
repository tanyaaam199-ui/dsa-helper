# Minimum Spanning Tree (MST)

## What it is
A minimum spanning tree of a connected, weighted, undirected graph is a subset of edges that connects all vertices with no cycles and the smallest possible total weight. It always has V-1 edges. If the graph is disconnected, no spanning tree exists.

## When to use
Connecting all nodes at minimum total cost: networks, roads, cables, pipelines, clustering. Keywords: "connect all", "minimum cost to connect", "spanning".

## Kruskal's algorithm
Sort all edges by weight. Go through them in order and add an edge if it does not form a cycle, checked with Union-Find. Stop after V-1 edges. Time O(E log E). Works well for sparse graphs.

## Prim's algorithm
Start from any node. Repeatedly add the cheapest edge that connects the current tree to a new vertex, using a min-heap. Time O(E log V). Works well for dense graphs.

## Python code (Kruskal)
    def kruskal(n, edges):   # edges = (weight, u, v), uses the DSU class
        dsu = DSU(n)
        total, used = 0, 0
        for w, u, v in sorted(edges):
            if dsu.union(u, v):
                total += w
                used += 1
        return total if used == n - 1 else -1   # -1 means graph is disconnected

## Common problems
Min Cost to Connect All Points, Connecting Cities With Minimum Cost, Optimize Water Distribution in a Village, Find Critical and Pseudo-Critical Edges in MST.
