"""Draw circuits as PNG pictures straight from their JSON files (needs matplotlib).
Run from the project root:
    python tracks/draw_circuit.py                       draws every tracks/circuit*.json
    python tracks/draw_circuit.py tracks/circuit1.json  draws just that one
The picture is saved next to the JSON file, e.g. tracks/circuit1_preview.png"""
import glob, json, os, sys

COLORS = {"Start": "#2ca02c", "Finish": "#000000", "Checkpoint": "#ff7f0e", "Intersection": "#aaaaaa",
          "FuelStation": "#9467bd", "NitroPickup": "#17becf", "DeadEnd": "#8c564b"}


def draw(json_path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    verts = {v["id"]: v for v in data["vertices"]}
    fig, ax = plt.subplots(figsize=(13, 8.6))
    for e in data["edges"]:
        a, b = verts[e["from"]], verts[e["to"]]
        fast = e["baseTime"] / max(e["distance"], 1e-9) < 0.03
        color = "#d62728" if e.get("isShortcut") else "#1f77b4" if fast else "#7f7f7f"
        width = 3.2 if e.get("isShortcut") else 2
        arrow = dict(arrowstyle="-|>", mutation_scale=22, shrinkA=9, shrinkB=9) if e.get("directed") \
            else dict(arrowstyle="-", shrinkA=0, shrinkB=0)
        ax.annotate("", xy=(b["x"], b["y"]), xytext=(a["x"], a["y"]),
                    arrowprops=dict(color=color, lw=width, **arrow))
    for v in verts.values():
        ax.scatter(v["x"], v["y"], s=170, c=COLORS.get(v["type"], "#aaaaaa"), zorder=3, edgecolors="white")
        label = "CP%d" % v["checkpointOrder"] if v.get("checkpointOrder") else v.get("name", str(v["id"]))
        ax.text(v["x"] + 8, v["y"] - 12, label, fontsize=8, zorder=4)
    ax.invert_yaxis()
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(data.get("name", os.path.basename(json_path)))
    legend = [Line2D([0], [0], color="#d62728", lw=3, label="shortcut (arrow = one-way)"),
              Line2D([0], [0], color="#1f77b4", lw=2, label="fast road"),
              Line2D([0], [0], color="#7f7f7f", lw=2, label="other road")]
    legend += [Line2D([0], [0], marker="o", color="w", markerfacecolor=c, markersize=9, label=t)
               for t, c in COLORS.items()]
    ax.legend(handles=legend, loc="lower center", ncol=5, fontsize=8, frameon=False, bbox_to_anchor=(0.5, -0.06))
    out = os.path.splitext(json_path)[0] + "_preview.png"
    fig.savefig(out, dpi=110, bbox_inches="tight")
    plt.close(fig)
    return out


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    paths = sys.argv[1:] or sorted(glob.glob(os.path.join(here, "circuit*.json")))
    if not paths:
        sys.exit("no circuit*.json found")
    for p in paths:
        print("saved", draw(p))