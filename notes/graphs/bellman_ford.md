# Bellman-Ford Algorithm

## What it is
Bellman-Ford finds shortest paths from one source and works with negative edge weights. It relaxes every edge V-1 times. One extra pass that still improves a distance proves a negative cycle exists. Time O(V * E), space O(V).

## When to use
Graphs with negative weights, detecting negative cycles, and problems that limit the number of edges used, such as "at most K stops". Slower than Dijkstra, so use Dijkstra when all weights are non-negative.

## Python code
    def bellman_ford(n, edges, src):   # edges = (u, v, w)
        dist = [float("inf")] * n
        dist[src] = 0
        for _ in range(n - 1):
            for u, v, w in edges:
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                return None        # negative cycle
        return dist

## Tips
For "at most K stops", run only K+1 rounds and use a copy of the previous round's distances when relaxing, so one round adds at most one edge.

## Common problems
Cheapest Flights Within K Stops, Network Delay Time, detecting arbitrage in currency exchange.
