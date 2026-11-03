# Heap and Priority Queue

## What it is
A heap is a tree-based structure that always gives you the smallest (min-heap) or largest (max-heap) element quickly. Push and pop take O(log n), peeking at the top is O(1), and building a heap from a list with heapify is O(n). Python's heapq module is a min-heap. For a max-heap, push negative values.

## When to use
Top K elements, K-th largest or smallest, merging K sorted lists, scheduling the next task, repeatedly taking the min or max, running median (two heaps), Dijkstra's algorithm. Keywords: "top k", "k-th largest", "most frequent", "smallest k".

## Python code
    import heapq

    # k-th largest: keep a min-heap of size k
    def kth_largest(nums, k):
        heap = nums[:k]
        heapq.heapify(heap)
        for x in nums[k:]:
            if x > heap[0]:
                heapq.heapreplace(heap, x)   # pop smallest, push x
        return heap[0]                       # O(n log k)

    # max-heap using negatives
    max_heap = []
    heapq.heappush(max_heap, -5)
    largest = -heapq.heappop(max_heap)

## Tips
To get the top K largest, keep a MIN-heap of size K: the smallest of the K sits on top and gets replaced when something bigger arrives. For a running median, keep a max-heap for the lower half and a min-heap for the upper half, and keep their sizes within one of each other.

## Common problems
Kth Largest Element in an Array, Top K Frequent Elements, Merge K Sorted Lists, Find Median from Data Stream, Task Scheduler, K Closest Points to Origin, Last Stone Weight.
