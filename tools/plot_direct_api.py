"""Render the public figures from the frozen direct-API tables (071749e)."""

import csv
from io import StringIO
from pathlib import Path

import matplotlib as mpl
from matplotlib.figure import Figure

DATA = Path(__file__).resolve().parents[1] / "compiler" / "results" / "direct-api"
PAPER = "#f5f2e9"
INK = "#23374c"
MUTED = "#4e5c68"
BRASS = "#8c581d"
ARMS = (("C1", "CC", BRASS, "-"), ("H", "Hybrid retrieval", INK, "--"))


def rows(filename):
    with (DATA / filename).open() as stream:
        return list(csv.DictReader(stream))


def panel(width=4.4, height=2.45):
    fig = Figure(figsize=(width, height), facecolor=PAPER)
    ax = fig.subplots()
    fig.subplots_adjust(left=.11, right=.96, bottom=.25, top=.83)
    ax.set_facecolor(PAPER)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(length=0, pad=5)
    ax.set_axisbelow(True)
    ax.grid(axis="y", color="#d4cec1", linewidth=.65)
    return fig, ax


def save(fig, name):
    svg = StringIO()
    fig.savefig(svg, format="svg", metadata={"Date": None, "Creator": "Reckoning Machines"})
    lines = [line.rstrip() for line in svg.getvalue().splitlines()]
    (DATA / f"{name}.svg").write_text("\n".join(lines) + "\n", encoding="utf-8")


def frontier():
    points = rows("frontier.csv")
    fig, ax = panel(5.3, 3.25)
    ax.set(xlim=(0, 13500), ylim=(0, 1), xlabel="Provider tokens per attempt")
    ax.set_xticks([0, 3000, 6000, 9000, 12000], ["0", "3,000", "6,000", "9,000", "12,000"])
    ax.set_yticks([0, .25, .5, .75, 1], ["0", "25%", "50%", "75%", "100%"])
    ax.set_title("Fully supported answers", loc="left", pad=10)
    for key, name, color, _ in ARMS:
        series = [r for r in points if r["arm"] == key]
        ax.scatter([float(r["tokens_per_task"]) for r in series],
                   [float(r["supported_rate"]) for r in series],
                   s=42, color=color, marker="o" if key == "C1" else "D", zorder=3)
        point = series[-1]
        ax.annotate(f"{name}  {int(point['correct'])}/48",
                    (float(point["tokens_per_task"]), float(point["supported_rate"])),
                    xytext=(9, 0) if key == "C1" else (0, 10), textcoords="offset points",
                    ha="left" if key == "C1" else "right", color=color, weight="semibold")
    save(fig, "frontier")


def observed():
    fig, ax = panel()
    ledger = rows("modeled-ledger.csv")
    for key, _, color, style in ARMS:
        series = [r for r in ledger if r["arm"] == key]
        ax.step([0] + [int(r["task"]) for r in series],
                [0] + [float(r["cumulative_modeled_usd"]) for r in series],
                where="post", color=color, ls=style)
    ax.set(xlim=(0, 44), ylim=(0, 2.65), xlabel="Observed requests")
    ax.set_xticks([0, 10, 20, 30, 44])
    ax.set_yticks([0, 1, 2], ["$0", "$1", "$2"])
    ax.set_title("Cumulative modeled cost", loc="left", pad=9)
    save(fig, "lifecycle")


def projections():
    for row in rows("task-mixes.csv"):
        fig, ax = panel()
        for key, _, color, style in ARMS:
            rate = float(row["CC_per_task" if key == "C1" else "H_per_task"])
            setup = 50 if key == "C1" else 0
            ax.plot([0, 15000], [setup, setup + 15000 * rate], color=color, ls=style)
        if row["tasks_to_repay_50"]:
            n = int(row["tasks_to_repay_50"])
            ax.scatter(n, n * float(row["H_per_task"]), s=40, facecolor=PAPER,
                       edgecolor=INK, zorder=3)
            ax.annotate(f"{n:,}", (n, n * float(row["H_per_task"])),
                        xytext=(0, 12), textcoords="offset points", ha="center",
                        bbox={"facecolor": PAPER, "edgecolor": "none", "pad": 1})
        ax.set(xlim=(0, 15000), ylim=(0, 510), xlabel="Projected requests")
        ax.set_xticks([0, 5000, 10000, 15000], ["0", "5,000", "10,000", "15,000"])
        ax.set_yticks([0, 125, 250, 375, 500], ["$0", "$125", "$250", "$375", "$500"])
        ax.set_title("Projected cumulative cost", loc="left", pad=9)
        save(fig, row["mix"])


if __name__ == "__main__":
    with mpl.rc_context({"svg.fonttype": "none", "svg.hashsalt": "direct-api",
                         "font.size": 11, "axes.titlesize": 11, "lines.linewidth": 2,
                         "text.color": INK, "axes.labelcolor": MUTED,
                         "ytick.color": MUTED, "xtick.color": MUTED}):
        frontier()
        observed()
        projections()
