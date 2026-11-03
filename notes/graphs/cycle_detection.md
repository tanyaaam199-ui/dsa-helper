# Cycle Detection in Graphs

## What it is
A cycle is a path that starts and ends at the same node. The method depends on whether the graph is directed or undirected.

## Undirected graph
Use DFS and track the parent: if you reach a visited node that is not the parent of the current node, there is a cycle. Union-Find also works: if union(u, v) finds both already in the same group, that edge creates a cycle.

## Directed graph
Use DFS with three states: 0 = unvisited, 1 = in the current recursion path, 2 = finished. If DFS reaches a node with state 1, there is a cycle. Alternatively, run Kahn's topological sort: if fewer than V nodes are output, there is a cycle.

## Python code (directed, DFS colors)
    def has_cycle(graph, n):
        state = [0] * n
        def dfs(u):
            state[u] = 1
            for v in graph[u]:
                if state[v] == 1:
                    return True
                if state[v] == 0 and dfs(v):
                    return True
            state[u] = 2
            return False
        return any(state[i] == 0 and dfs(i) for i in range(n))

## Common problems
Course Schedule (directed cycle means impossible), Redundant Connection (undirected), Graph Valid Tree, Find Eventual Safe States.
