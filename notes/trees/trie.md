# Trie (Prefix Tree)

## What it is
A trie stores strings character by character in a tree, where each node represents one character and a flag marks the end of a word. Words sharing a prefix share the same path. Insert, search and prefix lookup all take O(L) where L is the length of the word, independent of how many words are stored.

## When to use
Prefix problems: autocomplete, "starts with", dictionary of words, word search with many words, longest common prefix, replacing words with their roots. Keywords: "prefix", "dictionary", "autocomplete".

## Python code
    class Trie:
        def __init__(self):
            self.children = {}
            self.is_end = False

        def insert(self, word):
            node = self
            for ch in word:
                node = node.children.setdefault(ch, Trie())
            node.is_end = True

        def _walk(self, s):
            node = self
            for ch in s:
                if ch not in node.children:
                    return None
                node = node.children[ch]
            return node

        def search(self, word):
            node = self._walk(word)
            return node is not None and node.is_end

        def starts_with(self, prefix):
            return self._walk(prefix) is not None

## Tips
A word and a prefix differ only by the end flag: search needs is_end to be true, starts_with does not. Use a trie instead of a hash set when many lookups share prefixes, or when you must explore characters step by step (Word Search II).

## Common problems
Implement Trie, Design Add and Search Words Data Structure, Word Search II, Replace Words, Longest Word in Dictionary, Search Suggestions System.
