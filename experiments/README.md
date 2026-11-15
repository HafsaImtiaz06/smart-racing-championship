# Experiments (Person A: Exp 1 BFS/DFS, Exp 2 Dijkstra/A*)

Run from the project root (the folder with `src` and `tests`), inside your Python environment:

    python experiments/exp1_bfs_dfs.py
    python experiments/exp2_dijkstra_astar.py

Add `--quick` first to check that everything works in a few seconds. Add `--seed N` to try another random graph set.
Results are written to `experiments/results/`. Commit that folder: the spec asks for the raw measurements.

Use the same machine, the same Python and the same power settings for both experiments, close other heavy programs, and
plug in the laptop. Run each experiment once for the report (do not pick the best run).

| File | Content |
|---|---|
| exp1_raw.csv, exp2_raw.csv | every timed call (raw measurements) |
| exp1_summary.csv, exp2_summary.csv | mean, median, standard deviation, counters |
| exp1_verification.csv | correctness checks (BFS minimum edges, DFS components and cycle flag) |
| exp2_admissibility.csv | stress test with A* conditions broken on purpose |
| exp1_runtime.png, exp2_expanded.png | charts |
| exp1_report.md, exp2_report.md | draft report sheets with objective, environment, inputs, procedure, metrics, tables |

The `*_report.md` sheets are auto-filled except for **Interpretation** and **Conclusion**. Write those yourself from your
own numbers (the sheets list the questions to answer), then copy the sheets into the report. Keep theoretical complexity
(O(V+E), O((V+E) log V)) separate from measured runtime, and do not infer a complexity class from a single timing.

Exp 2 also picks up every `tracks/circuit*.json`, so rerun it after Person B and Person C add their circuits.
