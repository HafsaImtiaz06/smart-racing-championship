# Experiment 2 - Dijkstra and A* (draft sheet, auto-generated)

## Objective
Compare Dijkstra and A* on the same road networks and queries: runtime, expanded vertices, relaxed edges, heap operations and final path cost; verify equal optimal costs when the A* conditions hold; find cases where A* expands fewer, equal or more vertices.

## Environment
Date: 2026-11-21 17:26 | Python 3.13.15 (CPython) | OS: Windows-11-10.0.26300-SP0 | CPU: Intel64 Family 6 Model 142 Stepping 12, GenuineIntel, AMD64, 8 logical cores

Timing includes the heap, the distance/parent tables and building the returned path (cost, distance, time, fuel sums). It excludes graph construction, rendering and file I/O. Correctness checks run separately from the timed calls.

## Input generation
Synthetic jittered-grid networks from `make_grid_graph` (coordinates and cost ranges in its docstring), seed 1, plus every tracks/circuit*.json present (checkpoint-to-checkpoint legs and Start to Finish). Query pairs: the far corner pair plus random pairs. Presets: Balanced, Speed on grids, all four on circuits. A* heuristic = Graph.heuristic_ratio(preset) x straight-line distance; it is admissible when no road is shorter than the straight line (Graph.validate_geometry() == []).

## Dataset sizes
grid k = [10, 16, 24, 32, 40] (V = [100, 256, 576, 1024, 1600]), 15 queries per graph and preset.

## Procedure
For each query: 1 warm-up call(s), then 5 timed calls of each algorithm. Counters (expanded, relaxed, heap operations) and cost come from the last call; they are the same every run.

## Metrics
runtime (ms), expanded vertices, relaxed edges, heap operations (pushes + pops), final path cost.

## Results (means over the queries of each graph and preset; last column = queries where A* expanded fewer/equal/more)
| graph | preset | queries | Dij expanded | A* expanded | Dij ms | A* ms | Dij relaxed | A* relaxed | Dij heap ops | A* heap ops | A* fewer/equal/more |
|---|---|---|---|---|---|---|---|---|---|---|---|
| grid_k10_sparse_seed1 | Balanced | 15 | 49.333 | 40.867 | 0.704 | 0.722 | 109.8 | 91.933 | 105.4 | 89.0 | 14/1/0 |
| grid_k10_sparse_seed1 | Speed | 15 | 49.867 | 41.4 | 0.604 | 0.553 | 111.133 | 93.067 | 106.0 | 89.6 | 14/1/0 |
| grid_k10_medium_seed1 | Balanced | 15 | 48.8 | 28.667 | 0.718 | 0.553 | 176.2 | 103.267 | 122.6 | 81.8 | 15/0/0 |
| grid_k10_medium_seed1 | Speed | 15 | 48.8 | 29.467 | 0.979 | 0.806 | 176.067 | 106.133 | 124.8 | 84.6 | 15/0/0 |
| grid_k10_dense_seed1 | Balanced | 15 | 32.267 | 14.8 | 1.613 | 0.983 | 222.4 | 102.867 | 98.267 | 53.267 | 15/0/0 |
| grid_k10_dense_seed1 | Speed | 15 | 32.733 | 15.667 | 1.241 | 0.665 | 225.2 | 109.2 | 99.667 | 56.533 | 15/0/0 |
| grid_k16_sparse_seed1 | Balanced | 15 | 147.4 | 127.267 | 2.029 | 1.556 | 335.2 | 292.133 | 311.133 | 278.267 | 14/1/0 |
| grid_k16_sparse_seed1 | Speed | 15 | 148.267 | 129.733 | 1.893 | 1.994 | 337.2 | 297.267 | 311.933 | 279.4 | 13/2/0 |
| grid_k16_medium_seed1 | Balanced | 15 | 123.467 | 71.4 | 2.368 | 1.617 | 466.867 | 270.467 | 305.133 | 197.733 | 14/1/0 |
| grid_k16_medium_seed1 | Speed | 15 | 119.467 | 70.867 | 2.196 | 1.499 | 451.667 | 268.333 | 293.6 | 193.4 | 14/1/0 |
| grid_k16_dense_seed1 | Balanced | 15 | 113.4 | 56.4 | 3.716 | 2.065 | 839.4 | 425.733 | 349.467 | 199.933 | 15/0/0 |
| grid_k16_dense_seed1 | Speed | 15 | 113.333 | 58.933 | 3.863 | 2.213 | 838.333 | 444.6 | 351.067 | 211.733 | 15/0/0 |
| grid_k24_sparse_seed1 | Balanced | 15 | 290.533 | 238.4 | 3.339 | 3.164 | 675.4 | 555.133 | 615.667 | 511.533 | 15/0/0 |
| grid_k24_sparse_seed1 | Speed | 15 | 292.867 | 244.533 | 3.467 | 4.133 | 681.467 | 570.133 | 620.333 | 526.333 | 15/0/0 |
| grid_k24_medium_seed1 | Balanced | 15 | 309.133 | 172.4 | 5.934 | 3.784 | 1195.467 | 671.0 | 764.6 | 480.0 | 14/1/0 |
| grid_k24_medium_seed1 | Speed | 15 | 307.467 | 177.867 | 4.987 | 3.491 | 1189.2 | 692.6 | 754.4 | 486.4 | 14/1/0 |
| grid_k24_dense_seed1 | Balanced | 15 | 203.8 | 88.8 | 6.838 | 3.42 | 1552.6 | 682.867 | 624.133 | 315.533 | 15/0/0 |
| grid_k24_dense_seed1 | Speed | 15 | 207.933 | 94.867 | 6.798 | 3.292 | 1583.867 | 727.2 | 647.667 | 333.067 | 15/0/0 |
| grid_k32_sparse_seed1 | Balanced | 15 | 485.0 | 333.4 | 6.829 | 5.258 | 1132.2 | 789.867 | 1020.0 | 730.733 | 15/0/0 |
| grid_k32_sparse_seed1 | Speed | 15 | 484.733 | 344.8 | 7.33 | 5.681 | 1131.667 | 814.933 | 1020.533 | 750.533 | 15/0/0 |
| grid_k32_medium_seed1 | Balanced | 15 | 524.333 | 304.0 | 8.62 | 6.575 | 2042.867 | 1191.733 | 1292.533 | 849.867 | 14/1/0 |
| grid_k32_medium_seed1 | Speed | 15 | 522.533 | 310.533 | 8.521 | 5.665 | 2036.0 | 1216.933 | 1285.0 | 860.733 | 14/1/0 |
| grid_k32_dense_seed1 | Balanced | 15 | 478.733 | 229.0 | 13.965 | 7.946 | 3691.4 | 1791.267 | 1431.4 | 799.133 | 15/0/0 |
| grid_k32_dense_seed1 | Speed | 15 | 475.6 | 230.667 | 13.559 | 7.522 | 3666.6 | 1805.2 | 1446.6 | 809.533 | 15/0/0 |
| grid_k40_sparse_seed1 | Balanced | 15 | 645.867 | 517.0 | 7.192 | 6.507 | 1505.667 | 1208.933 | 1353.6 | 1108.933 | 15/0/0 |
| grid_k40_sparse_seed1 | Speed | 15 | 645.533 | 522.2 | 4.622 | 5.753 | 1504.6 | 1220.933 | 1350.267 | 1113.8 | 15/0/0 |
| grid_k40_medium_seed1 | Balanced | 15 | 729.733 | 449.133 | 7.616 | 5.174 | 2860.4 | 1765.333 | 1800.267 | 1235.467 | 14/1/0 |
| grid_k40_medium_seed1 | Speed | 15 | 731.533 | 461.2 | 6.372 | 4.58 | 2867.267 | 1811.867 | 1792.6 | 1250.4 | 14/1/0 |
| grid_k40_dense_seed1 | Balanced | 15 | 840.133 | 454.6 | 14.382 | 8.311 | 6529.467 | 3563.667 | 2520.8 | 1562.467 | 15/0/0 |
| grid_k40_dense_seed1 | Speed | 15 | 843.933 | 472.8 | 14.592 | 9.045 | 6560.6 | 3704.667 | 2556.067 | 1612.667 | 15/0/0 |
| Circuit 1 - Coastal Loop | Balanced | 12 | 5.333 | 2.583 | 0.082 | 0.053 | 14.083 | 4.75 | 14.75 | 7.667 | 10/2/0 |
| Circuit 1 - Coastal Loop | Speed | 12 | 4.75 | 2.5 | 0.074 | 0.057 | 11.333 | 4.667 | 12.5 | 7.667 | 10/2/0 |
| Circuit 1 - Coastal Loop | Economy | 12 | 5.667 | 2.75 | 0.091 | 0.061 | 14.583 | 5.333 | 15.167 | 8.167 | 10/2/0 |
| Circuit 1 - Coastal Loop | Safety | 12 | 6.917 | 3.75 | 0.119 | 0.077 | 20.0 | 8.917 | 19.667 | 11.167 | 10/2/0 |
| C:\Users\Hafsa\Desktop\5th Semester\DAA Project\smart_racing\tracks\circuit2.json | Balanced | 42 | 22.048 | 12.643 | 0.247 | 0.204 | 50.857 | 29.167 | 48.667 | 30.19 | 40/2/0 |
| C:\Users\Hafsa\Desktop\5th Semester\DAA Project\smart_racing\tracks\circuit2.json | Speed | 42 | 21.929 | 11.643 | 0.315 | 0.256 | 50.524 | 26.833 | 48.143 | 28.357 | 40/2/0 |
| C:\Users\Hafsa\Desktop\5th Semester\DAA Project\smart_racing\tracks\circuit2.json | Economy | 42 | 22.0 | 12.333 | 0.329 | 0.288 | 50.786 | 28.429 | 48.81 | 29.714 | 40/2/0 |
| C:\Users\Hafsa\Desktop\5th Semester\DAA Project\smart_racing\tracks\circuit2.json | Safety | 42 | 21.667 | 17.214 | 0.24 | 0.207 | 50.31 | 40.238 | 48.762 | 40.69 | 38/4/0 |

Chart: exp2_expanded.png.  Raw data: exp2_raw.csv, summary: exp2_summary.csv.

## Verification
On every graph where the A* condition holds (no road shorter than the straight line), Dijkstra and A* returned equal optimal costs for all queries: **YES**.

Stress test (conditions broken on purpose): 124 of the roads are shorter than the straight line. A* returned a more expensive path than Dijkstra on 15 of 40 queries (worst ratio 1.069). Details: exp2_admissibility.csv.

## Interpretation (WRITE THIS YOURSELF after reading your own numbers)
- When does A* expand fewer vertices, and by how much as V grows? When equal or more (look at the last column)?
- Is A*'s lower expansion count also a lower runtime? The heuristic costs time per vertex; compare ms with expanded.
- How do the preset and the density change the benefit? (the heuristic ratio is a lower bound, so a weak bound helps little)
- What happened in the stress test, and why does it show that admissibility matters?

## Limitations
- One machine and interpreter, synthetic grids, a small number of real circuits.
- Expanded counts depend on tie-breaking (insertion order) when costs are equal.
- Costs are random within the stated ranges, so another seed gives different numbers.

## Conclusion (write after the interpretation)
