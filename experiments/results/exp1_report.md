# Experiment 1 - BFS and DFS (draft sheet, auto-generated)

## Objective
Measure runtime, visited vertices and examined edges of BFS and DFS on sparse, medium and dense road networks of growing size, verify correctness, and compare the observed growth with the theoretical O(V+E).

## Environment
Date: 2026-11-20 15:26 | Python 3.13.15 (CPython) | OS: Windows-11-10.0.26300-SP0 | CPU: Intel64 Family 6 Model 142 Stepping 12, GenuineIntel, AMD64, 8 logical cores

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
| sparse | 100 | 111 | bfs_traverse | 0.1147 | 0.1084 | 0.0103 | 100 | 222 | 0.5435 |
| sparse | 100 | 111 | dfs_traverse | 0.3158 | 0.28 | 0.0669 | 100 | 222 | 1.4965 |
| sparse | 100 | 111 | dfs_analysis_full | 0.7675 | 0.7016 | 0.1746 | 100 | 222 | 3.6374 |
| medium | 100 | 180 | bfs_traverse | 0.1942 | 0.1877 | 0.0312 | 100 | 360 | 0.6934 |
| medium | 100 | 180 | dfs_traverse | 0.3855 | 0.3877 | 0.0437 | 100 | 360 | 1.3767 |
| medium | 100 | 180 | dfs_analysis_full | 0.822 | 0.8026 | 0.0368 | 100 | 360 | 2.9359 |
| dense | 100 | 342 | bfs_traverse | 0.6827 | 0.2909 | 0.8469 | 100 | 684 | 1.5446 |
| dense | 100 | 342 | dfs_traverse | 0.8682 | 0.8032 | 0.3033 | 100 | 684 | 1.9644 |
| dense | 100 | 342 | dfs_analysis_full | 2.5842 | 2.7048 | 0.5744 | 100 | 684 | 5.8466 |
| sparse | 256 | 288 | bfs_traverse | 0.5151 | 0.5116 | 0.0259 | 256 | 576 | 0.947 |
| sparse | 256 | 288 | dfs_traverse | 0.8792 | 0.868 | 0.1143 | 256 | 576 | 1.6162 |
| sparse | 256 | 288 | dfs_analysis_full | 1.9328 | 1.8755 | 0.2153 | 256 | 576 | 3.553 |
| medium | 256 | 480 | bfs_traverse | 0.7596 | 0.6667 | 0.2707 | 256 | 960 | 1.0321 |
| medium | 256 | 480 | dfs_traverse | 1.3757 | 1.1803 | 0.4597 | 256 | 960 | 1.8691 |
| medium | 256 | 480 | dfs_analysis_full | 3.695 | 3.5617 | 0.6558 | 256 | 960 | 5.0204 |
| dense | 256 | 930 | bfs_traverse | 2.1437 | 1.8243 | 0.8447 | 256 | 1860 | 1.8075 |
| dense | 256 | 930 | dfs_traverse | 3.2295 | 3.4513 | 0.6863 | 256 | 1860 | 2.723 |
| dense | 256 | 930 | dfs_analysis_full | 8.279 | 8.2318 | 0.6372 | 256 | 1860 | 6.9806 |
| sparse | 576 | 654 | bfs_traverse | 3.6189 | 2.8641 | 1.7775 | 576 | 1308 | 2.9422 |
| sparse | 576 | 654 | dfs_traverse | 6.1238 | 4.3868 | 2.8946 | 576 | 1308 | 4.9787 |
| sparse | 576 | 654 | dfs_analysis_full | 11.3029 | 11.4062 | 2.1105 | 576 | 1308 | 9.1894 |
| medium | 576 | 1104 | bfs_traverse | 1.3834 | 1.2881 | 0.3326 | 576 | 2208 | 0.8234 |
| medium | 576 | 1104 | dfs_traverse | 9.0514 | 9.2978 | 3.2641 | 576 | 2208 | 5.3877 |
| medium | 576 | 1104 | dfs_analysis_full | 24.0304 | 23.1352 | 5.6848 | 576 | 2208 | 14.3038 |
| dense | 576 | 2162 | bfs_traverse | 5.0319 | 4.8877 | 1.4235 | 576 | 4324 | 1.8378 |
| dense | 576 | 2162 | dfs_traverse | 10.9276 | 8.4784 | 5.1203 | 576 | 4324 | 3.9911 |
| dense | 576 | 2162 | dfs_analysis_full | 20.6266 | 20.3853 | 3.3371 | 576 | 4324 | 7.5334 |
| sparse | 1024 | 1167 | bfs_traverse | 5.4916 | 5.484 | 1.0754 | 1024 | 2334 | 2.5064 |
| sparse | 1024 | 1167 | dfs_traverse | 7.6373 | 7.4368 | 1.0692 | 1024 | 2334 | 3.4858 |
| sparse | 1024 | 1167 | dfs_analysis_full | 20.3491 | 19.1504 | 3.5268 | 1024 | 2334 | 9.2876 |
| medium | 1024 | 1984 | bfs_traverse | 2.3512 | 2.1775 | 0.7076 | 1024 | 3968 | 0.7817 |
| medium | 1024 | 1984 | dfs_traverse | 5.2814 | 4.9787 | 1.0367 | 1024 | 3968 | 1.7558 |
| medium | 1024 | 1984 | dfs_analysis_full | 13.8967 | 14.8295 | 1.4391 | 1024 | 3968 | 4.6199 |
| dense | 1024 | 3906 | bfs_traverse | 5.1821 | 5.1518 | 1.4848 | 1024 | 7812 | 1.0511 |
| dense | 1024 | 3906 | dfs_traverse | 8.0859 | 7.0127 | 2.0034 | 1024 | 7812 | 1.6401 |
| dense | 1024 | 3906 | dfs_analysis_full | 14.9614 | 13.7967 | 2.495 | 1024 | 7812 | 3.0348 |
| sparse | 1600 | 1827 | bfs_traverse | 2.383 | 2.272 | 0.5756 | 1600 | 3654 | 0.6953 |
| sparse | 1600 | 1827 | dfs_traverse | 5.4012 | 4.97 | 1.0007 | 1600 | 3654 | 1.5761 |
| sparse | 1600 | 1827 | dfs_analysis_full | 14.083 | 14.4218 | 2.3129 | 1600 | 3654 | 4.1094 |
| medium | 1600 | 3120 | bfs_traverse | 3.3747 | 3.4 | 0.894 | 1600 | 6240 | 0.715 |
| medium | 1600 | 3120 | dfs_traverse | 7.4658 | 7.2885 | 1.0828 | 1600 | 6240 | 1.5817 |
| medium | 1600 | 3120 | dfs_analysis_full | 15.1846 | 14.7031 | 2.9669 | 1600 | 6240 | 3.2171 |
| dense | 1600 | 6162 | bfs_traverse | 8.1642 | 7.5126 | 1.6841 | 1600 | 12324 | 1.0518 |
| dense | 1600 | 6162 | dfs_traverse | 14.2629 | 13.5083 | 1.8284 | 1600 | 12324 | 1.8375 |
| dense | 1600 | 6162 | dfs_analysis_full | 82.0394 | 36.9611 | 67.113 | 1600 | 12324 | 10.5694 |
| sparse | 3136 | 3588 | bfs_traverse | 9.8004 | 9.3768 | 1.4102 | 3136 | 7176 | 1.4575 |
| sparse | 3136 | 3588 | dfs_traverse | 19.6725 | 19.3405 | 2.9451 | 3136 | 7176 | 2.9257 |
| sparse | 3136 | 3588 | dfs_analysis_full | 74.3747 | 67.6689 | 21.6041 | 3136 | 7176 | 11.0611 |
| medium | 3136 | 6160 | bfs_traverse | 14.1024 | 14.6259 | 3.0415 | 3136 | 12320 | 1.517 |
| medium | 3136 | 6160 | dfs_traverse | 25.0659 | 25.2972 | 1.7243 | 3136 | 12320 | 2.6964 |
| medium | 3136 | 6160 | dfs_analysis_full | 77.5339 | 69.7987 | 17.5084 | 3136 | 12320 | 8.3406 |
| dense | 3136 | 12210 | bfs_traverse | 30.0708 | 26.2368 | 8.5163 | 3136 | 24420 | 1.9595 |
| dense | 3136 | 12210 | dfs_traverse | 60.5832 | 62.4528 | 8.1912 | 3136 | 24420 | 3.9478 |
| dense | 3136 | 12210 | dfs_analysis_full | 146.2473 | 136.3936 | 28.6227 | 3136 | 24420 | 9.53 |

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
