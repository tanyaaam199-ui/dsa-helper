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
