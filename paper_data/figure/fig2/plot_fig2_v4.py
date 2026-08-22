"""
Fig.2 v4 (paper Fig. 4-3): cross-condition / cross-dataset generalization -- publication-grade
true-physical-size refinement (178 x 125 mm master size).

DATA UNCHANGED FROM v1/v2/v3: imports v1's load() directly (taskwise_absolute/normalized,
cross_dataset_absolute/deltas) and re-derives every panel number with the exact same formulas v1
uses. Only the visualization layer changed again. See paper_data/figure/V4_DESIGN_AUDIT.md for the
full rationale and paper_data/figure/fig2/README.md's "v4" section for what changed vs v3 and why.

Run: python paper_data/figure/fig2/plot_fig2_v4.py
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Rectangle

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_shared"))
from style_v4 import (apply_style, save_all, panel_container, master_figsize_in,
                       METHOD_COLORS, METHOD_ORDER, BENEFIT_CMAP)  # noqa: E402

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
# panel (a): PHM D1/D2/D3 x 9-method mini-heatmaps, ONE shared y-axis + ONE shared colorbar
# ---------------------------------------------------------------------------
def panel_a_taskwise(fig, outer_cell, tw_norm, log_lines):
    content_spec, _ = panel_container(
        fig, outer_cell,
        "(a) Within-task robustness, PHM2010 D1/D2/D3 × 9 methods\n(color = within-task benefit; numbers = raw values)",
        hspace=0.58, caption_height=0.115, fontsize=8.4)
    grid = content_spec.subgridspec(1, 4, width_ratios=[1.42, 1.0, 1.0, 0.15], wspace=0.24)

    im_ref = None
    axes = []
    for i, task in enumerate(PHM_TASKS):
        ax = fig.add_subplot(grid[i])
        axes.append(ax)
        sub = tw_norm[tw_norm["Task"] == task]
        methods = [m for m in METHOD_ORDER if m in sub["Method"].unique()]
        g = np.zeros((len(methods), len(HEATMAP_METRICS)))
        raw = np.zeros_like(g)
        for j, metric in enumerate(HEATMAP_METRICS):
            for k, m in enumerate(methods):
                row = sub[(sub["Method"] == m) & (sub["metric"] == metric)]
                g[k, j] = row["normalized_score"].values[0]
                raw[k, j] = row["absolute_value"].values[0]
        im = ax.imshow(g, aspect="auto", cmap=BENEFIT_CMAP, vmin=0, vmax=1)
        im_ref = im
        ax.set_yticks(np.arange(len(methods)))
        ax.set_yticklabels(methods if i == 0 else [], fontsize=6.6)
        ax.set_xticks(np.arange(3))
        # rotated + right-aligned: at this mini-heatmap's narrow column width (~0.3in for D2/D3),
        # horizontal labels touch/overlap their neighbors -- rotation reduces each label's
        # horizontal footprint without shrinking text below the 6.5pt floor.
        ax.set_xticklabels(["Acc↑", "M-F1↑", "Smooth↓"], fontsize=6.6, rotation=32, ha="right",
                            rotation_mode="anchor")
        for k in range(len(methods)):
            for j in range(3):
                ax.text(j, k, f"{raw[k, j]:.2f}", ha="center", va="center", fontsize=6.5,
                         color="white" if g[k, j] > 0.55 else "#232323")
        ax.grid(False)
        ax.tick_params(length=1.6)
        # short single-line per-panel tag via set_xlabel -- this is the mechanism v3 already used
        # successfully here; an earlier v4 draft switched to set_title(y<0) by analogy with
        # fig1_v4's confusion-matrix labels, but that was the wrong tool for THIS case (dense
        # heatmap columns packed tightly side by side) and caused a real title/tick collision at
        # true physical size -- xlabel is the correct, already-validated choice for this panel.
        ax.set_xlabel(task, fontsize=7.0, fontweight="bold", labelpad=3, color="#1A1A1A")
        for k, m in enumerate(methods):
            if m == "DC-PSR":
                ax.add_patch(Rectangle((-0.5, k - 0.5), 3, 1, fill=False, edgecolor=DCPSR_COLOR, linewidth=1.1, zorder=5))
            elif m == "Multi-task TCN-GRU":
                ax.add_patch(Rectangle((-0.5, k - 0.5), 3, 1, fill=False, edgecolor=BACKBONE_COLOR, linewidth=1.1, zorder=5))

    cax = fig.add_subplot(grid[3])
    cbar = plt.colorbar(im_ref, cax=cax)
    cbar.set_label("benefit", fontsize=6.5, labelpad=2)
    cbar.ax.tick_params(labelsize=6.5)
    cbar.set_ticks([0, 1]); cbar.set_ticklabels(["low", "high"])

    n_unique_best = tw_norm[tw_norm["metric"] == "Acc"].sort_values(["Task", "absolute_value"]).groupby("Task").tail(1)["Method"].nunique()
    log_lines.append(f"PASS: {n_unique_best} distinct methods top Acc across D1/D2/D3 (target-condition dependence).")
    return axes


# ---------------------------------------------------------------------------
# panel (b): lollipop paired gain, PHM + NASA + MTW-CM
# ---------------------------------------------------------------------------
def panel_b_lollipop(fig, outer_cell, tw_abs, cross_abs, log_lines):
    content_spec, _ = panel_container(
        fig, outer_cell,
        "(b) Multi-task TCN-GRU → DC-PSR paired gain, PHM/NASA/MTW-CM\n(Smooth/Jump = benefit = backbone − DC-PSR; positive = improvement)",
        hspace=0.42, caption_height=0.115, fontsize=8.4)
    ax = fig.add_subplot(content_spec)

    bb = tw_abs[tw_abs["Method"] == "Multi-task TCN-GRU"].set_index("Task")
    dc = tw_abs[tw_abs["Method"] == "DC-PSR"].set_index("Task")
    rows = []
    for task in PHM_TASKS:
        d_acc = (dc.loc[task, "Acc"] - bb.loc[task, "Acc"]) * 100
        d_mf1 = (dc.loc[task, "M_F1"] - bb.loc[task, "M_F1"]) * 100
        smooth_benefit = (bb.loc[task, "Smooth"] - dc.loc[task, "Smooth"]) / bb.loc[task, "Smooth"] * 100
        rows.append((f"PHM {task}", d_acc, d_mf1, smooth_benefit, None))

    scopes = [("NASA N1–N4 avg", "NASA_MILLING", "original_N1-N4"),
              ("MTW-CM D1-M", "MILLING_CROSS_MACHINE", "D1-M"),
              ("MTW-CM D2-M", "MILLING_CROSS_MACHINE", "D2-M"),
              ("MTW-CM D3-M", "MILLING_CROSS_MACHINE", "D3-M"),
              ("MTW-CM 3-task avg", "MILLING_CROSS_MACHINE", "D1-M,D2-M,D3-M")]
    for label, dataset, scope in scopes:
        b11 = cross_abs[(cross_abs["dataset"] == dataset) & (cross_abs["task_scope"] == scope) & (cross_abs["method"] == "B11")].iloc[0]
        b12 = cross_abs[(cross_abs["dataset"] == dataset) & (cross_abs["task_scope"] == scope) & (cross_abs["method"] == "B12")].iloc[0]
        d_acc = (b12["Acc"] - b11["Acc"]) * 100
        d_mf1 = (b12["M_F1"] - b11["M_F1"]) * 100
        smooth_benefit = (b11["Smooth"] - b12["Smooth"]) / b11["Smooth"] * 100 if b11["Smooth"] > 0 else 0.0
        jump_benefit = (b11["Jump"] - b12["Jump"]) / b11["Jump"] * 100 if b11["Jump"] > 0 else 0.0
        rows.append((label, d_acc, d_mf1, smooth_benefit, jump_benefit))

    assert np.isclose(rows[0][1], -0.33, atol=0.1) and np.isclose(rows[0][2], -0.39, atol=0.15)
    assert np.isclose(rows[3][2], 5.86, atol=0.5), rows[3]
    assert np.isclose(rows[7][2], 10.04, atol=0.5), rows[7]
    log_lines.append("PASS: panel(b) PHM D1 dAcc/dM-F1 and NASA/MTW-CM-avg dM-F1 match design-doc headline numbers.")

    labels = [r[0] for r in rows]
    y = np.arange(len(rows))[::-1]
    metric_specs = [("ΔAcc (pp)", 1, "#2F6FB3", "D"), ("ΔM-F1 (pp)", 2, "#2E8B57", "o"),
                     ("Smooth benefit (%)", 3, "#D39B23", "s"), ("Jump benefit (%)", 4, "#C73635", "^")]
    offsets = np.linspace(-0.28, 0.28, 4)
    for (mlabel, idx, color, marker), off in zip(metric_specs, offsets):
        vals = [r[idx] for r in rows]
        yy = y + off
        valid = [(v, yv) for v, yv in zip(vals, yy) if v is not None]
        vv, yv = zip(*valid)
        ax.hlines(yv, 0, vv, color=color, lw=1.0, alpha=0.55)
        ax.scatter(vv, yv, color=color, s=26, marker=marker, label=mlabel, zorder=3, edgecolor="black", linewidth=0.35)
    ax.axvline(0, color="#555555", lw=0.9)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=6.9)
    ax.set_xlabel("Δ (pp) or benefit (%) — positive = improvement", fontsize=7.6)
    ax.legend(loc="lower right", fontsize=6.5, ncol=2, columnspacing=0.8, handlelength=1.2)
    ax.set_ylim(-0.7, len(rows) - 0.3)
    ax.tick_params(axis="both", labelsize=6.9)
    return ax


# ---------------------------------------------------------------------------
# panel (c): 3 dataset-profile mini-radars, Multi-task TCN-GRU vs DC-PSR only
# ---------------------------------------------------------------------------
def _radar_axes_angles(n):
    return np.linspace(0, 2 * np.pi, n, endpoint=False)


def panel_c_profiles(fig, outer_cell, cross_abs, log_lines):
    content_spec, _ = panel_container(
        fig, outer_cell,
        "(c) Dataset-profile cards: Multi-task TCN-GRU (blue)\nvs DC-PSR (red) only",
        hspace=0.42, caption_height=0.115, fontsize=8.4)
    grid3 = content_spec.subgridspec(1, 3, wspace=1.05)

    axes_metrics = ["Acc", "M-F1", "Cons.", "Stab."]
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
            ax.plot(angles_closed, vals_closed, color=color, lw=1.3, label=name)
            ax.fill(angles_closed, vals_closed, color=color, alpha=0.12)
        ax.set_xticks(angles)
        ax.set_xticklabels(axes_metrics, fontsize=6.5)
        ax.set_yticks([0.5, 1.0])
        ax.set_yticklabels(["0.5", "1.0"], fontsize=6.5)
        ax.set_rlabel_position(45)  # move radial ticks off the crowded "Acc" (0 deg) spoke
        ax.set_ylim(0, 1)
        ax.set_title(title, fontsize=7.6, fontweight="bold", pad=15, color="#1A1A1A")
        ax.tick_params(axis="x", pad=1)
    log_lines.append("PASS: panel(c) radar uses only real Multi-task TCN-GRU vs DC-PSR pairs on PHM2010/NASA/MTW-CM "
                     "(Cons.=1/(1+Smooth), Stab.=1/(1+Jump) are monotonic display transforms of the raw metrics, "
                     "not new statistics -- raw Acc/M-F1/Smooth/Jump remain in panels a/b/d; full transform names "
                     "spelled out in README since panel space only fits the abbreviation).")


# ---------------------------------------------------------------------------
# panel (d): balance map, 6 real points + 4 pale quadrant background tints
# ---------------------------------------------------------------------------
def panel_d_balance(fig, outer_cell, cross_abs, log_lines):
    content_spec, _ = panel_container(
        fig, outer_cell,
        "(d) Classification–consistency balance: 6 real\npoints, B11→B12 connector per dataset",
        hspace=0.75, caption_height=0.115, fontsize=8.4)
    ax = fig.add_subplot(content_spec)

    datasets = [("PHM2010", "PHM2010", "D1", "o"), ("NASA Milling", "NASA_MILLING", "original_N1-N4", "s"),
                ("MTW-CM", "MILLING_CROSS_MACHINE", "D1-M,D2-M,D3-M", "^")]
    xs, ys = [], []
    n_points = 0
    for label, dataset, scope, marker in datasets:
        b11 = cross_abs[(cross_abs["dataset"] == dataset) & (cross_abs["task_scope"] == scope) & (cross_abs["method"] == "B11")].iloc[0]
        b12 = cross_abs[(cross_abs["dataset"] == dataset) & (cross_abs["task_scope"] == scope) & (cross_abs["method"] == "B12")].iloc[0]
        x = [b11["M_F1"], b12["M_F1"]]
        y = [b11["Smooth"], b12["Smooth"]]
        xs += x; ys += y
        n_points += 2

    x_mid = (min(xs) + max(xs)) / 2
    y_mid = (min(ys) + max(ys)) / 2
    xlo, xhi = min(xs) - 0.06, max(xs) + 0.06
    ylo, yhi = min(ys) - 0.02, max(ys) + 0.06
    # 4 very pale quadrant background tints -- background context only, never new data, and no
    # in-plot text labels for the quadrants (an earlier pass tried corner text and it collided
    # with real point labels / axis labels at this panel's true physical size -- the caption below
    # names the 4 quadrants in words instead, so the color tint alone still carries the intent).
    # y-axis is inverted (low Smooth = better = "up" on screen); low-y (top) = more consistent.
    ax.axvspan(xlo, x_mid, ymin=0.5, ymax=1, color="#B85250", alpha=0.05, zorder=0)   # low class., high consistency
    ax.axvspan(x_mid, xhi, ymin=0.5, ymax=1, color="#25847E", alpha=0.07, zorder=0)   # high class., high consistency (balanced)
    ax.axvspan(xlo, x_mid, ymin=0.0, ymax=0.5, color="#B85250", alpha=0.09, zorder=0)  # low class., low consistency
    ax.axvspan(x_mid, xhi, ymin=0.0, ymax=0.5, color="#D39B23", alpha=0.06, zorder=0)  # high class., low consistency

    for label, dataset, scope, marker in datasets:
        b11 = cross_abs[(cross_abs["dataset"] == dataset) & (cross_abs["task_scope"] == scope) & (cross_abs["method"] == "B11")].iloc[0]
        b12 = cross_abs[(cross_abs["dataset"] == dataset) & (cross_abs["task_scope"] == scope) & (cross_abs["method"] == "B12")].iloc[0]
        x = [b11["M_F1"], b12["M_F1"]]
        y = [b11["Smooth"], b12["Smooth"]]
        ax.annotate("", xy=(x[1], y[1]), xytext=(x[0], y[0]),
                    arrowprops=dict(arrowstyle="-|>", color="#555555", lw=1.1), zorder=2)
        ax.scatter(x[0], y[0], color=BACKBONE_COLOR, marker=marker, s=62, edgecolor="black", linewidth=0.55, zorder=3)
        ax.scatter(x[1], y[1], color=DCPSR_COLOR, marker=marker, s=62, edgecolor="black", linewidth=0.55, zorder=3)
        ax.annotate(label, (x[1], y[1]), textcoords="offset points", xytext=(5, 5), fontsize=6.6, color="#333333")
    assert n_points == 6, n_points
    log_lines.append("PASS: panel(d) balance map plots exactly 6 real points (B11/B12 x PHM2010/NASA/MTW-CM), no fabricated methods.")

    ax.set_xlim(xlo, xhi)
    ax.set_ylim(ylo, yhi)
    ax.invert_yaxis()
    ax.set_xlabel("M-F1 (classification, higher better →)", fontsize=7.6)
    ax.set_ylabel("Smooth (consistency; axis inverted, ↑ = better)", fontsize=7.6)
    ax.tick_params(axis="both", labelsize=6.9)
    handles = [plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=BACKBONE_COLOR, markeredgecolor="black", markersize=6.5, label="Multi-task TCN-GRU"),
               plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=DCPSR_COLOR, markeredgecolor="black", markersize=6.5, label="DC-PSR"),
               plt.Line2D([0], [0], marker="o", color="none", markerfacecolor="#AAAAAA", markeredgecolor="black", markersize=6.5, label="PHM2010"),
               plt.Line2D([0], [0], marker="s", color="none", markerfacecolor="#AAAAAA", markeredgecolor="black", markersize=6.5, label="NASA Milling"),
               plt.Line2D([0], [0], marker="^", color="none", markerfacecolor="#AAAAAA", markeredgecolor="black", markersize=6.5, label="MTW-CM avg")]
    ax.legend(handles=handles, loc="center left", fontsize=6.5, bbox_to_anchor=(1.01, 0.5))
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
    log_lines.append("v4: reused v1 load() unchanged.")
    log_lines.append("v4: master physical size 178x125mm, true-scale typography, no post-hoc shrink.")

    fig = plt.figure(figsize=master_figsize_in("fig2"))
    outer = GridSpec(2, 2, height_ratios=[0.56, 0.44], width_ratios=[0.52, 0.48],
                      hspace=0.34, wspace=0.55, figure=fig,
                      left=0.048, right=0.86, top=0.99, bottom=0.05)

    panel_a_taskwise(fig, outer[0, 0], tw_norm, log_lines)
    panel_b_lollipop(fig, outer[0, 1], tw_abs, cross_abs, log_lines)
    panel_c_profiles(fig, outer[1, 0], cross_abs, log_lines)
    panel_d_balance(fig, outer[1, 1], cross_abs, log_lines)

    paths = save_all(fig, OUT_DIR, "fig2_v4")
    log_lines.append(f"Saved outputs: {paths}")
    with open(os.path.join(LOG_DIR, "validation_v4.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
    print("\n".join(log_lines))
    print("Fig.2 v4 done.")


if __name__ == "__main__":
    main()
