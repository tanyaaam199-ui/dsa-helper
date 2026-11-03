import datetime
import hashlib
import json
import os
import random
from typing import List, Dict, Any, Optional
import httpx
try:
    import ollama
except Exception:
    ollama = None

# Curated high-yield FAANG & tech interview flashcard bank
FLASHCARD_BANK: List[Dict[str, Any]] = [
    # --- Trees & BST ---
    {
        "id": "tree-1",
        "topic": "Trees & BST",
        "difficulty": "Medium",
        "question": "How do you find the Lowest Common Ancestor (LCA) in a BST in O(h) time without extra memory?",
        "answer": "Walk down from the root: if both values are smaller than root.val, go left. If both are larger, go right. The first node where the two values split (one <= root.val <= other) is the LCA!",
        "takeaway": "BST ordering property eliminates searching subtrees entirely."
    },
    {
        "id": "tree-2",
        "topic": "Trees & BST",
        "difficulty": "Easy",
        "question": "What is the common bug when validating whether a binary tree is a valid BST?",
        "answer": "Only checking that a node is greater than its left child and smaller than its right child! This misses values deep in the subtree. You must pass down valid bounds [low, high] or check that in-order traversal is strictly increasing.",
        "takeaway": "Local child checks fail for BSTs. Always validate globally using (low, high) bounds."
    },
    {
        "id": "tree-3",
        "topic": "Trees & BST",
        "difficulty": "Medium",
        "question": "What traversal order reconstructs a BST with unique keys from a single traversal list?",
        "answer": "Pre-order (or Post-order) traversal! Because the first element is the root, and all elements smaller belong to the left subtree while all larger belong to the right subtree.",
        "takeaway": "In-order alone cannot distinguish tree shapes (it's always sorted)."
    },
    {
        "id": "tree-4",
        "topic": "Trees & BST",
        "difficulty": "Hard",
        "question": "How do you calculate the Diameter of a Binary Tree in O(N) time?",
        "answer": "Use post-order DFS. At each node, compute max depth of left and right subtrees. The longest path through the node is left_depth + right_depth. Maintain a global max, and return 1 + max(left_depth, right_depth) to the parent.",
        "takeaway": "Diameter does not necessarily pass through the root node!"
    },

    # --- Heaps & Priority Queues ---
    {
        "id": "heap-1",
        "topic": "Heaps",
        "difficulty": "Medium",
        "question": "What is the time complexity to build a Heap from an arbitrary array of size N using heapify?",
        "answer": "O(N) time! While inserting N elements one by one takes O(N log N), bottom-up heapify (sift-down) converges mathematically to O(N).",
        "takeaway": "Always use heapify() instead of repeated heappush() when starting with an array."
    },
    {
        "id": "heap-2",
        "topic": "Heaps",
        "difficulty": "Medium",
        "question": "To find the K-th LARGEST element in an unsorted stream, what heap should you maintain and why?",
        "answer": "Maintain a MIN-heap of size K! The smallest of the top K sits at the top (root). When a new number arrives, if it's larger than the root, replace root. After the stream, root is the K-th largest.",
        "takeaway": "K-th largest requires a Min-Heap of size K (not a Max-Heap)."
    },
    {
        "id": "heap-3",
        "topic": "Heaps",
        "difficulty": "Hard",
        "question": "How do you find the running median of a data stream in O(log N) insert and O(1) find?",
        "answer": "Use two heaps: a Max-Heap for the smaller half of numbers, and a Min-Heap for the larger half. Keep sizes balanced (max-heap size == min-heap size or +1). The median is either the top of max-heap or the average of both tops.",
        "takeaway": "Two balanced heaps divide any sequence dynamically at its 50th percentile."
    },

    # --- Graphs & Traversals ---
    {
        "id": "graph-1",
        "topic": "Graphs",
        "difficulty": "Medium",
        "question": "When does Dijkstra's Algorithm fail to produce shortest paths?",
        "answer": "When the graph contains negative-weight edges! Dijkstra greedily assumes visiting a node finalizes its shortest path. Use Bellman-Ford (O(V*E)) or SPFA instead.",
        "takeaway": "Dijkstra requires all edge weights to be non-negative (>= 0)."
    },
    {
        "id": "graph-2",
        "topic": "Graphs",
        "difficulty": "Medium",
        "question": "How do you detect a cycle in a DIRECTED graph vs an UNDIRECTED graph?",
        "answer": "In directed graphs: use 3-color DFS (Unvisited, Visiting/In-Stack, Visited). A back-edge to a node currently 'Visiting' indicates a cycle. In undirected graphs: simple DFS with parent pointer, or Disjoint Set Union (Union-Find).",
        "takeaway": "Undirected graphs only need parent checks; directed graphs require cycle detection on the active recursion stack."
    },
    {
        "id": "graph-3",
        "topic": "Graphs",
        "difficulty": "Medium",
        "question": "What is Kahn's Algorithm for Topological Sort, and how does it detect cycles?",
        "answer": "Calculate in-degree for all vertices. Push 0 in-degree nodes into a queue. Repeatedly pop a node, append to output, and decrement neighbors' in-degrees. If output length < total vertices, a cycle exists!",
        "takeaway": "Topological sort only exists for Directed Acyclic Graphs (DAGs)."
    },
    {
        "id": "graph-4",
        "topic": "Graphs",
        "difficulty": "Easy",
        "question": "What is the difference between BFS and DFS space complexity on a tree with branching factor B and depth D?",
        "answer": "BFS space is O(B^D) because the queue stores all leaves at the deepest level. DFS space is O(D) because recursion only stores the current branch. On wide trees, DFS uses exponentially less memory!",
        "takeaway": "BFS consumes high memory on wide graphs; DFS consumes memory proportional to depth."
    },
    {
        "id": "graph-5",
        "topic": "Graphs",
        "difficulty": "Medium",
        "question": "What does Union-Find (Disjoint Set) with Path Compression and Union by Rank achieve asymptotically?",
        "answer": "Nearly O(1) time per operation: O(alpha(N)) where alpha is the Inverse Ackermann function (effectively <= 4 for all realistic N).",
        "takeaway": "Ideal for dynamic connectivity, Kruskal's MST, and grid grouping."
    },

    # --- Arrays & Two Pointers & Sliding Window ---
    {
        "id": "array-1",
        "topic": "Arrays & Pointers",
        "difficulty": "Easy",
        "question": "When is Two Pointers preferred over a Hash Map for the Two Sum problem?",
        "answer": "When the input array is already sorted, or when sorting in-place is allowed and O(1) auxiliary space is required! Two pointers uses O(1) space, while Hash Map uses O(N) space.",
        "takeaway": "Sorted array + pair matching = Two Pointers inward scan in O(1) space."
    },
    {
        "id": "array-2",
        "topic": "Arrays & Pointers",
        "difficulty": "Medium",
        "question": "What is Kadane's Algorithm and what edge case must you be careful with?",
        "answer": "Finds the Maximum Subarray Sum in O(N) time by maintaining curr_max = max(x, curr_max + x). Edge case: all numbers are negative! If you initialize max_so_far to 0, it fails; initialize to nums[0] or -infinity.",
        "takeaway": "Always initialize maximum tracking with nums[0] when negatives are possible."
    },
    {
        "id": "array-3",
        "topic": "Sliding Window",
        "difficulty": "Medium",
        "question": "What is the key template for variable-size Sliding Window problems?",
        "answer": "Expand the right pointer `r` and update window state. Then while window condition is INVALID (e.g. distinct chars > K), shrink left pointer `l` and update state. Then record max length or valid window.",
        "takeaway": "Expand right greedily; shrink left while invalid. Each pointer moves at most N times -> O(N) total."
    },
    {
        "id": "array-4",
        "topic": "Arrays & Pointers",
        "difficulty": "Medium",
        "question": "How does the Dutch National Flag algorithm sort an array of 0s, 1s, and 2s in one pass and O(1) space?",
        "answer": "Use 3 pointers: `low`, `mid`, `high`. If nums[mid] == 0: swap(low, mid), low++, mid++. If nums[mid] == 1: mid++. If nums[mid] == 2: swap(mid, high), high-- (do not increment mid because swapped element needs evaluation).",
        "takeaway": "Three-way partitioning splits elements into < pivot, == pivot, > pivot in O(N)."
    },

    # --- Searching & Binary Search ---
    {
        "id": "search-1",
        "topic": "Binary Search",
        "difficulty": "Medium",
        "question": "In a rotated sorted array with distinct values, how does Binary Search decide which half to search?",
        "answer": "Check which half is normally sorted: if nums[lo] <= nums[mid], the left half is sorted. If target lies in [nums[lo], nums[mid]], search left; otherwise search right. If right is sorted (nums[mid] < nums[hi]), do the symmetrical check.",
        "takeaway": "At least one half of a rotated sorted array is always sorted."
    },
    {
        "id": "search-2",
        "topic": "Binary Search",
        "difficulty": "Medium",
        "question": "What is 'Binary Search on the Answer' and what condition must hold?",
        "answer": "Searching for the optimal numeric value (min capacity, max speed, etc.) rather than an array index. The condition is MONOTONICITY: a boolean check `is_possible(x)` that transitions monotonically (e.g. False, False, ..., True, True).",
        "takeaway": "Whenever a problem asks for 'minimum capacity to...' or 'maximum days such that...', check for binary search on answer."
    },
    {
        "id": "search-3",
        "topic": "Binary Search",
        "difficulty": "Easy",
        "question": "Why write `mid = lo + (hi - lo) // 2` instead of `(lo + hi) // 2`?",
        "answer": "To prevent integer overflow in languages with fixed integer sizes (C++, Java, Go) when lo + hi exceeds 2^31 - 1. While Python handles arbitrary precision integers, `lo + (hi - lo) // 2` is universally safe.",
        "takeaway": "Prevents integer overflow bugs in production systems."
    },

    # --- Linked Lists ---
    {
        "id": "ll-1",
        "topic": "Linked Lists",
        "difficulty": "Medium",
        "question": "How does Floyd's Cycle Detection find the START node of a cycle?",
        "answer": "Phase 1: Move fast by 2, slow by 1 until they meet inside the cycle. Phase 2: Move slow back to head, keep fast at the meeting point. Move BOTH one step at a time. The node where they collide is the cycle entry!",
        "takeaway": "Distance from head to cycle start equals distance from meeting point to cycle start modulo cycle length."
    },
    {
        "id": "ll-2",
        "topic": "Linked Lists",
        "difficulty": "Easy",
        "question": "What is the primary benefit of using a Dummy (Sentinel) Node in Linked List problems?",
        "answer": "It eliminates special edge cases when modifying the head of the list (e.g. deleting the first node, inserting before head, merging lists). You can always safely return `dummy.next`.",
        "takeaway": "Always create a dummy head for linked list mutations to prevent null pointer exceptions."
    },

    # --- Dynamic Programming ---
    {
        "id": "dp-1",
        "topic": "Dynamic Programming",
        "difficulty": "Medium",
        "question": "What is the difference between 0/1 Knapsack and Unbounded Knapsack state transitions?",
        "answer": "In 0/1 Knapsack (each item usable once), the inner loop for capacity runs BACKWARDS from W down to weight[i], so the same item is not counted multiple times. In Unbounded Knapsack, it runs FORWARDS from weight[i] to W.",
        "takeaway": "Loop direction controls item reuse in 1D array space optimization."
    },
    {
        "id": "dp-2",
        "topic": "Dynamic Programming",
        "difficulty": "Hard",
        "question": "How can the Longest Increasing Subsequence (LIS) be solved in O(N log N) instead of O(N^2)?",
        "answer": "Patience Sorting with Binary Search! Maintain a list `tails` where `tails[i]` stores the smallest tail of all increasing subsequences of length i+1. For each x, binary search (bisect_left) in `tails`: replace if found, append if larger. Final length is len(tails).",
        "takeaway": "LIS length is found via binary search over increasing tail elements."
    },
    {
        "id": "dp-3",
        "topic": "Dynamic Programming",
        "difficulty": "Medium",
        "question": "When does a recursive problem qualify for Dynamic Programming?",
        "answer": "When it satisfies two key properties: 1) Optimal Substructure (optimal solution contains optimal sub-solutions), and 2) Overlapping Subproblems (the same subproblems are solved repeatedly).",
        "takeaway": "Overlapping subproblems + optimal substructure = memoization or tabulation."
    },

    # --- Bit Manipulation & Complexity ---
    {
        "id": "bit-1",
        "topic": "Bit Manipulation",
        "difficulty": "Easy",
        "question": "What does the bitwise expression `n & (n - 1)` do?",
        "answer": "It clears the lowest (rightmost) set bit of `n`! This is Brian Kernighan's algorithm to count set bits in O(k) operations (k = number of 1s). Also tests if n is a power of two: `n > 0 and (n & (n - 1)) == 0`.",
        "takeaway": "`n & (n - 1)` strips the lowest 1-bit. Vital for bit counting and power-of-two checks."
    },
    {
        "id": "bit-2",
        "topic": "Bit Manipulation",
        "difficulty": "Easy",
        "question": "Every number appears twice except ONE number that appears once. How do you find it in O(N) time and O(1) space?",
        "answer": "XOR all numbers together! Because `x ^ x = 0` and `x ^ 0 = x`, all pairs cancel out, leaving exactly the single unique number.",
        "takeaway": "XOR cancels identical pairs and preserves odd occurrences."
    },
    {
        "id": "comp-1",
        "topic": "Complexity",
        "difficulty": "Medium",
        "question": "Why is QuickSort preferred over MergeSort for arrays, but MergeSort preferred for Linked Lists?",
        "answer": "QuickSort sorts in-place (O(1) auxiliary space) and has excellent CPU cache locality on arrays. Linked Lists have non-contiguous memory so cache locality is lost, but MergeSort can merge linked lists with O(1) space without random access!",
        "takeaway": "Arrays favor QuickSort cache locality; Linked Lists favor MergeSort sequential pointer merging."
    }
]


def get_daily_flashcards(date_str: Optional[str] = None, count: int = 5) -> Dict[str, Any]:
    """Deterministically selects `count` flashcards for the given date.
    
    Every single calendar day has a completely fresh, deterministic deck of cards
    so students persistently learn new concepts every single day!
    """
    if not date_str:
        date_str = datetime.date.today().isoformat()

    # Create a stable seed from the date string, e.g. "2026-11-03"
    seed_val = int(hashlib.md5(date_str.encode("utf-8")).hexdigest(), 16)
    rng = random.Random(seed_val)

    # Pick a balanced daily selection
    shuffled_indices = list(range(len(FLASHCARD_BANK)))
    rng.shuffle(shuffled_indices)
    selected_indices = shuffled_indices[:count]

    cards = [FLASHCARD_BANK[i] for i in selected_indices]

    # Calculate day number of the year for streak display
    try:
        dt = datetime.date.fromisoformat(date_str)
        day_num = dt.timetuple().tm_yday
        day_title = f"Day {day_num} • Daily Interview Drill"
    except Exception:
        day_title = "Daily Interview Drill"

    return {
        "date": date_str,
        "day_title": day_title,
        "total_bank_size": len(FLASHCARD_BANK),
        "cards": cards,
    }


def generate_ai_flashcards(topic: str = "general", count: int = 5, model: str = "llama3.2:3b") -> Dict[str, Any]:
    """Generates brand new, novel interview flashcards on demand using the local LLM.
    
    If the LLM is busy or fails, it falls back to random selection from the bank.
    """
    prompt = f"""Generate {count} unique, high-yield technical interview flashcards on the DSA topic: '{topic}'.
Each card must be a real interview question or tricky complexity question asked at top tech companies.

Return ONLY a valid JSON array of {count} objects with these exact keys:
[
  {{
    "id": "ai-1",
    "topic": "{topic.title()}",
    "difficulty": "Medium",
    "question": "Question statement here?",
    "answer": "Direct, clear answer here.",
    "takeaway": "One-line rule or takeaway."
  }}
]
No extra text, no markdown backticks, just the raw JSON array."""

    content = ""
    # Try Groq Cloud Llama if API key is present
    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    if groq_key:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
            }
            res = httpx.post(url, headers=headers, json=payload, timeout=20.0)
            if res.status_code == 200:
                content = res.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"[groq flashcards]: {e}")

    # Otherwise try local Ollama if available
    if not content and ollama is not None:
        try:
            clean_m = model.split()[0].strip()
            resp = ollama.chat(
                model=clean_m,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.4, "num_ctx": 2048},
            )
            content = resp.message.content.strip()
        except Exception as e:
            print(f"[ollama flashcards fallback]: {e}")

    if content:
        try:
            if content.startswith("```"):
                lines = content.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                content = "\n".join(lines).strip()

            parsed = json.loads(content)
            if isinstance(parsed, list) and len(parsed) > 0:
                return {
                    "date": datetime.date.today().isoformat(),
                    "day_title": f"Custom AI Deck: {topic.title()}",
                    "cards": parsed[:count],
                    "generated": True,
                }
        except Exception as e:
            print(f"[json parse flashcards]: {e}")

    # Fallback to random sample from curated bank
    sample = random.sample(FLASHCARD_BANK, min(count, len(FLASHCARD_BANK)))
    return {
        "date": datetime.date.today().isoformat(),
        "day_title": f"Interview Practice: {topic.title()}",
        "cards": sample,
        "generated": False,
    }
