"""Experiment 2: Dijkstra and A* (Person A).  Run from the project root:
    python experiments/exp2_dijkstra_astar.py            full run (a few minutes)
    python experiments/exp2_dijkstra_astar.py --quick    tiny run to check that everything works
Uses synthetic grid networks AND every tracks/circuit*.json that exists.
Outputs in experiments/results/: exp2_raw.csv, exp2_summary.csv, exp2_admissibility.csv, exp2_expanded.png, exp2_report.md"""
import argparse, glob, os, random, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import *
from src.core.track_io import load_track
from src.routing.api import dijkstra, astar

PRESETS = ("Balanced", "Speed")


def query_pairs(g, count, rnd):
    ids = sorted(g.vertices)
    pairs = [(ids[0], ids[-1])]                           # always include the far corner pair
    while len(pairs) < count:
        s, t = rnd.sample(ids, 2)
        pairs.append((s, t))
    return pairs


def circuit_pairs(g):
    cps = g.checkpoints_in_order()
    legs = list(zip([g.start_vertex()] + cps, cps + [g.finish_vertex()]))
    return legs + [(g.start_vertex(), g.finish_vertex())]


def same_cost(a, b):
    return a.found == b.found and (not a.found or abs(a.cost - b.cost) <= 1e-9 * max(1.0, abs(b.cost)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args()
    sizes = [8, 12] if args.quick else [10, 16, 24, 32, 40]
    pairs_per_graph = 4 if args.quick else 15
    warmup, repeats = (1, 2) if args.quick else (1, 5)
    rnd = random.Random(args.seed)

    cases = []                                            # (graph, family, list of pairs)
    for k in sizes:
        for density in DENSITIES:
            g = make_grid_graph(k, density, args.seed)
            cases.append((g, density, query_pairs(g, pairs_per_graph, rnd)))
    for path in sorted(glob.glob(os.path.join(ROOT, "tracks", "circuit*.json"))):
        g = load_track(path)
        cases.append((g, "circuit", circuit_pairs(g)))

    raw, per_query = [], []
    for g, family, pairs in cases:
        V, E = len(g.vertices), len(g.edges)
        bad_geometry = len(g.validate_geometry())
        presets = PRESETS if family != "circuit" else tuple(("Balanced", "Speed", "Economy", "Safety"))
        for preset in presets:
            for pid, (s, t) in enumerate(pairs):
                results = {}
                for name, fn in (("dijkstra", dijkstra), ("astar", astar)):
                    times, res = time_call(lambda: fn(g, s, t, preset), warmup, repeats)
                    results[name] = (res, summarize(times)[0])
                    for rep, tm in enumerate(times):
                        raw.append([g.name, family, V, E, preset, pid, s, t, name, rep + 1, round(tm, 4),
                                    res.expanded, res.relaxed, res.heap_ops, round(res.cost, 9), int(res.found)])
                d, a = results["dijkstra"][0], results["astar"][0]
                per_query.append([g.name, family, V, E, preset, pid, bad_geometry, results["dijkstra"][1], results["astar"][1],
                                  d.expanded, a.expanded, d.relaxed, a.relaxed, d.heap_ops, a.heap_ops,
                                  int(same_cost(a, d)), int(d.found)])
        print("done", g.name, "(V=%d, E=%d)" % (V, E))

    head_raw = ["graph", "family", "V", "E", "preset", "pair", "source", "target", "algorithm", "repeat", "runtime_ms",
                "expanded", "relaxed", "heap_ops", "cost", "found"]
    write_csv(os.path.join(RESULTS, "exp2_raw.csv"), head_raw, raw)

    # ---- summary per (graph, preset) ----
    groups = {}
    for r in per_query:
        groups.setdefault((r[0], r[1], r[2], r[3], r[4], r[6]), []).append(r)
    summary = []
    for (name, family, V, E, preset, bad), rows in groups.items():
        n = len(rows)
        mean = lambda i: round(sum(x[i] for x in rows) / n, 3)
        fewer = sum(1 for x in rows if x[10] < x[9])
        equal = sum(1 for x in rows if x[10] == x[9])
        more = sum(1 for x in rows if x[10] > x[9])
        summary.append([name, family, V, E, preset, n, bad, mean(7), mean(8), mean(9), mean(10), mean(11), mean(12),
                        mean(13), mean(14), sum(x[15] for x in rows), fewer, equal, more])
    head_sum = ["graph", "family", "V", "E", "preset", "queries", "edges_breaking_geometry", "dijkstra_ms", "astar_ms",
                "dijkstra_expanded", "astar_expanded", "dijkstra_relaxed", "astar_relaxed", "dijkstra_heap_ops",
                "astar_heap_ops", "equal_cost_queries", "astar_fewer", "astar_equal", "astar_more"]
    write_csv(os.path.join(RESULTS, "exp2_summary.csv"), head_sum, summary)

    # ---- stress test: break admissibility on purpose ----
    k = 12 if args.quick else 24
    sg = make_grid_graph(k, "medium", args.seed, express_frac=0.10)
    violating = len(sg.validate_geometry())
    stress, worse, worst = [], 0, 1.0
    for pid, (s, t) in enumerate(query_pairs(sg, 10 if args.quick else 40, random.Random(args.seed + 1))):
        d, a = dijkstra(sg, s, t, "Balanced"), astar(sg, s, t, "Balanced")
        ratio = a.cost / d.cost if d.found and d.cost > 0 else 1.0
        worse += int(ratio > 1 + 1e-9)
        worst = max(worst, ratio)
        stress.append([sg.name, violating, pid, s, t, round(d.cost, 9), round(a.cost, 9), round(ratio, 6),
                       d.expanded, a.expanded])
    write_csv(os.path.join(RESULTS, "exp2_admissibility.csv"),
              ["graph", "edges_shorter_than_straight_line", "pair", "source", "target", "dijkstra_cost", "astar_cost",
               "astar_cost/dijkstra_cost", "dijkstra_expanded", "astar_expanded"], stress)

    plt = pyplot()
    if plt:
        fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
        for d_, mk in (("sparse", "o"), ("medium", "s"), ("dense", "^")):
            pts = sorted([r for r in summary if r[1] == d_ and r[4] == "Balanced"], key=lambda r: r[2])
            axes[0].plot([r[2] for r in pts], [r[9] for r in pts], mk + "-", color="#1f77b4", label="Dijkstra, " + d_)
            axes[0].plot([r[2] for r in pts], [r[10] for r in pts], mk + "--", color="#d62728", label="A*, " + d_)
            axes[1].plot([r[2] for r in pts], [r[7] for r in pts], mk + "-", color="#1f77b4", label="Dijkstra, " + d_)
            axes[1].plot([r[2] for r in pts], [r[8] for r in pts], mk + "--", color="#d62728", label="A*, " + d_)
        axes[0].set_xlabel("V"); axes[0].set_ylabel("mean expanded vertices"); axes[0].set_title("Expanded vertices (Balanced)")
        axes[1].set_xlabel("V"); axes[1].set_ylabel("mean runtime per query (ms)"); axes[1].set_title("Runtime (Balanced)")
        axes[0].legend(fontsize=7)
        fig.tight_layout()
        fig.savefig(os.path.join(RESULTS, "exp2_expanded.png"), dpi=130)

    ok_conditions = [r for r in summary if r[6] == 0]
    all_equal = all(r[15] == r[5] for r in ok_conditions)
    rows_md = [[r[0], r[4], r[5], r[9], r[10], r[7], r[8], r[11], r[12], r[13], r[14], "%d/%d/%d" % (r[16], r[17], r[18])]
               for r in summary]
    md = ["# Experiment 2 - Dijkstra and A* (draft sheet, auto-generated)", "",
          "## Objective", "Compare Dijkstra and A* on the same road networks and queries: runtime, expanded vertices, "
          "relaxed edges, heap operations and final path cost; verify equal optimal costs when the A* conditions hold; "
          "find cases where A* expands fewer, equal or more vertices.", "",
          "## Environment", env_text(), "",
          "Timing includes the heap, the distance/parent tables and building the returned path (cost, distance, time, fuel sums). "
          "It excludes graph construction, rendering and file I/O. Correctness checks run separately from the timed calls.", "",
          "## Input generation", "Synthetic jittered-grid networks from `make_grid_graph` (coordinates and cost ranges in its docstring), "
          "seed %d, plus every tracks/circuit*.json present (checkpoint-to-checkpoint legs and Start to Finish). Query pairs: the far "
          "corner pair plus random pairs. Presets: %s on grids, all four on circuits. A* heuristic = Graph.heuristic_ratio(preset) x "
          "straight-line distance; it is admissible when no road is shorter than the straight line (Graph.validate_geometry() == [])." % (args.seed, ", ".join(PRESETS)), "",
          "## Dataset sizes", "grid k = %s (V = %s), %d queries per graph and preset." % (sizes, [k * k for k in sizes], pairs_per_graph), "",
          "## Procedure", "For each query: %d warm-up call(s), then %d timed calls of each algorithm. Counters (expanded, relaxed, heap "
          "operations) and cost come from the last call; they are the same every run." % (warmup, repeats), "",
          "## Metrics", "runtime (ms), expanded vertices, relaxed edges, heap operations (pushes + pops), final path cost.", "",
          "## Results (means over the queries of each graph and preset; last column = queries where A* expanded fewer/equal/more)",
          md_table(["graph", "preset", "queries", "Dij expanded", "A* expanded", "Dij ms", "A* ms", "Dij relaxed", "A* relaxed",
                    "Dij heap ops", "A* heap ops", "A* fewer/equal/more"], rows_md), "",
          "Chart: exp2_expanded.png.  Raw data: exp2_raw.csv, summary: exp2_summary.csv.", "",
          "## Verification", "On every graph where the A* condition holds (no road shorter than the straight line), Dijkstra and A* returned "
          "equal optimal costs for all queries: **%s**." % ("YES" if all_equal else "NO - investigate"), "",
          "Stress test (conditions broken on purpose): %d of the roads are shorter than the straight line. A* returned a more expensive path "
          "than Dijkstra on %d of %d queries (worst ratio %.3f). Details: exp2_admissibility.csv." % (violating, worse, len(stress), worst), "",
          "## Interpretation (WRITE THIS YOURSELF after reading your own numbers)",
          "- When does A* expand fewer vertices, and by how much as V grows? When equal or more (look at the last column)?",
          "- Is A*'s lower expansion count also a lower runtime? The heuristic costs time per vertex; compare ms with expanded.",
          "- How do the preset and the density change the benefit? (the heuristic ratio is a lower bound, so a weak bound helps little)",
          "- What happened in the stress test, and why does it show that admissibility matters?", "",
          "## Limitations", "- One machine and interpreter, synthetic grids, a small number of real circuits.",
          "- Expanded counts depend on tie-breaking (insertion order) when costs are equal.",
          "- Costs are random within the stated ranges, so another seed gives different numbers.", "",
          "## Conclusion (write after the interpretation)", ""]
    with open(os.path.join(RESULTS, "exp2_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print("equal optimal costs where conditions hold:", all_equal)
    print("stress test: A* worse on %d of %d queries (worst ratio %.3f)" % (worse, len(stress), worst))
    print("results written to", RESULTS)


if __name__ == "__main__":
    main()
