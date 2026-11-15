"""Experiment 1: BFS and DFS (Person A).  Run from the project root:
    python experiments/exp1_bfs_dfs.py            full run (a few minutes)
    python experiments/exp1_bfs_dfs.py --quick    tiny run to check that everything works
Outputs go to experiments/results/: exp1_raw.csv, exp1_summary.csv, exp1_verification.csv, exp1_runtime.png, exp1_report.md"""
import argparse, os, random, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import *
from src.routing.api import bfs_order, dfs_order, dfs_analysis, bfs_path


# ---------- independent reference implementations (used ONLY for verification, never timed) ----------
def _adjacency(g):
    adj = {v: [] for v in g.vertices}
    for e in g.edges.values():
        if e.status.value != "Blocked":
            adj[e.from_].append(e.to)
            adj[e.to].append(e.from_)
    return adj


def reference_bfs_levels(g, s):
    adj, level, frontier = _adjacency(g), {s: 0}, [s]
    while frontier:
        nxt = []
        for u in frontier:
            for v in adj[u]:
                if v not in level:
                    level[v] = level[u] + 1
                    nxt.append(v)
        frontier = nxt
    return level


def reference_components(g):
    """Union-find. Returns (list of sorted components, {component root: edge count})."""
    parent = {v: v for v in g.vertices}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    live = [e for e in g.edges.values() if e.status.value != "Blocked"]
    for e in live:
        parent[find(e.from_)] = find(e.to)
    comps, edges = {}, {}
    for v in g.vertices:
        comps.setdefault(find(v), []).append(v)
    for e in live:
        r = find(e.from_)
        edges[r] = edges.get(r, 0) + 1
    return sorted(sorted(c) for c in comps.values()), {find(c[0]): edges.get(find(c[0]), 0) for c in comps.values()}, find


def verify_graph(k, density, seed, rnd):
    """Returns list of (check name, passed, total)."""
    results = []
    g = make_grid_graph(k, density, seed)
    n = len(g.vertices)
    level = reference_bfs_levels(g, 0)
    targets = rnd.sample(range(n), min(25, n))
    ok = sum(1 for t in targets if bfs_path(g, 0, t).found and len(bfs_path(g, 0, t).edges) == level[t])
    results.append(("BFS minimum edge count vs reference BFS", ok, len(targets)))
    # disconnected sections: block 8% of the roads and compare DFS results with union-find
    g2 = make_grid_graph(k, density, seed)
    for eid in rnd.sample(sorted(g2.edges), max(1, int(0.08 * len(g2.edges)))):
        g2.block_edge(eid)
    comps_ref, edge_count, find = reference_components(g2)
    a = dfs_analysis(g2, 0)
    results.append(("DFS components vs union-find (8% roads blocked)", int(a["components"] == comps_ref), 1))
    root = find(0)
    size = next(len(c) for c in comps_ref if 0 in c)
    results.append(("DFS cycle flag vs (edges >= vertices) in the source component",
                    int(a["has_cycle"] == (edge_count[root] >= size)), 1))
    results.append(("DFS visited = size of source component", int(a["visited"] == size), 1))
    return results


def full_analysis(g):
    r = dfs_analysis(g, 0)
    return r["order"], r["examined"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args()
    sizes = [8, 12] if args.quick else [10, 16, 24, 32, 40, 56]
    warmup, repeats = (1, 2) if args.quick else (2, 7)

    raw, summary, verification = [], [], []
    rnd = random.Random(args.seed)
    for k in sizes:
        for density in DENSITIES:
            g = make_grid_graph(k, density, args.seed)
            V, E = len(g.vertices), len(g.edges)
            jobs = {"bfs_traverse": lambda: bfs_order(g, 0),
                    "dfs_traverse": lambda: dfs_order(g, 0),
                    "dfs_analysis_full": lambda: full_analysis(g)}
            for name, fn in jobs.items():
                times, last = time_call(fn, warmup, repeats)
                order, examined = last
                for rep, t in enumerate(times):
                    raw.append([g.name, density, k, V, E, name, rep + 1, round(t, 4), len(order), examined])
                mean, median, sd = summarize(times)
                summary.append([g.name, density, k, V, E, V + E, name, round(mean, 4), round(median, 4), round(sd, 4),
                                len(order), examined, round(mean * 1000.0 / (V + E), 4)])
            for check, ok, total in verify_graph(k, density, args.seed, rnd):
                verification.append([g.name, check, ok, total])
            print("done k=%d %s (V=%d, E=%d)" % (k, density, V, E))

    head_raw = ["graph", "density", "k", "V", "E", "algorithm", "repeat", "runtime_ms", "visited", "examined"]
    head_sum = ["graph", "density", "k", "V", "E", "V+E", "algorithm", "mean_ms", "median_ms", "stdev_ms",
                "visited", "examined", "us_per_(V+E)"]
    write_csv(os.path.join(RESULTS, "exp1_raw.csv"), head_raw, raw)
    write_csv(os.path.join(RESULTS, "exp1_summary.csv"), head_sum, summary)
    write_csv(os.path.join(RESULTS, "exp1_verification.csv"), ["graph", "check", "passed", "total"], verification)

    plt = pyplot()
    if plt:
        fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
        marks = {"sparse": "o", "medium": "s", "dense": "^"}
        colors = {"bfs_traverse": "#1f77b4", "dfs_traverse": "#d62728", "dfs_analysis_full": "#2ca02c"}
        for alg in colors:
            for d in DENSITIES:
                pts = [r for r in summary if r[6] == alg and r[1] == d]
                axes[0].plot([r[5] for r in pts], [r[7] for r in pts], marks[d] + "-", color=colors[alg],
                             alpha=0.8, label="%s, %s" % (alg, d))
                axes[1].plot([r[5] for r in pts], [r[12] for r in pts], marks[d] + "-", color=colors[alg], alpha=0.8)
        axes[0].set_xlabel("V + E"); axes[0].set_ylabel("mean runtime (ms)"); axes[0].set_title("Runtime vs V+E")
        axes[1].set_xlabel("V + E"); axes[1].set_ylabel("microseconds per (V+E)")
        axes[1].set_title("Runtime per unit of V+E (flat line = linear growth)")
        axes[0].legend(fontsize=6)
        fig.tight_layout()
        fig.savefig(os.path.join(RESULTS, "exp1_runtime.png"), dpi=130)

    passed = sum(r[2] for r in verification)
    total = sum(r[3] for r in verification)
    table_rows = [[r[1], r[3], r[4], r[6], r[7], r[8], r[9], r[10], r[11], r[12]] for r in summary]
    md = ["# Experiment 1 - BFS and DFS (draft sheet, auto-generated)", "",
          "## Objective", "Measure runtime, visited vertices and examined edges of BFS and DFS on sparse, medium and dense "
          "road networks of growing size, verify correctness, and compare the observed growth with the theoretical O(V+E).", "",
          "## Environment", env_text(), "",
          "Timing includes the data structures each call allocates (visited set, queue/stack, order list). It excludes "
          "building the graph, rendering and file I/O. Correctness checks run separately, never inside a timed call.", "",
          "## Input generation", "Jittered k x k grid networks built by `make_grid_graph` (see its docstring: coordinates, "
          "road rules, cost ranges). Seed = %d. sparse = spanning tree + 15%% extra roads, medium = grid, dense = grid + diagonals." % args.seed, "",
          "## Dataset sizes", "k = %s, so V = %s." % (sizes, [k * k for k in sizes]), "",
          "## Procedure", "For every graph: %d warm-up calls, then %d timed calls of: bfs_traverse (full BFS from vertex 0), "
          "dfs_traverse (full DFS from vertex 0) and dfs_analysis_full (DFS + cycle detection + components + dead ends). "
          "Mean, median and standard deviation of the timed calls are reported." % (warmup, repeats), "",
          "## Metrics", "runtime (ms), visited vertices, examined edges (directed arcs looked at), microseconds per (V+E).", "",
          "## Results", md_table(["graph", "V", "E", "algorithm", "mean ms", "median ms", "stdev ms", "visited", "examined",
                                  "us per (V+E)"], table_rows), "",
          "Chart: exp1_runtime.png.  Raw data: exp1_raw.csv.", "",
          "## Verification", "%d of %d checks passed (details in exp1_verification.csv): BFS minimum edge count against a "
          "separate reference BFS, DFS components against union-find, DFS cycle flag against the edges >= vertices test." % (passed, total), "",
          "## Interpretation (WRITE THIS YOURSELF after reading your own numbers)",
          "- Do visited and examined counts match the theory? (visited = reachable vertices; examined = sum of degrees = 2E for two-way roads)",
          "- Does microseconds per (V+E) stay roughly flat as V+E grows? If yes, growth is consistent with O(V+E); one run alone does not prove it.",
          "- Compare BFS with DFS traversal, and traversal with the full analysis (which does extra passes).",
          "- Compare sparse, medium and dense at the same V.", "",
          "## Limitations", "- One machine, one interpreter (CPython), one seed, grid-like graphs only.",
          "- Python timings include interpreter overhead and can vary with background load.",
          "- Real circuits are tiny; the large graphs are synthetic.", "",
          "## Conclusion (write after the interpretation)", ""]
    with open(os.path.join(RESULTS, "exp1_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print("verification: %d/%d passed" % (passed, total))
    print("results written to", RESULTS)


if __name__ == "__main__":
    main()
