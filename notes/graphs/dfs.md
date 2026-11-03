# Depth-First Search (DFS)

## What it is
DFS goes as deep as possible along one path before backtracking. It uses recursion or an explicit stack. Time O(V + E), space O(V) for the visited set and recursion stack.

## When to use
Exploring all connected components, counting islands, detecting cycles, topological sort, finding paths, backtracking on graphs, checking connectivity. Keywords: "all paths", "connected", "reachable", "components".

## Python code
    def dfs(graph, node, visited):
        visited.add(node)
        for nei in graph[node]:
            if nei not in visited:
                dfs(graph, nei, visited)

    # count connected components
    visited = set()
    count = 0
    for node in graph:
        if node not in visited:
            dfs(graph, node, visited)
            count += 1

## Tips
Deep recursion can hit Python's recursion limit on big inputs, so use an explicit stack if depth can reach thousands. On grids, check bounds and visited before recursing into the 4 neighbours.

## Common problems
Number of Islands, Number of Provinces, Clone Graph, Max Area of Island, Pacific Atlantic Water Flow, All Paths From Source to Target.
