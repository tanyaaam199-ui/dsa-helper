# Linked List

## What it is
A linked list is a chain of nodes where each node stores a value and a pointer to the next node. Access by index is O(n), but inserting or deleting at a known node is O(1). Most problems use pointer tricks: a dummy node, fast and slow pointers, and reversing links.

## When to use
Reverse a list, find the middle, detect a cycle, merge two sorted lists, remove the n-th node from the end, check a palindrome. Keywords: "linked list", "in-place", "O(1) space".

## Python code
    class ListNode:
        def __init__(self, val=0, next=None):
            self.val, self.next = val, next

    def reverse(head):
        prev = None
        while head:
            nxt = head.next
            head.next = prev
            prev, head = head, nxt
        return prev

    def has_cycle(head):            # fast and slow pointers (Floyd)
        slow = fast = head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
