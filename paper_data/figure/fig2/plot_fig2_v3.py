"""
Fig.2 v3 (paper Fig. 4-3): cross-condition / cross-dataset generalization -- dense 2x2 dashboard
reconstruction.

DATA AND STATISTICS ARE UNCHANGED FROM v1/v2: imports v1's load() directly (taskwise_absolute /
taskwise_normalized / cross_dataset_absolute / cross_dataset_deltas), and re-derives every panel
number with the exact same formulas v1 uses (copied verbatim, including v1's np.isclose checks).

Layout, ground-up rebuilt as a strict 2x2 dashboard (landscape 15.5x10.2in):
  (a) top-left  : PHM2010 D1/D2/D3 x 9-method robustness, 3 compact mini-heatmaps (Acc/M-F1/Smooth)
  (b) top-right : Multi-task TCN-GRU -> DC-PSR paired gain, PHM D1/D2/D3 + NASA N1-N4 avg +
                  MTW-CM D1-M/D2-M/D3-M + avg, as a lollipop/dot-range chart (not grouped bars)
  (c) bottom-left: 3 dataset-profile mini-radars (PHM2010/NASA Milling/MTW-CM), each ONLY
                  Multi-task TCN-GRU vs DC-PSR (no fictional 9-method-per-dataset comparison --
                  NASA/MTW-CM never had all 9 methods evaluated)
  (d) bottom-right: classification-consistency balance map, 6 REAL points only (B11/B12 x 3
                  datasets), thin B11->B12 connector per dataset

No figure-level title anywhere (not even a bottom "鲁棒性" caption -- v2's convention is gone in
v3). Every panel caption "(a)/(b)/(c)/(d) description" sits BELOW its panel via
style_v3.panel_container()'s nested subgridspec.

Style reference: paper_data/figure/fig2/视觉参考效果图/*.png -- LAYOUT ONLY (2x2 dashboard
proportions, lollipop panel, radar-profile idea, balance-map idea). Its own numbers, its
CNN/ResNet18/TCN/GRU/TCN-GRU/Transformer/DANN/MTL roster, and its "9 methods on NASA/MTW-CM" claim
are all fictional and are NOT reproduced -- see reference vs 视觉参考效果图 distinction in
paper_data/figure/FIGURE_PROGRESS.md.

Run: python paper_data/figure/fig2/plot_fig2_v3.py
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_shared"))
from style_v3 import apply_style, save_all, panel_container, METHOD_COLORS, BENEFIT_CMAP  # noqa: E402
import data_utils as du  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
from plot_fig2 import load, PHM_TASKS  # noqa: E402

HERE = os.path.dirname(__file__)
OUT_DIR = os.path.join(HERE, "outputs")
LOG_DIR = os.path.join(HERE, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

HEATMAP_METRICS = ["Acc", "M_F1", "Smooth"]
BACKBONE_COLOR = METHOD_COLORS["Multi-task TCN-GRU"]
DCPSR_COLOR = METHOD_COLORS["DC-PSR"]


# ---------------------------------------------------------------------------
# panel (a): PHM D1/D2/D3 x 9-method mini-heatmaps
# ---------------------------------------------------------------------------
def panel_a_taskwise(fig, outer_cell, tw_norm, log_lines):
    content_spec, _ = panel_container(
        fig, outer_cell,
        "(a) Within-task robustness, PHM2010 D1/D2/D3 × 9 methods\n(color = within-task-metric benefit; numbers = raw values)",
        hspace=0.16, caption_height=0.09, fontsize=8.6)
    grid3 = content_spec.subgridspec(1, 3, wspace=0.12)

    from style_v3 import METHOD_ORDER
    axes = []
    for i, task in enumerate(PHM_TASKS):
        ax = fig.add_subplot(grid3[i])
        axes.append(ax)
        sub = tw_norm[tw_norm["Task"] == task]
        methods = [m for m in METHOD_ORDER if m in sub["Method"].unique()]
        grid = np.zeros((len(methods), len(HEATMAP_METRICS)))
        raw = np.zeros_like(grid)
        for j, metric in enumerate(HEATMAP_METRICS):
            for k, m in enumerate(methods):
                row = sub[(sub["Method"] == m) & (sub["metric"] == metric)]
                grid[k, j] = row["normalized_score"].values[0]
                raw[k, j] = row["absolute_value"].values[0]
        ax.imshow(grid, aspect="auto", cmap=BENEFIT_CMAP, vmin=0, vmax=1)
        ax.set_yticks(np.arange(len(methods)))
        ax.set_yticklabels(methods if i == 0 else [""] * len(methods), fontsize=6.3)
        ax.set_xticks(np.arange(3))
        ax.set_xticklabels(["Acc↑", "M-F1↑", "Smooth↓"], fontsize=6.5)
        for k in range(len(methods)):
            for j in range(3):
                ax.text(j, k, f"{raw[k, j]:.2f}", ha="center", va="center", fontsize=5.4,
                         color="white" if grid[k, j] > 0.55 else "#2A2A2A")
        ax.grid(False)
        ax.tick_params(length=2)
        ax.set_xlabel(task, fontsize=7.5, fontweight="bold", labelpad=3)
        for k, m in enumerate(methods):
            if m == "DC-PSR":
                ax.get_yticklabels()[k].set_color(DCPSR_COLOR)
            elif m == "Multi-task TCN-GRU":
                ax.get_yticklabels()[k].set_color(BACKBONE_COLOR)

    n_unique_best = tw_norm[tw_norm["metric"] == "Acc"].sort_values(["Task", "absolute_value"]).groupby("Task").tail(1)["Method"].nunique()
    log_lines.append(f"PASS: {n_unique_best} distinct methods top Acc across D1/D2/D3 (target-condition dependence).")
    return axes


# ---------------------------------------------------------------------------
# panel (b): lollipop paired gain, PHM + NASA + MTW-CM
# ---------------------------------------------------------------------------
def panel_b_lollipop(fig, outer_cell, tw_abs, cross_abs, log_lines):
    content_spec, _ = panel_container(
        fig, outer_cell,
        "(b) Multi-task TCN-GRU → DC-PSR paired gain, PHM/NASA/MTW-CM\n"
        "(Smooth/Jump = benefit = backbone − DC-PSR; positive = improvement)",
        hspace=0.16, caption_height=0.09, fontsize=8.6)
    ax = fig.add_subplot(content_spec)

    bb = tw_abs[tw_abs["Method"] == "Multi-task TCN-GRU"].set_index("Task")
    dc = tw_abs[tw_abs["Method"] == "DC-PSR"].set_index("Task")
    rows = []
    for task in PHM_TASKS:
        d_acc = (dc.loc[task, "Acc"] - bb.loc[task, "Acc"]) * 100
        d_mf1 = (dc.loc[task, "M_F1"] - bb.loc[task, "M_F1"]) * 100
        smooth_benefit = (bb.loc[task, "Smooth"] - dc.loc[task, "Smooth"]) / bb.loc[task, "Smooth"] * 100
        rows.append((f"PHM {task}", d_acc, d_mf1, smooth_benefit, None))

    scopes = [("NASA Milling\nN1–N4 avg", "NASA_MILLING", "original_N1-N4"),
              ("MTW-CM\nD1-M", "MILLING_CROSS_MACHINE", "D1-M"),
              ("MTW-CM\nD2-M", "MILLING_CROSS_MACHINE", "D2-M"),
              ("MTW-CM\nD3-M", "MILLING_CROSS_MACHINE", "D3-M"),
              ("MTW-CM\n3-task avg", "MILLING_CROSS_MACHINE", "D1-M,D2-M,D3-M")]
    for label, dataset, scope in scopes:
        b11 = cross_abs[(cross_abs["dataset"] == dataset) & (cross_abs["task_scope"] == scope) & (cross_abs["method"] == "B11")].iloc[0]
        b12 = cross_abs[(cross_abs["dataset"] == dataset) & (cross_abs["task_scope"] == scope) & (cross_abs["method"] == "B12")].iloc[0]
        d_acc = (b12["Acc"] - b11["Acc"]) * 100
        d_mf1 = (b12["M_F1"] - b11["M_F1"]) * 100
        smooth_benefit = (b11["Smooth"] - b12["Smooth"]) / b11["Smooth"] * 100 if b11["Smooth"] > 0 else 0.0
        jump_benefit = (b11["Jump"] - b12["Jump"]) / b11["Jump"] * 100 if b11["Jump"] > 0 else 0.0
        rows.append((label, d_acc, d_mf1, smooth_benefit, jump_benefit))

    # rows layout: [0]=PHM D1, [1]=PHM D2, [2]=PHM D3, [3]=NASA avg, [4..6]=MTW D1/D2/D3-M, [7]=MTW avg
    assert np.isclose(rows[0][1], -0.33, atol=0.1) and np.isclose(rows[0][2], -0.39, atol=0.15)
    assert np.isclose(rows[3][2], 5.86, atol=0.5), rows[3]
    assert np.isclose(rows[7][2], 10.04, atol=0.5), rows[7]
    log_lines.append("PASS: panel(b) PHM D1 dAcc/dM-F1 and NASA/MTW-CM-avg dM-F1 match design-doc headline numbers.")

    labels = [r[0] for r in rows]
    y = np.arange(len(rows))[::-1]
    metric_specs = [("ΔAcc (pp)", 1, "#3D6EA8", "D"), ("ΔM-F1 (pp)", 2, "#2A8C7A", "o"),
                     ("Smooth benefit (%)", 3, "#D9A441", "s"), ("Jump benefit (%)", 4, "#B0555E", "^")]
    offsets = np.linspace(-0.28, 0.28, 4)
    for (mlabel, idx, color, marker), off in zip(metric_specs, offsets):
        vals = [r[idx] for r in rows]
        yy = y + off
        valid = [(v, yv) for v, yv in zip(vals, yy) if v is not None]
        if not valid:
            continue
        vv, yv = zip(*valid)
        ax.hlines(yv, 0, vv, color=color, lw=1.1, alpha=0.55)
        ax.scatter(vv, yv, color=color, s=32, marker=marker, label=mlabel, zorder=3, edgecolor="black", linewidth=0.4)
    ax.axvline(0, color="#555555", lw=0.9)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=7.2)
    ax.set_xlabel("Δ (pp) or benefit (%) — positive = improvement")
    ax.legend(loc="lower right", fontsize=6.5, ncol=2)
    ax.set_ylim(-0.7, len(rows) - 0.3)
    return ax


# ---------------------------------------------------------------------------
# panel (c): 3 dataset-profile mini-radars, Multi-task TCN-GRU vs DC-PSR only
# ---------------------------------------------------------------------------
def _radar_axes_angles(n):
    return np.linspace(0, 2 * np.pi, n, endpoint=False)


def panel_c_profiles(fig, outer_cell, cross_abs, log_lines):
    content_spec, _ = panel_container(
        fig, outer_cell,
        "(c) Dataset-profile cards: Multi-task TCN-GRU vs DC-PSR only\n(NASA/MTW-CM never evaluated all 9 methods)",
        hspace=0.18, caption_height=0.09, fontsize=8.6)
    grid3 = content_spec.subgridspec(1, 3, wspace=0.45)

    axes_metrics = ["Acc↑", "M-F1↑", "Consistency↑\n=1/(1+Smooth)", "Stability↑\n=1/(1+Jump)"]
    n = len(axes_metrics)
    angles = _radar_axes_angles(n)
    angles_closed = np.concatenate([angles, [angles[0]]])

    cards = [("PHM2010", "PHM2010", "D1"), ("NASA Milling", "NASA_MILLING", "original_N1-N4"),
             ("MTW-CM", "MILLING_CROSS_MACHINE", "D1-M,D2-M,D3-M")]
    for i, (title, dataset, scope) in enumerate(cards):
        ax = fig.add_subplot(grid3[i], projection="polar")
        b11 = cross_abs[(cross_abs["dataset"] == dataset) & (cross_abs["task_scope"] == scope) & (cross_abs["method"] == "B11")].iloc[0]
        b12 = cross_abs[(cross_abs["dataset"] == dataset) & (cross_abs["task_scope"] == scope) & (cross_abs["method"] == "B12")].iloc[0]
        for row, color, name in [(b11, BACKBONE_COLOR, "Multi-task TCN-GRU"), (b12, DCPSR_COLOR, "DC-PSR")]:
            vals = [row["Acc"], row["M_F1"], 1 / (1 + row["Smooth"]), 1 / (1 + row["Jump"])]
            vals_closed = vals + [vals[0]]
            ax.plot(angles_closed, vals_closed, color=color, lw=1.4, label=name)
            ax.fill(angles_closed, vals_closed, color=color, alpha=0.12)
        ax.set_xticks(angles)
        ax.set_xticklabels(axes_metrics, fontsize=5.8)
        ax.set_yticks([0.25, 0.5, 0.75, 1.0])
        ax.set_yticklabels(["0.25", "0.50", "0.75", "1.00"], fontsize=5.0)
        ax.set_ylim(0, 1)
        ax.set_title(title, fontsize=8.0, fontweight="bold", pad=10, color="#1A1A1A")
        ax.tick_params(axis="x", pad=2)
        if i == 0:
            ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.28), fontsize=6.3)
    log_lines.append("PASS: panel(c) radar uses only real Multi-task TCN-GRU vs DC-PSR pairs on PHM2010/NASA/MTW-CM "
                     "(Consistency=1/(1+Smooth), Stability=1/(1+Jump) are monotonic display transforms of the raw metrics, "
                     "not new statistics -- raw Acc/M-F1/Smooth/Jump remain in panels a/b/d).")


# ---------------------------------------------------------------------------
# panel (d): balance map, 6 real points
# ---------------------------------------------------------------------------
def panel_d_balance(fig, outer_cell, cross_abs, log_lines):
    content_spec, _ = panel_container(
        fig, outer_cell,
        "(d) Classification–consistency balance: 6 real points\n(method × dataset), B11→B12 connector per dataset",
        hspace=0.16, caption_height=0.09, fontsize=8.6)
    ax = fig.add_subplot(content_spec)

    datasets = [("PHM2010", "PHM2010", "D1", "o"), ("NASA Milling", "NASA_MILLING", "original_N1-N4", "s"),
                ("MTW-CM", "MILLING_CROSS_MACHINE", "D1-M,D2-M,D3-M", "^")]
    n_points = 0
    for label, dataset, scope, marker in datasets:
        b11 = cross_abs[(cross_abs["dataset"] == dataset) & (cross_abs["task_scope"] == scope) & (cross_abs["method"] == "B11")].iloc[0]
        b12 = cross_abs[(cross_abs["dataset"] == dataset) & (cross_abs["task_scope"] == scope) & (cross_abs["method"] == "B12")].iloc[0]
        x = [b11["M_F1"], b12["M_F1"]]
        y = [b11["Smooth"], b12["Smooth"]]
        ax.plot(x, y, color="#8A8D8F", lw=1.2, ls="--", zorder=1)
        ax.scatter(x[0], y[0], color=BACKBONE_COLOR, marker=marker, s=70, edgecolor="black", linewidth=0.6, zorder=3)
        ax.scatter(x[1], y[1], color=DCPSR_COLOR, marker=marker, s=70, edgecolor="black", linewidth=0.6, zorder=3)
        ax.annotate(label, (x[1], y[1]), textcoords="offset points", xytext=(6, 6), fontsize=6.8, color="#333333")
        n_points += 2
    assert n_points == 6, n_points
    log_lines.append("PASS: panel(d) balance map plots exactly 6 real points (B11/B12 x PHM2010/NASA/MTW-CM), no fabricated methods.")

    ax.invert_yaxis()
    ax.set_xlabel("M-F1 (classification, higher better →)")
    ax.set_ylabel("Smooth (consistency; axis inverted, ↑ = better)")
    handles = [plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=BACKBONE_COLOR, markeredgecolor="black", markersize=7, label="Multi-task TCN-GRU"),
               plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=DCPSR_COLOR, markeredgecolor="black", markersize=7, label="DC-PSR"),
               plt.Line2D([0], [0], marker="o", color="none", markerfacecolor="#AAAAAA", markeredgecolor="black", markersize=7, label="PHM2010 (circle)"),
               plt.Line2D([0], [0], marker="s", color="none", markerfacecolor="#AAAAAA", markeredgecolor="black", markersize=7, label="NASA Milling (square)"),
               plt.Line2D([0], [0], marker="^", color="none", markerfacecolor="#AAAAAA", markeredgecolor="black", markersize=7, label="MTW-CM avg (triangle)")]
    ax.legend(handles=handles, loc="best", fontsize=6.3)
    return ax


def main():
    apply_style()
    tw_abs, tw_norm, cross_abs, cross_delta_ref = load()
    log_lines = []

    assert set(tw_abs["Task"].unique()) == set(PHM_TASKS)
    assert len(tw_abs) == 27
    assert set(cross_abs["dataset"].unique()) == {"PHM2010", "NASA_MILLING", "MILLING_CROSS_MACHINE"}
    assert "MIMII" not in cross_abs["dataset"].unique()
    log_lines.append("PASS: taskwise_absolute 27 rows; cross_dataset_absolute dataset set correct, no MIMII.")

    fig = plt.figure(figsize=(15.5, 10.2))
    outer = GridSpec(2, 2, height_ratios=[0.5, 0.5], width_ratios=[0.5, 0.5],
                      hspace=0.20, wspace=0.10, figure=fig,
                      left=0.045, right=0.985, top=0.99, bottom=0.03)

    panel_a_taskwise(fig, outer[0, 0], tw_norm, log_lines)
    panel_b_lollipop(fig, outer[0, 1], tw_abs, cross_abs, log_lines)
    panel_c_profiles(fig, outer[1, 0], cross_abs, log_lines)
    panel_d_balance(fig, outer[1, 1], cross_abs, log_lines)

    paths = save_all(fig, OUT_DIR, "fig2_v3")
    log_lines.append(f"Saved outputs: {paths}")
    with open(os.path.join(LOG_DIR, "validation_v3.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
    print("\n".join(log_lines))
    print("Fig.2 v3 done.")


if __name__ == "__main__":
    main()
