"""Rebuild the public figure with Python and Matplotlib 3.11.2."""

from io import StringIO
from pathlib import Path

import matplotlib as mpl
from matplotlib.figure import Figure


# Public aggregate counts. Columns: budget, Hybrid RAG, Context Compiler.
ROWS = ((600, 1, 2), (900, 2, 3), (1200, 2, 3), (1800, 3, 4))
OUTPUT = Path(__file__).resolve().parents[1] / "compiler" / "evidence-sufficiency.svg"


def main():
    budgets, retrieval, compiler = zip(*ROWS)
    ink, brass, muted = "#e9edf3", "#d9c9a3", "#a3afc0"
    with mpl.rc_context({
        "svg.hashsalt": "evidence-sufficiency", "svg.fonttype": "none",
        "font.size": 11, "text.color": ink, "axes.labelcolor": ink,
        "xtick.color": muted, "ytick.color": muted,
    }):
        fig = Figure(figsize=(4.7, 3.15))
        ax = fig.subplots()
        fig.subplots_adjust(left=.075, right=.94, bottom=.20, top=.84)
        ax.plot(budgets, compiler, "o-", color=brass, label="Context Compiler")
        ax.plot(budgets, retrieval, "s--", color=ink, label="Hybrid RAG")
        ax.set_xlim(570, 1830)
        ax.set_ylim(0, 5)
        ax.set_xticks(budgets, [f"{n:,}" for n in budgets])
        ax.set_yticks(range(6))
        ax.set_xlabel("Context budget (tokens)", labelpad=7)
        ax.set_ylabel("Questions with all required evidence (out of 5)",
                      rotation=0, ha="left", va="bottom")
        ax.yaxis.set_label_coords(0, 1.08)
        ax.tick_params(length=0, pad=5)
        ax.set_axisbelow(True)
        ax.grid(axis="y", color="#394557", linewidth=.6)
        ax.spines[:].set_visible(False)
        ax.legend(loc="upper left", ncols=2, frameon=False, fontsize=10,
                  handlelength=1.8, borderaxespad=.15)
        svg = StringIO()
        fig.savefig(svg, format="svg", transparent=True,
                    metadata={"Date": None, "Creator": "Reckoning Machines"})
        OUTPUT.write_text("".join(line.rstrip() + "\n" for line in svg.getvalue().splitlines()), encoding="utf-8")


if __name__ == "__main__":
    main()
