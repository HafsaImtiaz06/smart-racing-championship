# Experiment 1 - BFS and DFS (draft sheet, auto-generated)

## Objective
Measure runtime, visited vertices and examined edges of BFS and DFS on sparse, medium and dense road networks of growing size, verify correctness, and compare the observed growth with the theoretical O(V+E).

## Environment
Date: 2026-11-21 17:26 | Python 3.13.15 (CPython) | OS: Windows-11-10.0.26300-SP0 | CPU: Intel64 Family 6 Model 142 Stepping 12, GenuineIntel, AMD64, 8 logical cores

Timing includes the data structures each call allocates (visited set, queue/stack, order list). It excludes building the graph, rendering and file I/O. Correctness checks run separately, never inside a timed call.

## Input generation
Jittered k x k grid networks built by `make_grid_graph` (see its docstring: coordinates, road rules, cost ranges). Seed = 1. sparse = spanning tree + 15% extra roads, medium = grid, dense = grid + diagonals.

## Dataset sizes
k = [10, 16, 24, 32, 40, 56], so V = [100, 256, 576, 1024, 1600, 3136].

## Procedure
For every graph: 2 warm-up calls, then 7 timed calls of: bfs_traverse (full BFS from vertex 0), dfs_traverse (full DFS from vertex 0) and dfs_analysis_full (DFS + cycle detection + components + dead ends). Mean, median and standard deviation of the timed calls are reported.

## Metrics
runtime (ms), visited vertices, examined edges (directed arcs looked at), microseconds per (V+E).

## Results
| graph | V | E | algorithm | mean ms | median ms | stdev ms | visited | examined | us per (V+E) |
|---|---|---|---|---|---|---|---|---|---|
| sparse | 100 | 111 | bfs_traverse | 0.0892 | 0.086 | 0.007 | 100 | 222 | 0.4226 |
| sparse | 100 | 111 | dfs_traverse | 0.2096 | 0.2041 | 0.012 | 100 | 222 | 0.9934 |
| sparse | 100 | 111 | dfs_analysis_full | 0.3787 | 0.352 | 0.079 | 100 | 222 | 1.7948 |
| medium | 100 | 180 | bfs_traverse | 0.2519 | 0.204 | 0.0825 | 100 | 360 | 0.8996 |
| medium | 100 | 180 | dfs_traverse | 0.2609 | 0.2535 | 0.0149 | 100 | 360 | 0.9316 |
| medium | 100 | 180 | dfs_analysis_full | 0.4323 | 0.4233 | 0.0287 | 100 | 360 | 1.5439 |
| dense | 100 | 342 | bfs_traverse | 0.326 | 0.3011 | 0.1201 | 100 | 684 | 0.7375 |
| dense | 100 | 342 | dfs_traverse | 0.404 | 0.3957 | 0.0198 | 100 | 684 | 0.914 |
| dense | 100 | 342 | dfs_analysis_full | 0.7823 | 0.7393 | 0.1028 | 100 | 684 | 1.77 |
| sparse | 256 | 288 | bfs_traverse | 0.256 | 0.2415 | 0.0311 | 256 | 576 | 0.4706 |
| sparse | 256 | 288 | dfs_traverse | 1.0861 | 1.0437 | 0.1391 | 256 | 576 | 1.9965 |
| sparse | 256 | 288 | dfs_analysis_full | 1.2078 | 1.2207 | 0.3713 | 256 | 576 | 2.2202 |
| medium | 256 | 480 | bfs_traverse | 0.3065 | 0.3039 | 0.0124 | 256 | 960 | 0.4165 |
| medium | 256 | 480 | dfs_traverse | 0.729 | 0.6854 | 0.1195 | 256 | 960 | 0.9904 |
| medium | 256 | 480 | dfs_analysis_full | 1.6719 | 1.4062 | 0.4504 | 256 | 960 | 2.2716 |
| dense | 256 | 930 | bfs_traverse | 0.5113 | 0.5112 | 0.0216 | 256 | 1860 | 0.4311 |
| dense | 256 | 930 | dfs_traverse | 1.8368 | 1.9116 | 0.3064 | 256 | 1860 | 1.5488 |
| dense | 256 | 930 | dfs_analysis_full | 2.0076 | 1.8521 | 0.4074 | 256 | 1860 | 1.6927 |
| sparse | 576 | 654 | bfs_traverse | 0.5563 | 0.5473 | 0.0226 | 576 | 1308 | 0.4523 |
| sparse | 576 | 654 | dfs_traverse | 1.51 | 1.3751 | 0.2753 | 576 | 1308 | 1.2277 |
| sparse | 576 | 654 | dfs_analysis_full | 4.4039 | 4.3817 | 0.2011 | 576 | 1308 | 3.5804 |
| medium | 576 | 1104 | bfs_traverse | 0.8768 | 0.8074 | 0.2353 | 576 | 2208 | 0.5219 |
| medium | 576 | 1104 | dfs_traverse | 3.1673 | 3.1281 | 0.1762 | 576 | 2208 | 1.8853 |
| medium | 576 | 1104 | dfs_analysis_full | 3.4503 | 3.1122 | 0.95 | 576 | 2208 | 2.0538 |
| dense | 576 | 2162 | bfs_traverse | 2.1435 | 2.5188 | 0.6359 | 576 | 4324 | 0.7829 |
| dense | 576 | 2162 | dfs_traverse | 3.7309 | 3.0497 | 1.384 | 576 | 4324 | 1.3626 |
| dense | 576 | 2162 | dfs_analysis_full | 8.2123 | 9.3034 | 2.2754 | 576 | 4324 | 2.9994 |
| sparse | 1024 | 1167 | bfs_traverse | 1.0215 | 0.9875 | 0.1023 | 1024 | 2334 | 0.4662 |
| sparse | 1024 | 1167 | dfs_traverse | 2.6733 | 2.6538 | 0.3504 | 1024 | 2334 | 1.2201 |
| sparse | 1024 | 1167 | dfs_analysis_full | 4.081 | 3.8135 | 0.5699 | 1024 | 2334 | 1.8626 |
| medium | 1024 | 1984 | bfs_traverse | 1.8517 | 1.6939 | 0.4326 | 1024 | 3968 | 0.6156 |
| medium | 1024 | 1984 | dfs_traverse | 4.2549 | 3.8732 | 0.8656 | 1024 | 3968 | 1.4145 |
| medium | 1024 | 1984 | dfs_analysis_full | 6.1514 | 6.2958 | 0.4485 | 1024 | 3968 | 2.045 |
| dense | 1024 | 3906 | bfs_traverse | 2.7233 | 2.4729 | 0.5745 | 1024 | 7812 | 0.5524 |
| dense | 1024 | 3906 | dfs_traverse | 6.0744 | 6.1752 | 0.6721 | 1024 | 7812 | 1.2321 |
| dense | 1024 | 3906 | dfs_analysis_full | 9.7479 | 9.9634 | 0.412 | 1024 | 7812 | 1.9773 |
| sparse | 1600 | 1827 | bfs_traverse | 1.6618 | 1.5901 | 0.147 | 1600 | 3654 | 0.4849 |
| sparse | 1600 | 1827 | dfs_traverse | 4.0805 | 3.8048 | 0.5605 | 1600 | 3654 | 1.1907 |
| sparse | 1600 | 1827 | dfs_analysis_full | 6.9534 | 6.9581 | 0.548 | 1600 | 3654 | 2.029 |
| medium | 1600 | 3120 | bfs_traverse | 2.3311 | 2.1788 | 0.2673 | 1600 | 6240 | 0.4939 |
| medium | 1600 | 3120 | dfs_traverse | 5.194 | 4.9944 | 0.4276 | 1600 | 6240 | 1.1004 |
| medium | 1600 | 3120 | dfs_analysis_full | 8.819 | 8.6764 | 0.4976 | 1600 | 6240 | 1.8684 |
| dense | 1600 | 6162 | bfs_traverse | 4.2974 | 4.2806 | 0.7231 | 1600 | 12324 | 0.5537 |
| dense | 1600 | 6162 | dfs_traverse | 12.5511 | 9.8543 | 6.538 | 1600 | 12324 | 1.617 |
| dense | 1600 | 6162 | dfs_analysis_full | 16.4323 | 15.7274 | 1.4829 | 1600 | 12324 | 2.117 |
| sparse | 3136 | 3588 | bfs_traverse | 6.0199 | 5.6957 | 1.7531 | 3136 | 7176 | 0.8953 |
| sparse | 3136 | 3588 | dfs_traverse | 8.1825 | 8.0744 | 0.7857 | 3136 | 7176 | 1.2169 |
| sparse | 3136 | 3588 | dfs_analysis_full | 13.6673 | 13.6624 | 0.7333 | 3136 | 7176 | 2.0326 |
| medium | 3136 | 6160 | bfs_traverse | 5.9998 | 5.6764 | 1.4096 | 3136 | 12320 | 0.6454 |
| medium | 3136 | 6160 | dfs_traverse | 12.847 | 11.6127 | 3.3165 | 3136 | 12320 | 1.382 |
| medium | 3136 | 6160 | dfs_analysis_full | 19.2975 | 18.8315 | 1.498 | 3136 | 12320 | 2.0759 |
| dense | 3136 | 12210 | bfs_traverse | 9.591 | 9.1418 | 1.7809 | 3136 | 24420 | 0.625 |
| dense | 3136 | 12210 | dfs_traverse | 19.5223 | 19.7945 | 1.2363 | 3136 | 24420 | 1.2721 |
| dense | 3136 | 12210 | dfs_analysis_full | 56.3839 | 41.1437 | 28.6919 | 3136 | 24420 | 3.6742 |

Chart: exp1_runtime.png.  Raw data: exp1_raw.csv.

## Verification
504 of 504 checks passed (details in exp1_verification.csv): BFS minimum edge count against a separate reference BFS, DFS components against union-find, DFS cycle flag against the edges >= vertices test.

## Interpretation (WRITE THIS YOURSELF after reading your own numbers)
- Do visited and examined counts match the theory? (visited = reachable vertices; examined = sum of degrees = 2E for two-way roads)
- Does microseconds per (V+E) stay roughly flat as V+E grows? If yes, growth is consistent with O(V+E); one run alone does not prove it.
- Compare BFS with DFS traversal, and traversal with the full analysis (which does extra passes).
- Compare sparse, medium and dense at the same V.

## Limitations
- One machine, one interpreter (CPython), one seed, grid-like graphs only.
- Python timings include interpreter overhead and can vary with background load.
- Real circuits are tiny; the large graphs are synthetic.

## Conclusion (write after the interpretation)
