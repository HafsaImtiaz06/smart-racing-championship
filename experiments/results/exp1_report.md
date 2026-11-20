# Experiment 1 - BFS and DFS (draft sheet, auto-generated)

## Objective
Measure runtime, visited vertices and examined edges of BFS and DFS on sparse, medium and dense road networks of growing size, verify correctness, and compare the observed growth with the theoretical O(V+E).

## Environment
Date: 2026-11-20 15:42 | Python 3.13.15 (CPython) | OS: Windows-11-10.0.26300-SP0 | CPU: Intel64 Family 6 Model 142 Stepping 12, GenuineIntel, AMD64, 8 logical cores

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
| sparse | 100 | 111 | bfs_traverse | 0.1938 | 0.1825 | 0.0249 | 100 | 222 | 0.9184 |
| sparse | 100 | 111 | dfs_traverse | 0.2413 | 0.2321 | 0.0193 | 100 | 222 | 1.1437 |
| sparse | 100 | 111 | dfs_analysis_full | 0.4716 | 0.4461 | 0.0861 | 100 | 222 | 2.235 |
| medium | 100 | 180 | bfs_traverse | 0.1612 | 0.1577 | 0.027 | 100 | 360 | 0.5757 |
| medium | 100 | 180 | dfs_traverse | 0.3857 | 0.3213 | 0.1263 | 100 | 360 | 1.3774 |
| medium | 100 | 180 | dfs_analysis_full | 0.6891 | 0.6937 | 0.1485 | 100 | 360 | 2.4612 |
| dense | 100 | 342 | bfs_traverse | 0.3296 | 0.2883 | 0.0963 | 100 | 684 | 0.7458 |
| dense | 100 | 342 | dfs_traverse | 1.0195 | 0.992 | 0.0913 | 100 | 684 | 2.3066 |
| dense | 100 | 342 | dfs_analysis_full | 1.0155 | 0.9702 | 0.2092 | 100 | 684 | 2.2975 |
| sparse | 256 | 288 | bfs_traverse | 0.5653 | 0.533 | 0.1331 | 256 | 576 | 1.0392 |
| sparse | 256 | 288 | dfs_traverse | 0.8421 | 0.7801 | 0.1811 | 256 | 576 | 1.548 |
| sparse | 256 | 288 | dfs_analysis_full | 1.3264 | 1.2625 | 0.2677 | 256 | 576 | 2.4382 |
| medium | 256 | 480 | bfs_traverse | 0.4054 | 0.4076 | 0.0156 | 256 | 960 | 0.5509 |
| medium | 256 | 480 | dfs_traverse | 1.3481 | 1.1002 | 0.3977 | 256 | 960 | 1.8317 |
| medium | 256 | 480 | dfs_analysis_full | 1.7286 | 1.7248 | 0.2923 | 256 | 960 | 2.3486 |
| dense | 256 | 930 | bfs_traverse | 1.1101 | 1.2567 | 0.2387 | 256 | 1860 | 0.936 |
| dense | 256 | 930 | dfs_traverse | 3.1725 | 2.2065 | 2.4916 | 256 | 1860 | 2.675 |
| dense | 256 | 930 | dfs_analysis_full | 2.5674 | 2.488 | 0.3955 | 256 | 1860 | 2.1648 |
| sparse | 576 | 654 | bfs_traverse | 0.8677 | 0.837 | 0.2095 | 576 | 1308 | 0.7055 |
| sparse | 576 | 654 | dfs_traverse | 2.2739 | 2.0909 | 0.5219 | 576 | 1308 | 1.8487 |
| sparse | 576 | 654 | dfs_analysis_full | 3.0462 | 2.9258 | 0.3199 | 576 | 1308 | 2.4766 |
| medium | 576 | 1104 | bfs_traverse | 1.1387 | 1.04 | 0.2 | 576 | 2208 | 0.6778 |
| medium | 576 | 1104 | dfs_traverse | 2.6335 | 2.6373 | 0.4708 | 576 | 2208 | 1.5676 |
| medium | 576 | 1104 | dfs_analysis_full | 6.7237 | 5.8273 | 3.2874 | 576 | 2208 | 4.0022 |
| dense | 576 | 2162 | bfs_traverse | 2.4481 | 2.3268 | 0.5552 | 576 | 4324 | 0.8941 |
| dense | 576 | 2162 | dfs_traverse | 3.9146 | 3.9442 | 0.1582 | 576 | 4324 | 1.4297 |
| dense | 576 | 2162 | dfs_analysis_full | 7.311 | 6.9341 | 1.0053 | 576 | 4324 | 2.6702 |
| sparse | 1024 | 1167 | bfs_traverse | 1.2758 | 1.2515 | 0.0569 | 1024 | 2334 | 0.5823 |
| sparse | 1024 | 1167 | dfs_traverse | 4.2134 | 3.2017 | 2.4802 | 1024 | 2334 | 1.923 |
| sparse | 1024 | 1167 | dfs_analysis_full | 5.4276 | 5.4249 | 0.2374 | 1024 | 2334 | 2.4772 |
| medium | 1024 | 1984 | bfs_traverse | 1.953 | 1.8795 | 0.2794 | 1024 | 3968 | 0.6493 |
| medium | 1024 | 1984 | dfs_traverse | 4.4426 | 4.3244 | 0.4629 | 1024 | 3968 | 1.4769 |
| medium | 1024 | 1984 | dfs_analysis_full | 8.2578 | 7.6475 | 2.2819 | 1024 | 3968 | 2.7453 |
| dense | 1024 | 3906 | bfs_traverse | 6.0726 | 5.6173 | 2.9312 | 1024 | 7812 | 1.2318 |
| dense | 1024 | 3906 | dfs_traverse | 8.5316 | 8.741 | 1.1809 | 1024 | 7812 | 1.7306 |
| dense | 1024 | 3906 | dfs_analysis_full | 18.9357 | 18.9679 | 2.8084 | 1024 | 7812 | 3.8409 |
| sparse | 1600 | 1827 | bfs_traverse | 13.3021 | 9.4001 | 10.5073 | 1600 | 3654 | 3.8816 |
| sparse | 1600 | 1827 | dfs_traverse | 59.1196 | 29.3146 | 53.5385 | 1600 | 3654 | 17.2511 |
| sparse | 1600 | 1827 | dfs_analysis_full | 54.1067 | 54.0058 | 14.4281 | 1600 | 3654 | 15.7884 |
| medium | 1600 | 3120 | bfs_traverse | 11.4966 | 12.5489 | 2.3503 | 1600 | 6240 | 2.4357 |
| medium | 1600 | 3120 | dfs_traverse | 32.1731 | 31.2712 | 5.5109 | 1600 | 6240 | 6.8163 |
| medium | 1600 | 3120 | dfs_analysis_full | 47.8261 | 46.07 | 11.2229 | 1600 | 6240 | 10.1327 |
| dense | 1600 | 6162 | bfs_traverse | 15.4375 | 14.2673 | 3.6029 | 1600 | 12324 | 1.9889 |
| dense | 1600 | 6162 | dfs_traverse | 28.3181 | 28.3215 | 3.2744 | 1600 | 12324 | 3.6483 |
| dense | 1600 | 6162 | dfs_analysis_full | 68.7347 | 63.8216 | 13.6196 | 1600 | 12324 | 8.8553 |
| sparse | 3136 | 3588 | bfs_traverse | 24.1732 | 18.6733 | 9.9178 | 3136 | 7176 | 3.5951 |
| sparse | 3136 | 3588 | dfs_traverse | 30.8029 | 27.1782 | 8.2703 | 3136 | 7176 | 4.581 |
| sparse | 3136 | 3588 | dfs_analysis_full | 48.8051 | 44.8456 | 20.4108 | 3136 | 7176 | 7.2583 |
| medium | 3136 | 6160 | bfs_traverse | 8.7351 | 8.5409 | 1.2663 | 3136 | 12320 | 0.9397 |
| medium | 3136 | 6160 | dfs_traverse | 22.2856 | 22.8304 | 4.756 | 3136 | 12320 | 2.3973 |
| medium | 3136 | 6160 | dfs_analysis_full | 34.6624 | 34.7254 | 5.5598 | 3136 | 12320 | 3.7287 |
| dense | 3136 | 12210 | bfs_traverse | 13.4766 | 13.0216 | 1.2195 | 3136 | 24420 | 0.8782 |
| dense | 3136 | 12210 | dfs_traverse | 33.3696 | 30.5292 | 8.1157 | 3136 | 24420 | 2.1745 |
| dense | 3136 | 12210 | dfs_analysis_full | 54.4698 | 53.2297 | 11.4075 | 3136 | 24420 | 3.5494 |

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
