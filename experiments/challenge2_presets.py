"""Challenge 2 - multi-objective route planning (Person A).  Run from the project root:
    python experiments/challenge2_presets.py [tracks/circuit1.json]      (add --quick for a fast check)
Shows (1) what each preset chooses and what its route costs under the OTHER presets, (2) how a weight sweep changes
the chosen route, (3) routes that are Pareto-optimal yet never chosen by any weights, (4) how the choice depends on the
normalization constants. Output: experiments/results/challenge2_*.csv, challenge2_weights.png, challenge2_report.md"""
import argparse, os, random, sys
sys.path.insert(0, os.path.dirname(__file__))
import common
from common import ROOT, md_table, write_csv, pyplot, env_text
from src.core import constants as K
from src.core.models import EdgeStatus
from src.core.track_io import load_track
from src.routing.api import plan_route, route_vertices, route_edges, alternative_routes

TERMS = ("D", "T", "F", "R", "O")          # distance, time, fuel, road difficulty, obstacle penalty


def edge_terms(g, e):
    """Normalized terms of one road, exactly as Graph.edge_cost uses them."""
    return (e.distance / g.d_ref, g.effective_time(e) / g.t_ref, g.effective_fuel(e) / g.f_ref,
            (g.effective_difficulty(e) - 1) / 4.0, g.obstacle_penalty(e))


def route_terms(g, edge_ids):
    sums = [0.0] * 5
    for eid in edge_ids:
        for i, v in enumerate(edge_terms(g, g.edges[eid])):
            sums[i] += v
    return tuple(sums)


def raw_metrics(g, edge_ids):
    es = [g.edges[e] for e in edge_ids]
    return (sum(e.distance for e in es), sum(g.effective_time(e) for e in es), sum(g.effective_fuel(e) for e in es))


def edges_of(g, vertices):
    out = []
    for a, b in zip(vertices, vertices[1:]):
        out.append(min(e.id for e, v in g.neighbors(a) if v == b))
    return out


def dot(w, terms):
    return sum(x * y for x, y in zip(w, terms))


def lap_plan(g, preset):
    return plan_route(g, g.start_vertex(), g.checkpoints_in_order(), g.finish_vertex(), preset)


def with_weights(weights, fn):
    """Run fn(preset_name) with a temporary preset holding `weights` (a unique name, so cached heuristics stay valid)."""
    name = "sweep_%d" % len(K.PRESETS)
    K.PRESETS[name] = tuple(weights)
    try:
        return fn(name)
    finally:
        del K.PRESETS[name]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("track", nargs="?", default=os.path.join(ROOT, "tracks", "circuit1.json"))
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--out", default=common.RESULTS)
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args(argv)
    g = load_track(args.track)
    out = args.out
    names = list(K.PRESETS)

    # ---------- (1) presets: chosen routes and cross-evaluation ----------
    routes, rows_a = {}, []
    for p in names:
        plan = lap_plan(g, p)
        eds = route_edges(plan)
        routes[p] = (route_vertices(plan), eds)
        d, t, f = raw_metrics(g, eds)
        rows_a.append([p, len(eds), round(d, 1), round(t, 1), round(f, 1), round(plan.cost, 4)])
    own = {q: dot(K.PRESETS[q], route_terms(g, routes[q][1])) for q in names}
    cross = []
    for p in names:
        terms = route_terms(g, routes[p][1])
        cross.append([p] + ["%.3f (+%.1f%%)" % (dot(K.PRESETS[q], terms), (dot(K.PRESETS[q], terms) / own[q] - 1) * 100.0)
                            if own[q] > 0 else "n/a" for q in names])
    write_csv(os.path.join(out, "challenge2_lap_presets.csv"),
              ["preset", "roads", "distance", "time_s", "fuel", "cost_under_own_preset"], rows_a)
    write_csv(os.path.join(out, "challenge2_cross_cost.csv"),
              ["route chosen by \\ cost under"] + names, cross)
    distinct = len({tuple(v[1]) for v in routes.values()})

    # ---------- (2) weight sweep on the time weight ----------
    base = K.PRESETS["Balanced"]                      # (w_d, w_t, w_f, w_r, w_o)
    others = [base[0], base[2], base[3], base[4]]
    step = 0.25 if args.quick else 0.05
    sweep, labels, switches, prev = [], {}, [], None
    n = int(round(1 / step))
    for i in range(n + 1):
        wt = i * step
        scale = (1 - wt) / sum(others)
        w = (others[0] * scale, wt, others[1] * scale, others[2] * scale, others[3] * scale)
        plan = with_weights(w, lambda name: lap_plan(g, name))
        eds = tuple(route_edges(plan))
        label = labels.setdefault(eds, "route %s" % chr(ord("A") + len(labels)))
        d, t, f = raw_metrics(g, eds)
        sweep.append([round(wt, 2), label, round(d, 1), round(t, 1), round(f, 1)])
        if prev is not None and label != prev:
            switches.append((round(wt, 2), label))
        prev = label
    write_csv(os.path.join(out, "challenge2_weight_sweep.csv"),
              ["time_weight", "chosen_route", "distance", "time_s", "fuel"], sweep)

    # ---------- (3) Pareto analysis on one leg (complete enumeration of simple routes) ----------
    cps = g.checkpoints_in_order()
    legs = list(zip([g.start_vertex()] + cps, cps + [g.finish_vertex()]))
    limit = 400 if args.quick else 1500
    best = None                                   # (Pareto size, routes enumerated, leg, routes, vectors, front)
    for a, b in legs:
        rs = alternative_routes(g, a, b, max_routes=limit, max_len=12, max_expansions=3_000_000)
        if len(rs) >= limit or len(rs) < 2:       # skip legs whose enumeration is not complete
            continue
        vs = [route_terms(g, edges_of(g, r)) for r in rs]
        fr = [i for i in range(len(vs)) if not any(all(vs[j][k] <= vs[i][k] for k in range(5)) and
                                                    any(vs[j][k] < vs[i][k] for k in range(5)) for j in range(len(vs)))]
        if best is None or (len(fr), len(rs)) > (best[0], best[1]):
            best = (len(fr), len(rs), (a, b), rs, vs, fr)
    best_leg = best[2] if best else None
    pareto_text = "no leg with a complete enumeration under the limit"
    pareto_rows = []
    if best_leg:
        best_routes, vecs, front = best[3], best[4], best[5]
        n_r = len(vecs)
        rnd = random.Random(args.seed)
        winners = set()
        for w in list(K.PRESETS.values()) + [tuple(rnd.expovariate(1.0) for _ in range(5)) for _ in range(300 if args.quick else 5000)]:
            winners.add(min(range(n_r), key=lambda i: (dot(w, vecs[i]), i)))
        preset_winners = {p: min(range(n_r), key=lambda i: (dot(K.PRESETS[p], vecs[i]), i)) for p in names}
        never = [i for i in front if i not in winners]
        pareto_rows = [["leg", "%d -> %d" % best_leg], ["simple routes enumerated (complete, max 12 roads)", n_r],
                       ["Pareto-optimal routes (5 objectives)", len(front)],
                       ["Pareto routes chosen by some sampled weights", len(front) - len(never)],
                       ["Pareto routes never chosen by any sampled weights", len(never)],
                       ["distinct routes chosen by the 4 presets", len(set(preset_winners.values()))]]
        write_csv(os.path.join(out, "challenge2_pareto.csv"), ["quantity", "value"], pareto_rows)
        pareto_text = "see table"

    # ---------- (4) sensitivity to normalization constants ----------
    norm_rows, base_route = [], None
    t_ref0 = g.t_ref
    try:
        for m in (0.25, 0.5, 1.0, 2.0, 4.0):
            g.t_ref = t_ref0 * m
            g._ratio_cache.clear()
            plan = lap_plan(g, "Balanced")
            eds = tuple(route_edges(plan))
            base_route = base_route if base_route is not None else None
            d, t, f = raw_metrics(g, eds)
            norm_rows.append([m, len(eds), round(d, 1), round(t, 1), round(f, 1), hash(eds) % 100000])
    finally:
        g.t_ref = t_ref0
        g._ratio_cache.clear()
    sig = {}
    for r in norm_rows:
        r[-1] = sig.setdefault(r[-1], "route %s" % chr(ord("A") + len(sig)))
    write_csv(os.path.join(out, "challenge2_normalization.csv"),
              ["T_ref multiplier", "roads", "distance", "time_s", "fuel", "route"], norm_rows)

    plt = pyplot()
    if plt:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        xs = [r[0] for r in sweep]
        ax.plot(xs, [r[3] for r in sweep], "o-", color="#1f77b4", label="lap time (s)")
        ax2 = ax.twinx()
        ax2.plot(xs, [r[4] for r in sweep], "s--", color="#d62728", label="fuel")
        ax.set_xlabel("weight on time (other weights scaled to keep the sum 1)")
        ax.set_ylabel("lap time (s)")
        ax2.set_ylabel("fuel")
        ax.set_title("Chosen route changes as the time weight grows")
        fig.legend(loc="upper center", ncol=2, fontsize=8)
        fig.tight_layout()
        fig.savefig(os.path.join(out, "challenge2_weights.png"), dpi=130)
        plt.close(fig)

    md = ["# Challenge 2 - Multi-objective route planning (draft sheet, auto-generated)", "",
          "Circuit: %s. Lap = Start -> checkpoints 1..10 in order -> Finish. %s" % (g.name, env_text()), "",
          "## 1. What each preset chooses (whole lap)", md_table(["preset", "roads", "distance", "time s", "fuel", "cost (own preset)"], rows_a), "",
          "%d distinct routes among the %d presets." % (distinct, len(names)), "",
          "## 2. Cost of each preset's route under every preset's weights (percent above the best route for that column)",
          md_table(["route chosen by \\ cost under"] + names, cross), "",
          "## 3. Weight sweep: time weight from 0 to 1, other weights scaled to keep the sum at 1",
          "Chosen routes in order: %s. Switch points: %s." % (", ".join(sorted(set(labels.values()))),
                                                              "; ".join("%s at w_t = %.2f" % (l, w) for w, l in switches) or "none"),
          md_table(["w_t", "route", "distance", "time s", "fuel"], sweep), "Chart: challenge2_weights.png", "",
          "## 4. Pareto analysis of one leg (all simple routes up to 12 roads)",
          md_table(["quantity", "value"], pareto_rows) if pareto_rows else pareto_text,
          "Sampling many random weight vectors cannot prove that a Pareto route is unreachable, but a route that is never chosen "
          "after thousands of samples is a strong sign of an unsupported (non-convex) trade-off.", "",
          "## 5. Sensitivity to the normalization constant T_ref (Balanced preset)",
          md_table(["T_ref x", "roads", "distance", "time s", "fuel", "route"], norm_rows), "",
          "## Discussion points to write yourself from these tables",
          "- Why one scalar cost hides trade-offs (a route can be cheap overall yet bad on one objective; section 2 shows the regret).",
          "- Why the weights and the normalization constants are arbitrary choices that change the answer (sections 3 and 5).",
          "- Why weighted sums cannot reach every Pareto-optimal route (section 4), and what a Pareto-front presentation would add.",
          "- How the game uses the presets: the player picks the trade-off; the planner optimizes exactly the scalar cost it displays.", ""]
    with open(os.path.join(out, "challenge2_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print("distinct preset routes:", distinct, "| sweep switches:", switches)
    if pareto_rows:
        print({r[0]: r[1] for r in pareto_rows})
    print("normalization routes:", [r[-1] for r in norm_rows])
    print("results written to", out)


if __name__ == "__main__":
    main()
