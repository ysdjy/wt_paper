"""Fig. 2 — Cross-condition robustness across D1/D2/D3.

Input: final_statistical_evidence/results/TRANSFER_TASKS_D1_D2_D3.csv
Output: fig2_cross_condition.{svg,pdf,png} and data_manifest.json
Run: python figures/fig2_cross_condition/plot_fig2.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.palette import DC_PSR, METHOD_ORDER
from _shared.style import FIG_WIDTH, apply_publication_style
from _shared.utils_export import export_figure
from _shared.utils_io import read_csv, sha256, write_manifest
from _shared.utils_layout import add_panel_caption


SOURCE = "final_statistical_evidence/results/TRANSFER_TASKS_D1_D2_D3.csv"
TASKS = ["D1", "D2", "D3"]
OUT_DIR = Path(__file__).resolve().parent
CMAP = LinearSegmentedColormap.from_list("relative", ["#17324D", "#4A8C91", "#F0D89E"])


def minmax(values: np.ndarray, higher_better: bool) -> np.ndarray:
    lo, hi = float(np.min(values)), float(np.max(values))
    score = np.full_like(values, 0.5, dtype=float) if np.isclose(lo, hi) else (values - lo) / (hi - lo)
    return score if higher_better else 1 - score


def rank_desc(values: np.ndarray) -> np.ndarray:
    order = np.argsort(-values, kind="stable")
    ranks = np.empty(len(order), dtype=int)
    ranks[order] = np.arange(1, len(order) + 1)
    return ranks


def metric_pack(df: pd.DataFrame, metric: str, higher_better: bool):
    raw = df.pivot(index="Method", columns="Task", values=metric).loc[METHOD_ORDER, TASKS]
    score, rank = raw.copy(), raw.copy()
    for task in TASKS:
        vals = raw[task].to_numpy(float)
        score[task] = minmax(vals, higher_better)
        rank[task] = rank_desc(score[task].to_numpy(float))
    return raw, score.astype(float), rank.astype(int)


def draw_heatmap(fig, ax, score, rank, *, show_ylabels: bool):
    im = ax.imshow(score, cmap=CMAP, vmin=0, vmax=1, aspect="auto", interpolation="nearest")
    ax.set_xticks(range(3), labels=TASKS)
    ax.set_yticks(range(len(METHOD_ORDER)), labels=METHOD_ORDER if show_ylabels else [""] * len(METHOD_ORDER))
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    for i in range(score.shape[0]):
        for j in range(score.shape[1]):
            rgba = CMAP(score[i, j])
            lum = 0.299 * rgba[0] + 0.587 * rgba[1] + 0.114 * rgba[2]
            ax.text(j, i, f"#{rank[i, j]}", ha="center", va="center", fontsize=5.6,
                    color="white" if lum < 0.48 else "#202020")
    ax.add_patch(mpl.patches.Rectangle((-0.49, -0.49), 2.98, 0.98, fill=False,
                                       edgecolor=DC_PSR, linewidth=1.2, clip_on=False))
    cbar = fig.colorbar(im, ax=ax, fraction=0.045, pad=0.025)
    cbar.set_label("Relative within task", fontsize=6.0)
    cbar.ax.tick_params(labelsize=5.5, length=2)
    return cbar


def main() -> list[Path]:
    apply_publication_style()
    df = read_csv(SOURCE).replace({"HTT-Net (adapted)": "HTT-Net"})
    for column in ["Acc", "M_F1", "Smooth"]:
        df[column] = pd.to_numeric(df[column])
    packs = {
        "Accuracy": metric_pack(df, "Acc", True),
        "M-F1": metric_pack(df, "M_F1", True),
        "Consistency": metric_pack(df, "Smooth", False),
    }

    fig, axes = plt.subplots(2, 2, figsize=(FIG_WIDTH, 6.1))
    ax_a, ax_b, ax_c, ax_d = axes.ravel()
    fig.subplots_adjust(left=0.18, right=0.975, top=0.98, bottom=0.10, hspace=0.72, wspace=0.44)
    cba = draw_heatmap(fig, ax_a, packs["Accuracy"][1].to_numpy(), packs["Accuracy"][2].to_numpy(), show_ylabels=True)
    cbb = draw_heatmap(fig, ax_b, packs["M-F1"][1].to_numpy(), packs["M-F1"][2].to_numpy(), show_ylabels=False)
    cbc = draw_heatmap(fig, ax_c, packs["Consistency"][1].to_numpy(), packs["Consistency"][2].to_numpy(), show_ylabels=True)

    # d — DC-PSR task-wise rank profile; no pooled absolute mean.
    x = np.arange(3)
    metric_colors = {"Accuracy": "#315A7D", "M-F1": "#6A8E88", "Consistency": "#D9A441"}
    rank_profile = {}
    for label, (_, _, ranks) in packs.items():
        values = ranks.loc["DC-PSR", TASKS].to_numpy(int)
        rank_profile[label] = values.tolist()
        ax_d.plot(x, values, marker="o", ms=4.2, lw=1.2, color=metric_colors[label], label=label)
        for xi, value in zip(x, values):
            ax_d.text(xi, value - 0.25, f"#{value}", ha="center", va="bottom", fontsize=5.7, color=metric_colors[label])
    ax_d.set_xticks(x, labels=TASKS)
    ax_d.set_ylabel("DC-PSR within-task rank")
    ax_d.set_ylim(9.6, 0.4)
    ax_d.set_yticks(range(1, 10, 2))
    ax_d.grid(axis="y", color="#E8E8E8", lw=0.45)
    ax_d.legend(ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.01), columnspacing=0.8)
    ax_d.text(0.5, 0.04, "No cross-task absolute average", transform=ax_d.transAxes,
              ha="center", va="bottom", fontsize=5.8, color="#606060")

    add_panel_caption(fig, [ax_a, cba.ax], "a", "Within-task relative accuracy", pad=0.027)
    add_panel_caption(fig, [ax_b, cbb.ax], "b", "Within-task relative M-F1", pad=0.027)
    add_panel_caption(fig, [ax_c, cbc.ax], "c", "Within-task relative consistency (Smooth)", pad=0.027)
    add_panel_caption(fig, ax_d, "d", "DC-PSR task-dependent rank profile", pad=0.042)

    key_values = {
        "dc_psr_rank_profile": rank_profile,
        "note": "Heatmap colors are task-wise min-max scores; cell labels are within-task ranks.",
    }
    write_manifest(OUT_DIR / "data_manifest.json", {
        "figure": "Fig.2 Cross-condition Robustness", "audit_status": "passed",
        "sources": [{"path": SOURCE, "sha256": sha256(SOURCE),
                     "table_or_rows": "27 rows = 9 methods × D1/D2/D3",
                     "columns": ["Method", "Task", "Acc", "M_F1", "Smooth"],
                     "aggregation": "none beyond source task-level summaries",
                     "normalization": "within each task: high-is-good min-max for Acc/M-F1; inverted min-max for Smooth",
                     "bootstrap": "not used in this figure"}],
        "key_values": key_values,
        "warnings": ["D1/D2/D3 use their formal native test universes; the figure therefore avoids pooled absolute means."],
    })
    return export_figure(fig, OUT_DIR / "fig2_cross_condition")


if __name__ == "__main__":
    main()
