# Binary Tree and Traversals

## What it is
A binary tree is a structure where each node has at most two children (left and right). The depth of a node is its distance from the root, and the height of the tree is the longest root-to-leaf path. Most tree problems are solved with recursion: solve for the left subtree, solve for the right subtree, combine the results.

## Traversals
Inorder: left, node, right (gives sorted order in a BST). Preorder: node, left, right (copying or serializing a tree). Postorder: left, right, node (compute a value from the children first, such as height or deleting a tree). Level order: BFS using a queue, one level at a time. All are O(n) time, and recursion uses O(h) space where h is the height.

## Python code
    from collections import deque

    class TreeNode:
        def __init__(self, val=0, left=None, right=None):
            self.val, self.left, self.right = val, left, right

    def inorder(root):
        return inorder(root.left) + [root.val] + inorder(root.right) if root else []

    def height(root):
        return 0 if not root else 1 + max(height(root.left), height(root.right))

    def level_order(root):
        if not root:
            return []
        res, queue = [], deque([root])
        while queue:
            level = []
            for _ in range(len(queue)):        # process one full level
                node = queue.popleft()
                level.append(node.val)
                if node.left: queue.append(node.left)
                if node.right: queue.append(node.right)
            res.append(level)
        return res

## Common problems
Maximum Depth of Binary Tree, Invert Binary Tree, Diameter of Binary Tree, Balanced Binary Tree, Binary Tree Level Order Traversal, Lowest Common Ancestor, Path Sum, Serialize and Deserialize Binary Tree.
