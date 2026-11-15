"""Shared helpers for the experiments (Person A: Exp 1 and Exp 2). Keep timing and correctness checks separate."""
import csv, datetime, gc, math, os, platform, random, statistics, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from src.core.graph import Graph
from src.core.models import Vertex, Edge, VertexType

RESULTS = os.path.join(ROOT, "experiments", "results")
DENSITIES = ("sparse", "medium", "dense")


def make_grid_graph(k, density, seed, express_frac=0.0):
    """Reproducible test road network on a jittered k x k grid (V = k*k).
    Coordinates: column*20 + U(-5,5), row*20 + U(-5,5).   Roads (all two-way, all open):
      sparse : random spanning tree of the grid + 15% of the remaining grid roads      (average degree about 2.3)
      medium : every horizontal/vertical grid road                                      (average degree about 4)
      dense  : grid roads + both diagonals                                              (average degree about 8)
    Edge attributes: distance = straight line x U(1.00, 1.25); baseTime = distance x U(0.02, 0.05);
    fuelCost = distance x U(0.03, 0.06); difficulty from [1,1,2,2,3,4,5].
    express_frac > 0 turns that share of roads into 'express lanes' whose distance is only 0.2 x the straight line
    (this BREAKS A* admissibility on purpose, for the stress test)."""
    rnd = random.Random("%d|%s|%d" % (k, density, seed))
    g = Graph("grid_k%d_%s_seed%d" % (k, density, seed))
    for r in range(k):
        for c in range(k):
            g.add_vertex(Vertex(r * k + c, c * 20.0 + rnd.uniform(-5, 5), r * 20.0 + rnd.uniform(-5, 5),
                                VertexType.INTERSECTION))
    cand = []
    for r in range(k):
        for c in range(k):
            u = r * k + c
            if c + 1 < k:
                cand.append((u, u + 1))
            if r + 1 < k:
                cand.append((u, u + k))
            if density == "dense":
                if r + 1 < k and c + 1 < k:
                    cand.append((u, u + k + 1))
                if r + 1 < k and c - 1 >= 0:
                    cand.append((u, u + k - 1))
    if density == "sparse":
        order = cand[:]
        rnd.shuffle(order)
        parent = list(range(k * k))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        tree, rest = [], []
        for a, b in order:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb
                tree.append((a, b))
            else:
                rest.append((a, b))
        cand = tree + rest[:int(0.15 * len(rest))]
    for eid, (a, b) in enumerate(cand):
        va, vb = g.vertices[a], g.vertices[b]
        straight = math.hypot(va.x - vb.x, va.y - vb.y)
        dist = straight * rnd.uniform(1.0, 1.25)
        if express_frac and rnd.random() < express_frac:
            dist = straight * 0.2
        g.add_edge(Edge(eid, a, b, dist, dist * rnd.uniform(0.02, 0.05), dist * rnd.uniform(0.03, 0.06),
                        rnd.choice([1, 1, 2, 2, 3, 4, 5])))
    g.finalize()
    return g


def time_call(fn, warmup, repeats):
    """Run fn warmup times (untimed), then repeats times (timed). Returns (list of ms, result of last run)."""
    for _ in range(warmup):
        fn()
    gc.collect()
    times, last = [], None
    for _ in range(repeats):
        t0 = time.perf_counter()
        last = fn()
        times.append((time.perf_counter() - t0) * 1000.0)
    return times, last


def summarize(xs):
    return (statistics.mean(xs), statistics.median(xs), statistics.stdev(xs) if len(xs) > 1 else 0.0)


def write_csv(path, header, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def env_info():
    return {"date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "python": sys.version.split()[0], "implementation": platform.python_implementation(),
            "os": platform.platform(), "machine": platform.machine(), "processor": platform.processor() or "unknown",
            "cpu_count": os.cpu_count()}


def env_text():
    e = env_info()
    return ("Date: %(date)s | Python %(python)s (%(implementation)s) | OS: %(os)s | CPU: %(processor)s, %(machine)s, "
            "%(cpu_count)s logical cores" % e)


def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def pyplot():
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        return plt
    except Exception as ex:                         # matplotlib missing or blocked: skip charts, keep the data
        print("charts skipped (matplotlib unavailable):", ex)
        return None
