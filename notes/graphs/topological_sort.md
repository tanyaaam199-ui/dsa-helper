# Topological Sort

## What it is
A topological ordering of a directed acyclic graph (DAG) lists the nodes so that every edge u -> v has u before v. It exists only if the graph has no cycle. Time O(V + E).

## When to use
Tasks with dependencies, course prerequisites, build order, ordering characters from an alien dictionary. Keywords: "prerequisites", "order", "dependencies". If you cannot produce all nodes, the graph has a cycle.

## Kahn's algorithm (BFS)
Compute the in-degree of every node. Put all nodes with in-degree 0 in a queue. Repeatedly pop a node, add it to the order, and decrease the in-degree of its neighbours, pushing any that reach 0. If the order has fewer than V nodes, there is a cycle.

## Python code
    from collections import deque
    def topo_sort(n, edges):
        graph = [[] for _ in range(n)]
        indeg = [0] * n
        for u, v in edges:
            graph[u].append(v)
            indeg[v] += 1
        queue = deque(i for i in range(n) if indeg[i] == 0)
        order = []
        while queue:
            node = queue.popleft()
            order.append(node)
            for nei in graph[node]:
                indeg[nei] -= 1
                if indeg[nei] == 0:
                    queue.append(nei)
        return order if len(order) == n else []

## Common problems
Course Schedule, Course Schedule II, Alien Dictionary, Parallel Courses, Find All Possible Recipes.
