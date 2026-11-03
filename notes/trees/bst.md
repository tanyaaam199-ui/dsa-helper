# Binary Search Tree (BST)

## What it is
A BST is a binary tree where for every node, all values in the left subtree are smaller and all values in the right subtree are larger. An inorder traversal of a BST gives the values in sorted order. Search, insert and delete take O(h): O(log n) when balanced, O(n) in the worst case when the tree is a chain.

## When to use
Problems about sorted order inside a tree: validate a BST, k-th smallest element, closest value, lowest common ancestor in a BST, convert a sorted array to a BST. Keywords: "BST", "inorder", "sorted".

## Python code
    def search(root, target):
        while root and root.val != target:
            root = root.left if target < root.val else root.right
        return root

    def is_valid_bst(root, low=float("-inf"), high=float("inf")):
        if not root:
            return True
        if not (low < root.val < high):
            return False
        return (is_valid_bst(root.left, low, root.val) and
                is_valid_bst(root.right, root.val, high))

## Tips
Validating a BST by only comparing a node with its direct children is wrong. Pass down the allowed range (low, high), or check that inorder traversal is strictly increasing. For the lowest common ancestor in a BST, walk down: if both values are smaller go left, if both are larger go right, otherwise the current node is the answer.

## Common problems
Validate Binary Search Tree, Kth Smallest Element in a BST, Lowest Common Ancestor of a BST, Insert into a BST, Convert Sorted Array to BST.
