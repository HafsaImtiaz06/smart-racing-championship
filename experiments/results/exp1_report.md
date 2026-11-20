# Experiment 1 - BFS and DFS (draft sheet, auto-generated)

## Objective
Measure runtime, visited vertices and examined edges of BFS and DFS on sparse, medium and dense road networks of growing size, verify correctness, and compare the observed growth with the theoretical O(V+E).

## Environment
Date: 2026-11-20 15:38 | Python 3.13.15 (CPython) | OS: Windows-11-10.0.26300-SP0 | CPU: Intel64 Family 6 Model 142 Stepping 12, GenuineIntel, AMD64, 8 logical cores

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
| sparse | 100 | 111 | bfs_traverse | 0.1126 | 0.1077 | 0.0117 | 100 | 222 | 0.5337 |
| sparse | 100 | 111 | dfs_traverse | 0.2699 | 0.2648 | 0.0097 | 100 | 222 | 1.2789 |
| sparse | 100 | 111 | dfs_analysis_full | 0.4636 | 0.4569 | 0.0409 | 100 | 222 | 2.1972 |
| medium | 100 | 180 | bfs_traverse | 0.1448 | 0.1408 | 0.0095 | 100 | 360 | 0.5173 |
| medium | 100 | 180 | dfs_traverse | 0.3342 | 0.3266 | 0.0202 | 100 | 360 | 1.1935 |
| medium | 100 | 180 | dfs_analysis_full | 0.6713 | 0.6002 | 0.1345 | 100 | 360 | 2.3974 |
| dense | 100 | 342 | bfs_traverse | 0.26 | 0.2477 | 0.0277 | 100 | 684 | 0.5883 |
| dense | 100 | 342 | dfs_traverse | 0.5544 | 0.533 | 0.0837 | 100 | 684 | 1.2543 |
| dense | 100 | 342 | dfs_analysis_full | 0.7794 | 0.755 | 0.073 | 100 | 684 | 1.7633 |
| sparse | 256 | 288 | bfs_traverse | 0.3056 | 0.2989 | 0.0189 | 256 | 576 | 0.5618 |
| sparse | 256 | 288 | dfs_traverse | 0.6051 | 0.6078 | 0.0344 | 256 | 576 | 1.1123 |
| sparse | 256 | 288 | dfs_analysis_full | 1.1752 | 1.0404 | 0.2069 | 256 | 576 | 2.1603 |
| medium | 256 | 480 | bfs_traverse | 0.3132 | 0.2912 | 0.0582 | 256 | 960 | 0.4255 |
| medium | 256 | 480 | dfs_traverse | 0.7296 | 0.7241 | 0.0158 | 256 | 960 | 0.9914 |
| medium | 256 | 480 | dfs_analysis_full | 1.4815 | 1.3834 | 0.2406 | 256 | 960 | 2.0129 |
| dense | 256 | 930 | bfs_traverse | 0.713 | 0.536 | 0.3335 | 256 | 1860 | 0.6012 |
| dense | 256 | 930 | dfs_traverse | 1.4429 | 1.4132 | 0.3181 | 256 | 1860 | 1.2166 |
| dense | 256 | 930 | dfs_analysis_full | 2.1737 | 2.0236 | 0.6108 | 256 | 1860 | 1.8328 |
| sparse | 576 | 654 | bfs_traverse | 0.6792 | 0.6644 | 0.0379 | 576 | 1308 | 0.5522 |
| sparse | 576 | 654 | dfs_traverse | 2.3036 | 1.932 | 0.8716 | 576 | 1308 | 1.8729 |
| sparse | 576 | 654 | dfs_analysis_full | 3.3605 | 2.9505 | 1.184 | 576 | 1308 | 2.7321 |
| medium | 576 | 1104 | bfs_traverse | 1.2802 | 1.1544 | 0.3153 | 576 | 2208 | 0.762 |
| medium | 576 | 1104 | dfs_traverse | 2.6176 | 2.377 | 0.7394 | 576 | 2208 | 1.5581 |
| medium | 576 | 1104 | dfs_analysis_full | 4.3894 | 3.7797 | 1.1261 | 576 | 2208 | 2.6127 |
| dense | 576 | 2162 | bfs_traverse | 1.9251 | 1.6225 | 0.4769 | 576 | 4324 | 0.7031 |
| dense | 576 | 2162 | dfs_traverse | 4.8364 | 3.9566 | 1.5738 | 576 | 4324 | 1.7664 |
| dense | 576 | 2162 | dfs_analysis_full | 7.5253 | 7.1955 | 1.3928 | 576 | 4324 | 2.7485 |
| sparse | 1024 | 1167 | bfs_traverse | 1.5672 | 1.356 | 0.553 | 1024 | 2334 | 0.7153 |
| sparse | 1024 | 1167 | dfs_traverse | 3.1526 | 2.7948 | 0.7282 | 1024 | 2334 | 1.4389 |
| sparse | 1024 | 1167 | dfs_analysis_full | 5.0302 | 5.0285 | 1.0125 | 1024 | 2334 | 2.2958 |
| medium | 1024 | 1984 | bfs_traverse | 2.2885 | 1.5446 | 1.2296 | 1024 | 3968 | 0.7608 |
| medium | 1024 | 1984 | dfs_traverse | 5.0812 | 5.1418 | 1.2839 | 1024 | 3968 | 1.6892 |
| medium | 1024 | 1984 | dfs_analysis_full | 7.2742 | 6.7457 | 0.9558 | 1024 | 3968 | 2.4183 |
| dense | 1024 | 3906 | bfs_traverse | 4.726 | 4.1529 | 1.5092 | 1024 | 7812 | 0.9586 |
| dense | 1024 | 3906 | dfs_traverse | 10.8677 | 11.4569 | 1.8586 | 1024 | 7812 | 2.2044 |
| dense | 1024 | 3906 | dfs_analysis_full | 12.1902 | 12.4635 | 2.3097 | 1024 | 7812 | 2.4727 |
| sparse | 1600 | 1827 | bfs_traverse | 2.8164 | 2.9798 | 0.5988 | 1600 | 3654 | 0.8218 |
| sparse | 1600 | 1827 | dfs_traverse | 5.4489 | 5.0322 | 1.2183 | 1600 | 3654 | 1.59 |
| sparse | 1600 | 1827 | dfs_analysis_full | 9.2752 | 8.677 | 2.1709 | 1600 | 3654 | 2.7065 |
| medium | 1600 | 3120 | bfs_traverse | 3.0523 | 2.9996 | 0.3871 | 1600 | 6240 | 0.6467 |
| medium | 1600 | 3120 | dfs_traverse | 7.0002 | 6.5263 | 1.3216 | 1600 | 6240 | 1.4831 |
| medium | 1600 | 3120 | dfs_analysis_full | 13.6244 | 13.6642 | 1.2846 | 1600 | 6240 | 2.8865 |
| dense | 1600 | 6162 | bfs_traverse | 6.1014 | 5.8296 | 1.5184 | 1600 | 12324 | 0.7861 |
| dense | 1600 | 6162 | dfs_traverse | 11.3598 | 11.251 | 1.0216 | 1600 | 12324 | 1.4635 |
| dense | 1600 | 6162 | dfs_analysis_full | 20.0176 | 18.7939 | 3.0388 | 1600 | 12324 | 2.5789 |
| sparse | 3136 | 3588 | bfs_traverse | 5.0767 | 4.9194 | 0.6345 | 3136 | 7176 | 0.755 |
| sparse | 3136 | 3588 | dfs_traverse | 10.0481 | 9.8851 | 1.2267 | 3136 | 7176 | 1.4944 |
| sparse | 3136 | 3588 | dfs_analysis_full | 30.821 | 29.4419 | 7.8331 | 3136 | 7176 | 4.5837 |
| medium | 3136 | 6160 | bfs_traverse | 9.7619 | 9.3023 | 1.7203 | 3136 | 12320 | 1.0501 |
| medium | 3136 | 6160 | dfs_traverse | 18.6128 | 18.5294 | 2.351 | 3136 | 12320 | 2.0022 |
| medium | 3136 | 6160 | dfs_analysis_full | 31.6962 | 31.0075 | 4.5719 | 3136 | 12320 | 3.4097 |
| dense | 3136 | 12210 | bfs_traverse | 11.7039 | 11.0367 | 1.9332 | 3136 | 24420 | 0.7627 |
| dense | 3136 | 12210 | dfs_traverse | 18.6923 | 16.6604 | 3.8062 | 3136 | 24420 | 1.2181 |
| dense | 3136 | 12210 | dfs_analysis_full | 44.8145 | 45.5891 | 14.5402 | 3136 | 24420 | 2.9203 |

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
