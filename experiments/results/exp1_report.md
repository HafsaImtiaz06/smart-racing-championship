# Experiment 1 - BFS and DFS (draft sheet, auto-generated)

## Objective
Measure runtime, visited vertices and examined edges of BFS and DFS on sparse, medium and dense road networks of growing size, verify correctness, and compare the observed growth with the theoretical O(V+E).

## Environment
Date: 2026-11-15 11:55 | Python 3.13.15 (CPython) | OS: Windows-11-10.0.26300-SP0 | CPU: Intel64 Family 6 Model 142 Stepping 12, GenuineIntel, AMD64, 8 logical cores

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
| sparse | 100 | 111 | bfs_traverse | 0.1138 | 0.1085 | 0.0116 | 100 | 222 | 0.5395 |
| sparse | 100 | 111 | dfs_traverse | 0.2367 | 0.232 | 0.0101 | 100 | 222 | 1.1217 |
| sparse | 100 | 111 | dfs_analysis_full | 0.6365 | 0.6297 | 0.041 | 100 | 222 | 3.0168 |
| medium | 100 | 180 | bfs_traverse | 0.1691 | 0.1644 | 0.0109 | 100 | 360 | 0.6041 |
| medium | 100 | 180 | dfs_traverse | 0.3761 | 0.3655 | 0.0172 | 100 | 360 | 1.3431 |
| medium | 100 | 180 | dfs_analysis_full | 1.0198 | 1.0051 | 0.0704 | 100 | 360 | 3.6421 |
| dense | 100 | 342 | bfs_traverse | 0.3641 | 0.3321 | 0.0656 | 100 | 684 | 0.8238 |
| dense | 100 | 342 | dfs_traverse | 0.9557 | 0.9383 | 0.0969 | 100 | 684 | 2.1621 |
| dense | 100 | 342 | dfs_analysis_full | 1.889 | 1.8445 | 0.0719 | 100 | 684 | 4.2737 |
| sparse | 256 | 288 | bfs_traverse | 0.6459 | 0.5108 | 0.1846 | 256 | 576 | 1.1873 |
| sparse | 256 | 288 | dfs_traverse | 1.2868 | 1.2912 | 0.0571 | 256 | 576 | 2.3654 |
| sparse | 256 | 288 | dfs_analysis_full | 1.7812 | 1.6956 | 0.2732 | 256 | 576 | 3.2743 |
| medium | 256 | 480 | bfs_traverse | 0.5204 | 0.4949 | 0.1568 | 256 | 960 | 0.7071 |
| medium | 256 | 480 | dfs_traverse | 1.1627 | 1.2051 | 0.0796 | 256 | 960 | 1.5798 |
| medium | 256 | 480 | dfs_analysis_full | 2.3975 | 2.3931 | 0.5684 | 256 | 960 | 3.2575 |
| dense | 256 | 930 | bfs_traverse | 0.6859 | 0.6838 | 0.0096 | 256 | 1860 | 0.5783 |
| dense | 256 | 930 | dfs_traverse | 1.5692 | 1.511 | 0.2107 | 256 | 1860 | 1.3231 |
| dense | 256 | 930 | dfs_analysis_full | 3.3755 | 3.4307 | 0.6458 | 256 | 1860 | 2.8461 |
| sparse | 576 | 654 | bfs_traverse | 0.8631 | 0.863 | 0.0423 | 576 | 1308 | 0.7017 |
| sparse | 576 | 654 | dfs_traverse | 1.9484 | 1.9949 | 0.2813 | 576 | 1308 | 1.584 |
| sparse | 576 | 654 | dfs_analysis_full | 3.0695 | 2.9005 | 0.4456 | 576 | 1308 | 2.4955 |
| medium | 576 | 1104 | bfs_traverse | 0.8838 | 0.883 | 0.1748 | 576 | 2208 | 0.5261 |
| medium | 576 | 1104 | dfs_traverse | 2.6387 | 2.322 | 0.6654 | 576 | 2208 | 1.5706 |
| medium | 576 | 1104 | dfs_analysis_full | 3.8899 | 3.8571 | 0.6152 | 576 | 2208 | 2.3154 |
| dense | 576 | 2162 | bfs_traverse | 1.7537 | 1.7168 | 0.1281 | 576 | 4324 | 0.6405 |
| dense | 576 | 2162 | dfs_traverse | 2.6259 | 2.5802 | 0.1438 | 576 | 4324 | 0.9591 |
| dense | 576 | 2162 | dfs_analysis_full | 6.573 | 6.4188 | 0.837 | 576 | 4324 | 2.4007 |
| sparse | 1024 | 1167 | bfs_traverse | 1.3672 | 1.3747 | 0.198 | 1024 | 2334 | 0.624 |
| sparse | 1024 | 1167 | dfs_traverse | 2.6741 | 2.2776 | 0.7735 | 1024 | 2334 | 1.2205 |
| sparse | 1024 | 1167 | dfs_analysis_full | 5.2658 | 5.0264 | 0.5671 | 1024 | 2334 | 2.4034 |
| medium | 1024 | 1984 | bfs_traverse | 1.8388 | 1.7356 | 0.4281 | 1024 | 3968 | 0.6113 |
| medium | 1024 | 1984 | dfs_traverse | 4.2976 | 4.3454 | 1.5357 | 1024 | 3968 | 1.4287 |
| medium | 1024 | 1984 | dfs_analysis_full | 8.4698 | 8.7479 | 1.0632 | 1024 | 3968 | 2.8158 |
| dense | 1024 | 3906 | bfs_traverse | 2.7194 | 2.4817 | 0.6882 | 1024 | 7812 | 0.5516 |
| dense | 1024 | 3906 | dfs_traverse | 5.0526 | 4.4674 | 0.902 | 1024 | 7812 | 1.0249 |
| dense | 1024 | 3906 | dfs_analysis_full | 13.9719 | 15.0572 | 1.721 | 1024 | 7812 | 2.8341 |
| sparse | 1600 | 1827 | bfs_traverse | 1.681 | 1.5519 | 0.3495 | 1600 | 3654 | 0.4905 |
| sparse | 1600 | 1827 | dfs_traverse | 3.9877 | 3.7445 | 0.7479 | 1600 | 3654 | 1.1636 |
| sparse | 1600 | 1827 | dfs_analysis_full | 9.1773 | 9.9043 | 1.2518 | 1600 | 3654 | 2.6779 |
| medium | 1600 | 3120 | bfs_traverse | 2.5475 | 2.4258 | 0.366 | 1600 | 6240 | 0.5397 |
| medium | 1600 | 3120 | dfs_traverse | 5.2189 | 4.8552 | 0.8851 | 1600 | 6240 | 1.1057 |
| medium | 1600 | 3120 | dfs_analysis_full | 11.5532 | 11.5336 | 0.931 | 1600 | 6240 | 2.4477 |
| dense | 1600 | 6162 | bfs_traverse | 3.5404 | 3.5438 | 0.3822 | 1600 | 12324 | 0.4561 |
| dense | 1600 | 6162 | dfs_traverse | 7.9787 | 7.8947 | 0.8345 | 1600 | 12324 | 1.0279 |
| dense | 1600 | 6162 | dfs_analysis_full | 18.3558 | 18.0942 | 0.822 | 1600 | 12324 | 2.3648 |
| sparse | 3136 | 3588 | bfs_traverse | 3.5009 | 3.4636 | 0.5042 | 3136 | 7176 | 0.5207 |
| sparse | 3136 | 3588 | dfs_traverse | 6.3159 | 6.101 | 0.6187 | 3136 | 7176 | 0.9393 |
| sparse | 3136 | 3588 | dfs_analysis_full | 16.4799 | 16.2647 | 0.5113 | 3136 | 7176 | 2.4509 |
| medium | 3136 | 6160 | bfs_traverse | 4.5032 | 4.4174 | 0.4959 | 3136 | 12320 | 0.4844 |
| medium | 3136 | 6160 | dfs_traverse | 11.079 | 9.2629 | 4.0448 | 3136 | 12320 | 1.1918 |
| medium | 3136 | 6160 | dfs_analysis_full | 27.0732 | 23.5244 | 6.5899 | 3136 | 12320 | 2.9123 |
| dense | 3136 | 12210 | bfs_traverse | 8.3206 | 8.3797 | 0.845 | 3136 | 24420 | 0.5422 |
| dense | 3136 | 12210 | dfs_traverse | 17.0583 | 17.8336 | 1.2905 | 3136 | 24420 | 1.1116 |
| dense | 3136 | 12210 | dfs_analysis_full | 63.4224 | 57.4959 | 7.8886 | 3136 | 24420 | 4.1328 |

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
