# Breadth-First Search (BFS)

## What it is
BFS explores a graph level by level using a queue. It visits all nodes at distance 1, then distance 2, and so on. Time O(V + E), space O(V).

## When to use
Shortest path in an unweighted graph or grid, minimum number of steps or moves, level order traversal, multi-source spreading problems (rotting oranges, walls and gates). Keywords: "minimum steps", "shortest", "nearest".

## Python code
    from collections import deque
    def bfs(graph, start):
        visited = {start}
        dist = {start: 0}
        queue = deque([start])
        while queue:
            node = queue.popleft()
            for nei in graph[node]:
                if nei not in visited:
                    visited.add(nei)
                    dist[nei] = dist[node] + 1
                    queue.append(nei)
        return dist

## Tips
Mark a node visited when you push it into the queue, not when you pop it, otherwise nodes get added many times. For multi-source BFS, push all sources into the queue at the start.

## Common problems
Number of Islands, Rotting Oranges, Shortest Path in Binary Matrix, Word Ladder, Open the Lock, 01 Matrix.
