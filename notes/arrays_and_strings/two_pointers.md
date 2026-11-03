Two pointers

Two pointers uses two indices that move through an array, usually from both ends or one behind the other.

Use it on sorted arrays or when you need to find a pair, remove duplicates, or reverse in place.

Example: in a sorted array, find two numbers that sum to a target. Put one pointer at the start and one at the end. If the sum is too small move the left pointer right, if too big move the right pointer left. Time O(n), space O(1).