"""PERSON C. CONTRACT (frozen). ONE comparator for everything.
Signatures unchanged; implementations live in comparator.py and sorts.py (re-exported here)."""
from .comparator import championship_key, better, compare
from .sorts import merge_sort, quick_sort, heap_sort, top_k
