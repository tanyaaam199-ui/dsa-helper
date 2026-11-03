=== graphs/graph_representation.md ===
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

=== graphs/bfs.md ===
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

=== graphs/dfs.md ===
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

=== graphs/topological_sort.md ===
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

=== graphs/dijkstra.md ===
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

=== graphs/bellman_ford.md ===
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

=== graphs/union_find.md ===
# Union-Find (Disjoint Set Union)

## What it is
Union-Find tracks which elements belong to the same group. find(x) returns the group leader of x, union(a, b) merges two groups. With path compression and union by rank, each operation is almost O(1) (amortized inverse Ackermann).

## When to use
Connected components in an undirected graph, detecting a cycle in an undirected graph, Kruskal's MST, grouping equivalent items, dynamic connectivity where edges are added over time. Keywords: "connected", "same group", "merge", "redundant".

## Python code
    class DSU:
        def __init__(self, n):
            self.parent = list(range(n))
            self.rank = [0] * n
        def find(self, x):
            if self.parent[x] != x:
                self.parent[x] = self.find(self.parent[x])   # path compression
            return self.parent[x]
        def union(self, a, b):
            ra, rb = self.find(a), self.find(b)
            if ra == rb:
                return False       # already connected, edge would form a cycle
            if self.rank[ra] < self.rank[rb]:
                ra, rb = rb, ra
            self.parent[rb] = ra
            if self.rank[ra] == self.rank[rb]:
                self.rank[ra] += 1
            return True

## Common problems
Number of Provinces, Redundant Connection, Accounts Merge, Number of Connected Components in an Undirected Graph, Graph Valid Tree, Min Cost to Connect All Points.

=== graphs/mst.md ===
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

=== graphs/cycle_detection.md ===
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