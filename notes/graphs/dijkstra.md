# Dijkstra's Algorithm

## What it is
Dijkstra finds the shortest path from one source to all other nodes in a graph with non-negative edge weights. It always expands the closest unvisited node using a min-heap. Time O((V + E) log V).

## When to use
Shortest path in a weighted graph where all weights are 0 or positive: road networks, network delay, minimum cost paths. It does NOT work with negative weights, use Bellman-Ford for those. For an unweighted graph, plain BFS is enough.

## Python code
    import heapq
    def dijkstra(graph, src):   # graph[u] = list of (v, w)
        dist = {src: 0}
        heap = [(0, src)]
        while heap:
            d, u = heapq.heappop(heap)
            if d > dist.get(u, float("inf")):
                continue        # stale entry
            for v, w in graph[u]:
                nd = d + w
                if nd < dist.get(v, float("inf")):
                    dist[v] = nd
                    heapq.heappush(heap, (nd, v))
        return dist

## Tips
The check "if d > dist[u]: continue" skips outdated heap entries and is important for speed. Nodes missing from dist are unreachable. For paths, store a parent for each node.

## Common problems
Network Delay Time, Path With Minimum Effort, Cheapest Flights Within K Stops (Bellman-Ford is also used), Swim in Rising Water, Path With Maximum Probability.
