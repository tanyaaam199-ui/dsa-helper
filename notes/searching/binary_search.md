# Binary Search

## What it is
Binary search finds a target in a sorted array by repeatedly halving the search range. Compare the middle element with the target and throw away the half that cannot contain it. Time O(log n), space O(1).

## When to use
Sorted arrays, rotated sorted arrays, finding the first or last position of a value, and "binary search on the answer": when you can check if a value works (a monotonic yes/no condition) and want the smallest or largest value that works. Keywords: "sorted", "minimum such that", "maximum possible", "log n".

## Python code (standard)
    def binary_search(nums, target):
        lo, hi = 0, len(nums) - 1
        while lo <= hi:
            mid = lo + (hi - lo) // 2
            if nums[mid] == target:
                return mid
            elif nums[mid] < target:
                lo = mid + 1
            else:
                hi = mid - 1
        return -1

## Python code (search on the answer: smallest value that works)
    def smallest_valid(lo, hi, is_ok):    # is_ok(x) is False...False True...True
        while lo < hi:
            mid = lo + (hi - lo) // 2
            if is_ok(mid):
                hi = mid          # mid might be the answer, keep it
            else:
                lo = mid + 1
        return lo

## Tips
Common bugs are infinite loops from wrong lo/hi updates and off-by-one errors. With "while lo <= hi" always move to mid + 1 or mid - 1. With "while lo < hi" use hi = mid and lo = mid + 1. Python's bisect_left and bisect_right give the first position at or after, or after, a value.

## Common problems
Binary Search, Search in Rotated Sorted Array, Find First and Last Position of Element, Koko Eating Bananas, Capacity to Ship Packages Within D Days, Find Minimum in Rotated Sorted Array, Median of Two Sorted Arrays.
