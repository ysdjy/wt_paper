"""
Fig.2 v2 (paper Fig. 4-3): cross-condition / cross-dataset generalization -- reference-style
visual reconstruction.

DATA AND STATISTICS ARE UNCHANGED FROM v1 (plot_fig2.py): this script imports v1's load()
function directly, and every panel re-derives its numbers with the SAME formulas v1 uses (copied
verbatim, including v1's np.isclose validation assertions), so v2 is independently self-validating
against the same headline numbers rather than just visually mimicking v1. Only the visualization
layer (layout, palette, panel captions, spacing) is new. See paper_data/figure/fig2/README.md for
what changed and why, and reference/SOURCE.md for exactly what was/wasn't learned from the two
style-reference mockups.

Run: python paper_data/figure/fig2/plot_fig2_v2.py
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_shared"))
from style_v2 import (apply_style, save_all, panel_letter, panel_caption, figure_caption,
                       METHOD_ORDER, METHOD_COLORS, BENEFIT_CMAP, DIVERGING_CMAP)  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
from plot_fig2 import load, PHM_TASKS, HEATMAP_METRICS  # noqa: E402

HERE = os.path.dirname(__file__)
OUT_DIR = os.path.join(HERE, "outputs")
LOG_DIR = os.path.join(HERE, "logs")
os.makedirs(LOG_DIR, exist_ok=True)


def group_caption(fig, axes, text, pad=0.05, fontsize=8.8):
    """Same idea as style_v2.panel_caption but centered under a GROUP of axes (e.g. the 3
    per-task heatmap sub-panels that together form one logical panel)."""
    fig.canvas.draw()
    x0 = min(ax.get_position().x0 for ax in axes)
    x1 = max(ax.get_position().x1 for ax in axes)
    y0 = min(ax.get_position().y0 for ax in axes)
    fig.text((x0 + x1) / 2, y0 - pad, text, ha="center", va="top", fontsize=fontsize)


def panel_taskwise_heatmap(fig, gs_row, tw_norm, log_lines):
    gs3 = GridSpecFromSubplotSpec(1, 3, subplot_spec=gs_row, wspace=0.55)
    axes = [fig.add_subplot(gs3[i]) for i in range(3)]
    for ax, task in zip(axes, PHM_TASKS):
        sub = tw_norm[tw_norm["Task"] == task]
        methods = [m for m in METHOD_ORDER if m in sub["Method"].unique()]
        grid = np.zeros((len(methods), len(HEATMAP_METRICS)))
        raw = np.zeros_like(grid)
        for j, metric in enumerate(HEATMAP_METRICS):
            for i, m in enumerate(methods):
                row = sub[(sub["Method"] == m) & (sub["metric"] == metric)]
                grid[i, j] = row["normalized_score"].values[0]
                raw[i, j] = row["absolute_value"].values[0]
        im = ax.imshow(grid, aspect="auto", cmap=BENEFIT_CMAP, vmin=0, vmax=1)
        ax.set_yticks(np.arange(len(methods)))
        ax.set_yticklabels(methods if task == "D1" else [""] * len(methods), fontsize=6.5)
        ax.set_xticks(np.arange(3))
        ax.set_xticklabels(["Acc↑", "M-F1↑", "Smooth↓"], fontsize=7)
        ax.grid(False)
        for i in range(len(methods)):
            for j in range(3):
                ax.text(j, i, f"{raw[i, j]:.3f}", ha="center", va="center", fontsize=5.6,
                         color="white" if grid[i, j] > 0.55 else "#2A2A2A")
        # orange (DC-PSR accent) row outline, borrowed from the reference mockup's emphasis style
        dcpsr_row = methods.index("DC-PSR")
        rect = plt.Rectangle((-0.5, dcpsr_row - 0.5), 3, 1, fill=False,
                              edgecolor=METHOD_COLORS["DC-PSR"], linewidth=2.0, zorder=5)
        ax.add_patch(rect)
        ax.text(0.5, 1.06, task, transform=ax.transAxes, fontsize=9, fontweight="bold", ha="center")
        best_method = sub[(sub["metric"] == "Acc")].sort_values("absolute_value", ascending=False)["Method"].iloc[0]
        log_lines.append(f"{task}: best Acc = {best_method}")
    panel_letter(axes[0], "a")
    n_unique_best = tw_norm[tw_norm["metric"] == "Acc"].sort_values(["Task", "absolute_value"]).groupby("Task").tail(1)["Method"].nunique()
    log_lines.append(f"PASS: {n_unique_best} distinct methods top Acc across D1/D2/D3 (target-condition dependence, no single winner if >1).")
    group_caption(fig, axes, "Within-task normalized performance, D1/D2/D3 × 9 methods\n"
                              "(color = within-task-and-metric benefit; numbers = raw values; outline = DC-PSR)")


def panel_paired_delta(fig, ax, tw_abs, log_lines):
    bb = tw_abs[tw_abs["Method"] == "Multi-task TCN-GRU"].set_index("Task")
    dc = tw_abs[tw_abs["Method"] == "DC-PSR"].set_index("Task")
    rows = []
    for task in PHM_TASKS:
        d_acc = (dc.loc[task, "Acc"] - bb.loc[task, "Acc"]) * 100
        d_mf1 = (dc.loc[task, "M_F1"] - bb.loc[task, "M_F1"]) * 100
        d_mrec = (dc.loc[task, "M_Recall"] - bb.loc[task, "M_Recall"]) * 100
        smooth_benefit_pct = (bb.loc[task, "Smooth"] - dc.loc[task, "Smooth"]) / bb.loc[task, "Smooth"] * 100
        rows.append((task, d_acc, d_mf1, d_mrec, smooth_benefit_pct))
    df = pd.DataFrame(rows, columns=["Task", "dAcc_pp", "dM_F1_pp", "dM_Rec_pp", "Smooth_benefit_pct"])

    expected = {"D1": (-0.33, -0.39, 0.0, 20.5), "D2": (-0.33, -0.61, None, 6.6), "D3": (0.66, 1.10, 1.80, -5.7)}
    for task, d_acc, d_mf1, d_mrec, sm in rows:
        e_acc, e_mf1, e_mrec, e_sm = expected[task]
        assert np.isclose(d_acc, e_acc, atol=0.1), f"{task} dAcc: got {d_acc:.2f}, expected {e_acc}"
        assert np.isclose(d_mf1, e_mf1, atol=0.15), f"{task} dM_F1: got {d_mf1:.2f}, expected {e_mf1}"
        if e_mrec is not None:
            assert np.isclose(d_mrec, e_mrec, atol=0.15), f"{task} dM_Rec: got {d_mrec:.2f}, expected {e_mrec}"
        assert np.isclose(sm, e_sm, atol=1.0), f"{task} Smooth benefit%: got {sm:.2f}, expected {e_sm}"
        log_lines.append(f"PASS: PHM {task} Multi-task TCN-GRU->DC-PSR: dAcc={d_acc:.2f}pp, dM-F1={d_mf1:.2f}pp, "
                          f"dM-Rec={d_mrec:.2f}pp, Smooth_benefit={sm:.2f}% (matches design-doc narrative).")

    x = np.arange(len(PHM_TASKS))
    width = 0.2
    metrics_plot = [("dAcc_pp", "ΔAcc (pp)", METHOD_COLORS["Multi-task TCN-GRU"]),
                     ("dM_F1_pp", "ΔM-F1 (pp)", "#2A8C7A"),
                     ("dM_Rec_pp", "ΔM-Rec (pp)", "#D9A441"),
                     ("Smooth_benefit_pct", "Smooth benefit (%)", METHOD_COLORS["DC-PSR"])]
    for i, (col, label, color) in enumerate(metrics_plot):
        ax.bar(x + (i - 1.5) * width, df[col], width=width, color=color, label=label)
    ax.axhline(0, color="black", lw=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels(PHM_TASKS)
    ax.set_ylabel("Δ (pp) or benefit (%)")
    ax.legend(loc="upper right", fontsize=6.5, ncol=1)
    panel_letter(ax, "b")
    panel_caption(fig, ax, "Multi-task TCN-GRU → DC-PSR paired delta, PHM D1/D2/D3\n"
                           "(Smooth benefit = Smooth_backbone − Smooth_DC-PSR; raw Smooth never itself flipped)")


def panel_cross_dataset_delta(fig, ax, cross_abs, log_lines):
    scopes = [("PHM2010", "D1"), ("NASA_MILLING", "original_N1-N4"),
              ("MILLING_CROSS_MACHINE", "D1-M"), ("MILLING_CROSS_MACHINE", "D2-M"),
              ("MILLING_CROSS_MACHINE", "D3-M"), ("MILLING_CROSS_MACHINE", "D1-M,D2-M,D3-M")]
    row_labels = ["PHM2010\nD1", "NASA Milling\nN1-N4 avg", "MTW-CM\nD1-M", "MTW-CM\nD2-M",
                  "MTW-CM\nD3-M", "MTW-CM\n3-task avg"]
    rows = []
    for dataset, scope in scopes:
        b11 = cross_abs[(cross_abs["dataset"] == dataset) & (cross_abs["task_scope"] == scope) & (cross_abs["method"] == "B11")].iloc[0]
        b12 = cross_abs[(cross_abs["dataset"] == dataset) & (cross_abs["task_scope"] == scope) & (cross_abs["method"] == "B12")].iloc[0]
        d_acc = (b12["Acc"] - b11["Acc"]) * 100
        d_mf1 = (b12["M_F1"] - b11["M_F1"]) * 100
        smooth_benefit_pct = (b11["Smooth"] - b12["Smooth"]) / b11["Smooth"] * 100 if b11["Smooth"] > 0 else 0.0
        jump_benefit_pct = (b11["Jump"] - b12["Jump"]) / b11["Jump"] * 100 if b11["Jump"] > 0 else 0.0
        rows.append([d_acc, d_mf1, smooth_benefit_pct, jump_benefit_pct])
    grid = np.array(rows)

    n_mf1, s_ben = grid[1, 1], grid[1, 2]
    assert np.isclose(n_mf1, 5.86, atol=0.5), n_mf1
    assert np.isclose(s_ben, 35.0, atol=1.5), s_ben
    log_lines.append(f"PASS: NASA B11->B12 M-F1 delta={n_mf1:.2f}pp (~5.86), Smooth benefit={s_ben:.2f}% (~35.0).")
    n_mf1_mtw, s_ben_mtw = grid[5, 1], grid[5, 2]
    assert np.isclose(n_mf1_mtw, 10.04, atol=0.5), n_mf1_mtw
    assert np.isclose(s_ben_mtw, 23.9, atol=1.5), s_ben_mtw
    log_lines.append(f"PASS: MTW-CM 3-task avg B11->B12 M-F1 delta={n_mf1_mtw:.2f}pp (~10.04), Smooth benefit={s_ben_mtw:.2f}% (~23.9).")
    j_ben_mtw = grid[5, 3]
    assert np.isclose(j_ben_mtw, 82.5, atol=1.5), j_ben_mtw
    log_lines.append(f"PASS: MTW-CM 3-task avg Jump benefit={j_ben_mtw:.2f}% (~82.5).")

    cols = ["ΔAcc (pp)", "ΔM-F1 (pp)", "Smooth benefit (%)", "Jump benefit (%)"]
    color_grid = np.zeros_like(grid)
    for j in range(grid.shape[1]):
        col_vmax = np.abs(grid[:, j]).max()
        color_grid[:, j] = grid[:, j] / col_vmax if col_vmax > 0 else 0.0
    im = ax.imshow(color_grid, aspect="auto", cmap=DIVERGING_CMAP, vmin=-1, vmax=1)
    ax.set_yticks(np.arange(len(row_labels)))
    ax.set_yticklabels(row_labels, fontsize=7)
    ax.set_xticks(np.arange(len(cols)))
    ax.set_xticklabels(cols, fontsize=7.5)
    ax.grid(False)
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            txt_color = "white" if abs(color_grid[i, j]) > 0.75 else "#2A2A2A"
            ax.text(j, i, f"{grid[i, j]:+.2f}", ha="center", va="center", fontsize=7, color=txt_color)
    panel_letter(ax, "c")
    cbar = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label("within-column benefit\n(normalized, diverging)", fontsize=6.5)
    cbar.ax.tick_params(labelsize=6)
    panel_caption(fig, ax, "Cross-dataset Multi-task TCN-GRU → DC-PSR (B11→B12) delta matrix\n"
                           "(teal = improvement, terracotta = regression; color per-column normalized since units mix pp and %)")


def main():
    apply_style()
    tw_abs, tw_norm, cross_abs, cross_delta_ref = load()
    log_lines = []

    assert set(tw_abs["Task"].unique()) == set(PHM_TASKS)
    assert len(tw_abs) == 27, f"expected 27 rows (3 tasks x 9 methods), got {len(tw_abs)}"
    assert set(cross_abs["dataset"].unique()) == {"PHM2010", "NASA_MILLING", "MILLING_CROSS_MACHINE"}
    assert "MIMII" not in cross_abs["dataset"].unique()
    log_lines.append("PASS: taskwise_absolute has 27 rows (3 PHM tasks x 9 methods); cross_dataset_absolute uses "
                     "{PHM2010, NASA_MILLING, MILLING_CROSS_MACHINE} only, no legacy 'MIMII' label present.")

    fig = plt.figure(figsize=(13.6, 12.8))
    # left/right/top/bottom fixed HERE at construction (see fig1_v2's documented bug: never call
    # fig.subplots_adjust() after panels are drawn/captioned, or captions detach from their axes).
    gs = GridSpec(3, 2, height_ratios=[1.55, 1.0, 1.15], hspace=0.72, wspace=0.35, figure=fig,
                  left=0.075, right=0.97, top=0.97, bottom=0.145)

    panel_taskwise_heatmap(fig, gs[0, :], tw_norm, log_lines)

    ax_b = fig.add_subplot(gs[1, :])
    panel_paired_delta(fig, ax_b, tw_abs, log_lines)

    ax_c = fig.add_subplot(gs[2, :])
    panel_cross_dataset_delta(fig, ax_c, cross_abs, log_lines)

    figure_caption(fig, "鲁棒性", subtitle="Fig. 4-3  Cross-condition and cross-dataset generalization landscape")

    paths = save_all(fig, OUT_DIR, "fig2_v2_reference_style")
    log_lines.append(f"Saved outputs: {paths}")

    with open(os.path.join(LOG_DIR, "validation_v2.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
    print("\n".join(log_lines))
    print("Fig.2 v2 done.")


if __name__ == "__main__":
    main()
