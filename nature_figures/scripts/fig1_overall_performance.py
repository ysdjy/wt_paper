from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from common import (
    CMAP_ABSOLUTE,
    METHOD_COLORS,
    METHOD_MARKERS,
    OUT,
    apply_style,
    clean_method_names,
    panel_label,
    read_csv,
    save_figure,
    write_plot_data,
)


SOURCE = "final_statistical_evidence/results/D1_MAIN_BOOTSTRAP_CI.csv"


def pareto_frontier(df: pd.DataFrame) -> pd.DataFrame:
    keep = []
    for i, row in df.iterrows():
        dominated = ((df["Acc"] >= row["Acc"]) & (df["Smooth"] <= row["Smooth"]) &
                     ((df["Acc"] > row["Acc"]) | (df["Smooth"] < row["Smooth"]))).any()
        if not dominated:
            keep.append(i)
    return df.loc[keep].sort_values("Acc")


def make_figure():
    apply_style()
    df = clean_method_names(read_csv(SOURCE))
    numeric = [c for c in df.columns if c != "Method"]
    df[numeric] = df[numeric].apply(pd.to_numeric)
    write_plot_data(df, "fig1_D1_common_universe_metrics.csv")

    fig = plt.figure(figsize=(7.2, 4.65))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.45, 1.0], hspace=0.58, wspace=0.46)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    c_gs = gs[1, :].subgridspec(1, 5, wspace=0.52)
    axes_c = [fig.add_subplot(c_gs[0, i]) for i in range(5)]

    # a | moving-block bootstrap forest plot
    forest = df.sort_values("Acc", ascending=True).reset_index(drop=True)
    y = np.arange(len(forest))
    for yi, row in forest.iterrows():
        hero = row["Method"] == "DC-PSR"
        color = METHOD_COLORS[row["Method"]] if hero else "#7F8790"
        ax_a.plot([row["Acc_CI_low"], row["Acc_CI_high"]], [yi, yi], color=color,
                  lw=1.55 if hero else 1.0, alpha=1.0 if hero else 0.78, zorder=2)
        ax_a.scatter(row["Acc"], yi, s=32 if hero else 18,
                     marker=METHOD_MARKERS[row["Method"]], color=color,
                     edgecolor="white", linewidth=0.45, zorder=3)
        if hero:
            ax_a.text(row["Acc"] - 0.008, yi + 0.34,
                      f"{100 * row['Acc']:.2f}%  [{100 * row['Acc_CI_low']:.2f}, {100 * row['Acc_CI_high']:.2f}]",
                      color=METHOD_COLORS["DC-PSR"], fontsize=6.0, ha="right", va="center")
    ax_a.set_yticks(y, labels=forest["Method"])
    ax_a.set_xlabel("Accuracy")
    ax_a.set_xlim(max(0.55, forest["Acc_CI_low"].min() - 0.025), 1.012)
    ax_a.set_title("D1 accuracy with 95% moving-block bootstrap CI", loc="left")
    ax_a.grid(axis="x", color="#E8E8E8", lw=0.45, zorder=0)
    panel_label(ax_a, "a", x=-0.17)

    # b | discrimination-consistency Pareto map
    abbreviations = {
        "DC-PSR": "DC-PSR",
        "Multi-task TCN-GRU": "MT-TCN",
        "TCN-GRU": "TCN",
        "RF": "RF",
        "HTT-Net": "HTT",
        "Multi-source Attention": "MS-Attn",
        "MTF-AViTK": "MTF",
        "Dynamic GIN + TGP": "DynGIN",
        "DP2Net-adapted": "DP2Net",
    }
    for _, row in df.iterrows():
        method = row["Method"]
        ax_b.scatter(row["Acc"], row["Smooth"], s=38 if method == "DC-PSR" else 27,
                     marker=METHOD_MARKERS[method], color=METHOD_COLORS[method],
                     edgecolor="white", linewidth=0.45, zorder=4)
        dx = 0.006
        dy = 0.006 if method not in {"TCN-GRU", "DC-PSR"} else -0.010
        ax_b.text(row["Acc"] + dx, row["Smooth"] + dy, abbreviations[method],
                  fontsize=5.8, color=METHOD_COLORS[method], va="center")
    front = pareto_frontier(df)
    ax_b.plot(front["Acc"], front["Smooth"], color="#8A8A8A", lw=0.8, ls="--", zorder=1)
    ax_b.set_xlabel("Accuracy ↑")
    ax_b.set_ylabel("Smooth ↓")
    ax_b.set_title("Accuracy–consistency Pareto map", loc="left")
    ax_b.set_xlim(df["Acc"].min() - 0.035, 1.015)
    ax_b.set_ylim(-0.008, df["Smooth"].max() * 1.12)
    panel_label(ax_b, "b", x=-0.15)

    # c | controlled shared-backbone comparison; each metric keeps its own truthful axis.
    pair = df.set_index("Method").loc[["Multi-task TCN-GRU", "DC-PSR"]]
    metrics = [
        ("Acc", "Acc ↑"),
        ("MacroF1", "Macro-F1 ↑"),
        ("M_F1", "M-F1 ↑"),
        ("Smooth", "Smooth ↓"),
        ("Rev", "Rev ↓"),
    ]
    for j, (metric, label) in enumerate(metrics):
        ax = axes_c[j]
        vals = pair[metric].to_numpy(float)
        ax.plot(vals, [0, 0], color="#A0A0A0", lw=1.15, zorder=1)
        ax.scatter(vals[0], 0, marker=METHOD_MARKERS["Multi-task TCN-GRU"],
                   color=METHOD_COLORS["Multi-task TCN-GRU"], s=27, zorder=3,
                   edgecolor="white", linewidth=0.4)
        ax.scatter(vals[1], 0, marker=METHOD_MARKERS["DC-PSR"],
                   color=METHOD_COLORS["DC-PSR"], s=34, zorder=4,
                   edgecolor="white", linewidth=0.4)
        span = max(abs(vals.max() - vals.min()), 0.004 if metric != "Rev" else 1.0)
        ax.set_xlim(vals.min() - 0.65 * span, vals.max() + 0.65 * span)
        ax.set_ylim(-0.5, 0.5)
        ax.set_yticks([])
        ax.set_xlabel(label, labelpad=2)
        fmt = ".3f" if metric not in {"Smooth", "Rev"} else (".4f" if metric == "Smooth" else ".0f")
        ax.text(vals[0], 0.22, format(vals[0], fmt), color=METHOD_COLORS["Multi-task TCN-GRU"],
                ha="center", fontsize=5.8)
        ax.text(vals[1], -0.28, format(vals[1], fmt), color=METHOD_COLORS["DC-PSR"],
                ha="center", fontsize=5.8)
        ax.spines["left"].set_visible(False)
        ax.tick_params(axis="x", labelsize=5.6)
        if j == 0:
            panel_label(ax, "c", x=-0.38, y=1.18)
            ax.text(-0.08, 1.18, "Controlled backbone comparison", transform=ax.transAxes,
                    ha="left", va="bottom", fontsize=8.0, fontweight="bold")

    fig.text(0.995, 0.012,
             "Blue diamond: Multi-task TCN-GRU   •   Vermillion circle: DC-PSR",
             ha="right", va="bottom", fontsize=6.0)
    return fig


def main():
    fig = make_figure()
    return save_figure(fig, OUT / "fig1_overall_performance", "fig1_overall_performance")


if __name__ == "__main__":
    main()
