Sliding window

A sliding window keeps a range [left, right] over an array or string and moves it forward instead of recomputing from scratch.

Use it for the longest or shortest subarray or substring that satisfies a condition, such as the maximum sum of k consecutive elements.

Example: longest substring without repeating characters. Expand right, and when a duplicate appears move left forward until the window is valid again. Time O(n).