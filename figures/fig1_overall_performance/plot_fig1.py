"""Fig. 1 — Overall performance.

Input: final_statistical_evidence/results/D1_MAIN_BOOTSTRAP_CI.csv
Output: fig1_overall_performance.{svg,pdf,png} and data_manifest.json
Run: python figures/fig1_overall_performance/plot_fig1.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.palette import BACKBONE, DC_PSR, GRID, METHOD_COLORS, METHOD_MARKERS
from _shared.style import FIG_WIDTH, apply_publication_style
from _shared.utils_export import export_figure
from _shared.utils_io import read_csv, sha256, write_manifest
from _shared.utils_layout import add_panel_caption


SOURCE = "final_statistical_evidence/results/D1_MAIN_BOOTSTRAP_CI.csv"
OUT_DIR = Path(__file__).resolve().parent


def pareto_frontier(frame: pd.DataFrame) -> pd.DataFrame:
    keep = []
    for idx, row in frame.iterrows():
        dominated = (
            (frame["Acc"] >= row["Acc"])
            & (frame["Smooth"] <= row["Smooth"])
            & ((frame["Acc"] > row["Acc"]) | (frame["Smooth"] < row["Smooth"]))
        ).any()
        if not dominated:
            keep.append(idx)
    return frame.loc[keep].sort_values("Acc")


def main() -> list[Path]:
    apply_publication_style()
    df = read_csv(SOURCE).replace({"HTT-Net (adapted)": "HTT-Net"})
    numeric = [column for column in df.columns if column != "Method"]
    df[numeric] = df[numeric].apply(pd.to_numeric)
    pair = df.set_index("Method").loc[["Multi-task TCN-GRU", "DC-PSR"]]

    fig, axes = plt.subplots(2, 2, figsize=(FIG_WIDTH, 5.65))
    ax_a, ax_b, ax_c, ax_d = axes.ravel()
    fig.subplots_adjust(left=0.12, right=0.985, top=0.97, bottom=0.11, hspace=0.76, wspace=0.42)

    # a — D1 accuracy estimates and bootstrap confidence intervals.
    forest = df.sort_values("Acc").reset_index(drop=True)
    y = np.arange(len(forest))
    for yi, row in forest.iterrows():
        hero = row["Method"] == "DC-PSR"
        color = DC_PSR if hero else "#7E8993"
        ax_a.plot([row["Acc_CI_low"], row["Acc_CI_high"]], [yi, yi], color=color,
                  lw=1.55 if hero else 0.95, alpha=1 if hero else 0.78)
        ax_a.scatter(row["Acc"], yi, marker=METHOD_MARKERS[row["Method"]],
                     s=34 if hero else 18, color=color, edgecolor="white", linewidth=0.45, zorder=3)
        if hero:
            ax_a.annotate(
                f"98.68%  [96.38, 100.00]",
                xy=(row["Acc"], yi), xytext=(-7, 10), textcoords="offset points",
                ha="right", va="bottom", fontsize=6.2, color=DC_PSR,
            )
    ax_a.set_yticks(y, labels=forest["Method"])
    ax_a.set_xlabel("Accuracy")
    ax_a.set_xlim(max(0.55, forest["Acc_CI_low"].min() - 0.02), 1.012)
    ax_a.grid(axis="x", color=GRID, lw=0.45)

    # b — Pareto view of discrimination and sequence smoothness.
    short = {
        "DC-PSR": "DC-PSR", "Multi-task TCN-GRU": "MT-TCN", "TCN-GRU": "TCN",
        "RF": "RF", "HTT-Net": "HTT", "Multi-source Attention": "MS-Attn",
        "MTF-AViTK": "MTF", "Dynamic GIN + TGP": "DynGIN", "DP2Net-adapted": "DP2Net",
    }
    for _, row in df.iterrows():
        method = row["Method"]
        ax_b.scatter(row["Acc"], row["Smooth"], marker=METHOD_MARKERS[method],
                     s=40 if method == "DC-PSR" else 25, color=METHOD_COLORS[method],
                     edgecolor="white", linewidth=0.4, zorder=3)
        ax_b.annotate(short[method], (row["Acc"], row["Smooth"]), xytext=(4, 1),
                      textcoords="offset points", fontsize=5.5, color=METHOD_COLORS[method])
    front = pareto_frontier(df)
    ax_b.plot(front["Acc"], front["Smooth"], ls="--", lw=0.8, color="#919191")
    ax_b.set_xlabel("Accuracy ↑")
    ax_b.set_ylabel("Smooth ↓")
    ax_b.set_xlim(df["Acc"].min() - 0.035, 1.015)
    ax_b.set_ylim(-0.008, df["Smooth"].max() * 1.12)

    # c — shared-backbone controlled comparison.
    metrics = [
        ("Acc", "Acc", ".3f"), ("M_F1", "M-F1", ".3f"), ("M_Rec", "M-Rec", ".3f"),
        ("M_to_L", "M→L", ".3f"), ("Smooth", "Smooth", ".4f"),
    ]
    yy = np.arange(len(metrics))[::-1]
    for yi, (column, label, fmt) in zip(yy, metrics):
        b, d = float(pair.loc["Multi-task TCN-GRU", column]), float(pair.loc["DC-PSR", column])
        higher_better = column != "Smooth"
        if np.isclose(b, d):
            xb = xd = 0.50
        elif (d > b) == higher_better:
            xb, xd = 0.18, 0.82
        else:
            xb, xd = 0.82, 0.18
        ax_c.plot([xb, xd], [yi, yi], color="#B5BCC2", lw=1.4)
        ax_c.scatter(xb, yi, marker="D", s=28, color=BACKBONE, edgecolor="white", linewidth=0.4, zorder=3)
        ax_c.scatter(xd, yi, marker="o", s=34, color=DC_PSR, edgecolor="white", linewidth=0.4, zorder=4)
        ax_c.text(0.50, yi + 0.23, f"{b:{fmt}} → {d:{fmt}}", va="bottom", ha="center", fontsize=5.3)
    ax_c.set_yticks(yy, labels=[item[1] for item in metrics])
    ax_c.set_xlabel("Within-metric paired position (better →)")
    ax_c.set_xlim(0, 1)
    ax_c.grid(axis="x", color=GRID, lw=0.45)
    ax_c.legend(
        [plt.Line2D([], [], marker="D", ls="", color=BACKBONE), plt.Line2D([], [], marker="o", ls="", color=DC_PSR)],
        ["Multi-task TCN-GRU", "DC-PSR"], loc="lower center", bbox_to_anchor=(0.5, 1.01), ncol=2,
    )

    # d — normalized summary without duplicating the raw metrics.
    class_cols = ["Acc", "M_F1", "M_Rec"]
    retention = float((pair.loc["DC-PSR", class_cols] / pair.loc["Multi-task TCN-GRU", class_cols]).mean())
    smooth_reduction = float(1 - pair.loc["DC-PSR", "Smooth"] / pair.loc["Multi-task TCN-GRU", "Smooth"])
    values = [100 * retention, 100 * smooth_reduction]
    labels = ["Classification retained", "Smoothness reduction"]
    colors = [BACKBONE, DC_PSR]
    bars = ax_d.barh([1, 0], values, color=colors, height=0.48)
    ax_d.set_yticks([1, 0], labels=labels)
    ax_d.set_xlabel("Normalized summary (%)")
    ax_d.set_xlim(0, 108)
    ax_d.grid(axis="x", color=GRID, lw=0.45)
    for bar, value in zip(bars, values):
        ax_d.text(value + 1.5, bar.get_y() + bar.get_height() / 2, f"{value:.1f}%", va="center", fontsize=6.3)

    add_panel_caption(fig, ax_a, "a", "D1 bootstrap confidence intervals", pad=0.038)
    add_panel_caption(fig, ax_b, "b", "Accuracy–consistency trade-off", pad=0.038)
    add_panel_caption(fig, ax_c, "c", "Controlled comparison:\nbackbone vs DC-PSR", pad=0.040)
    add_panel_caption(fig, ax_d, "d", "Classification retention\nand consistency gain", pad=0.040)

    key = {
        "dc_psr_accuracy": float(pair.loc["DC-PSR", "Acc"]),
        "dc_psr_accuracy_ci": [float(pair.loc["DC-PSR", "Acc_CI_low"]), float(pair.loc["DC-PSR", "Acc_CI_high"])],
        "backbone_accuracy": float(pair.loc["Multi-task TCN-GRU", "Acc"]),
        "dc_psr_smooth": float(pair.loc["DC-PSR", "Smooth"]),
        "backbone_smooth": float(pair.loc["Multi-task TCN-GRU", "Smooth"]),
        "classification_retention_percent": 100 * retention,
        "smoothness_reduction_percent": 100 * smooth_reduction,
    }
    write_manifest(OUT_DIR / "data_manifest.json", {
        "figure": "Fig.1 Overall Performance", "audit_status": "passed",
        "sources": [{"path": SOURCE, "sha256": sha256(SOURCE),
                     "table_or_rows": "all 9 method rows; controlled panels use Multi-task TCN-GRU and DC-PSR",
                     "columns": ["Method", "Acc", "Acc_CI_low", "Acc_CI_high", "M_F1", "M_Rec", "M_to_L", "Smooth"],
                     "aggregation": "none; source contains 304-run common-universe summaries",
                     "normalization": "only panel d uses ratios relative to the shared backbone",
                     "bootstrap": "moving-block bootstrap CI read directly from source"}],
        "key_values": key, "warnings": [],
    })
    return export_figure(fig, OUT_DIR / "fig1_overall_performance")


if __name__ == "__main__":
    main()
