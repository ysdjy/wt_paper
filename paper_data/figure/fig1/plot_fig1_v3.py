"""
Fig.1 v3 (paper Fig. 4-2): PHM2010 D1 core-task overall performance -- dense landscape
reconstruction.

DATA AND STATISTICS ARE UNCHANGED FROM v1/v2: imports v1's load(), build_heatmap_table(),
validate_headline(), load_predictions() directly. Only layout changed:
  - landscape canvas (15.5 x 10.0), not v2's portrait 13.8 x 15.5
  - 2-row dashboard: top = heatmap (58%) + 2x2 confusion matrices (42%); bottom = one composite
    middle-stage/transition/consistency diagnostics panel (3 internal blocks)
  - every panel caption "(x) description" sits BELOW its panel via style_v3.panel_container's
    nested subgridspec (geometrically locked, no fig.text() bbox guessing)
  - no figure-level title anywhere (v2's bottom "主比较" caption is also gone -- the Chinese name
    lives only in the folder/README/filename now, per this round's explicit instruction)
  - Pareto scatter and bootstrap-CI strip (v2 panels b/c) are DROPPED from the main composite this
    round per the task brief ("不要让它们再单独占整行... 本轮不要因为它们破坏 Fig1 的整体构图") --
    left for a future supplementary figure, not deleted from the codebase (v1/v2 keep them).

Style reference: paper_data/figure/fig1/视觉参考效果图/*.png -- LAYOUT ONLY (panel proportions,
heatmap+2x2-confusion top row, 3-block bottom diagnostics row). Every number, color scale, and
method roster comes from paper_data, not from the mockup (whose own data is fictional).

Run: python paper_data/figure/fig1/plot_fig1_v3.py
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_shared"))
from style_v3 import (apply_style, save_all, panel_container, sub_caption,
                       METHOD_ORDER, METHOD_COLORS, REPRESENTATIVE_METHODS, STAGE_ORDER,
                       BENEFIT_CMAP)  # noqa: E402
import data_utils as du  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
from plot_fig1 import load, build_heatmap_table, validate_headline, load_predictions, HEATMAP_METRICS  # noqa: E402

HERE = os.path.dirname(__file__)
OUT_DIR = os.path.join(HERE, "outputs")
LOG_DIR = os.path.join(HERE, "logs")
os.makedirs(LOG_DIR, exist_ok=True)


def panel_a_heatmap(fig, outer_cell, merged):
    content_spec, _ = panel_container(fig, outer_cell,
                                       "(a) 9-method × metric performance landscape on PHM2010 D1 (n=304)",
                                       hspace=0.14)
    # explicit sub-row for the colorbar (instead of plt.colorbar's auto space-stealing, which
    # does not respect the caption strip reserved by panel_container) -- same geometric-lock
    # pattern as panel_container itself.
    inner = content_spec.subgridspec(2, 1, height_ratios=[0.86, 0.14], hspace=0.55)
    ax = fig.add_subplot(inner[0])
    cbar_ax = fig.add_subplot(inner[1])

    n_methods = len(merged)
    n_metrics = len(HEATMAP_METRICS)
    grid = np.zeros((n_methods, n_metrics))
    raw = np.zeros((n_methods, n_metrics))
    for j, (col, direction, _) in enumerate(HEATMAP_METRICS):
        vals = merged[col].values.astype(float)
        raw[:, j] = vals
        vmin, vmax = vals.min(), vals.max()
        norm = np.ones_like(vals) * 0.5 if vmax - vmin < 1e-12 else (vals - vmin) / (vmax - vmin)
        if direction == "lower":
            norm = 1 - norm
        grid[:, j] = norm
    im = ax.imshow(grid, aspect="auto", cmap=BENEFIT_CMAP, vmin=0, vmax=1)
    ax.set_yticks(np.arange(n_methods))
    ax.set_yticklabels(merged["Method"].tolist())
    ax.set_xticks(np.arange(n_metrics))
    ax.set_xticklabels([f"{lab}{'↑' if d=='higher' else '↓'}" for _, d, lab in HEATMAP_METRICS])
    ax.grid(False)
    for i in range(n_methods):
        for j in range(n_metrics):
            col = HEATMAP_METRICS[j][0]
            v = raw[i, j]
            txt = f"{int(v)}" if col in ("Rev", "Jump") else f"{v:.3f}"
            ax.text(j, i, txt, ha="center", va="center", fontsize=6.9,
                     color="white" if grid[i, j] > 0.55 else "#2A2A2A")
    for i, m in enumerate(merged["Method"]):
        if m == "DC-PSR":
            ax.get_yticklabels()[i].set_color(METHOD_COLORS["DC-PSR"])
            ax.get_yticklabels()[i].set_fontweight("bold")
        elif m == "Multi-task TCN-GRU":
            ax.get_yticklabels()[i].set_color(METHOD_COLORS["Multi-task TCN-GRU"])
            ax.get_yticklabels()[i].set_fontweight("bold")
    cbar = plt.colorbar(im, cax=cbar_ax, orientation="horizontal")
    cbar.set_label("within-column benefit (1=best; raw value in cell)", fontsize=6.6, labelpad=2)
    cbar.ax.tick_params(labelsize=6.0, pad=1)
    return ax


def panel_b_confusion(fig, outer_cell, predictions_by_method):
    content_spec, _ = panel_container(fig, outer_cell,
                                       "(b) Representative confusion matrices (rows=true, columns=predicted; row-normalized)")
    grid2x2 = content_spec.subgridspec(2, 2, wspace=0.32, hspace=0.20)

    axes = []
    ims = []
    for idx, method in enumerate(REPRESENTATIVE_METHODS):
        r, c = divmod(idx, 2)
        cell_spec, _ = sub_caption(fig, grid2x2[r, c], method, caption_height=0.16, fontsize=8.2,
                                    caption_color=METHOD_COLORS.get(method, "#333333"))
        ax = fig.add_subplot(cell_spec)
        axes.append(ax)
        dfp = predictions_by_method[method]
        counts, row_norm = du.confusion_counts(dfp["true_stage"].values, dfp["pred_stage"].values, labels=STAGE_ORDER)
        im = ax.imshow(row_norm, cmap=BENEFIT_CMAP, vmin=0, vmax=1)
        ims.append(im)
        for i in range(3):
            for j in range(3):
                color = "white" if row_norm[i, j] > 0.55 else "#2A2A2A"
                ax.text(j, i, f"{row_norm[i, j]:.2f}\n({counts[i, j]})", ha="center", va="center",
                         fontsize=6.0, color=color)
        ax.set_xticks(range(3)); ax.set_xticklabels(["E", "M", "L"], fontsize=6.8)
        ax.set_yticks(range(3)); ax.set_yticklabels(["E", "M", "L"], fontsize=6.8)
        ax.grid(False)
        ax.tick_params(length=2)
    return axes, ims


def panel_c_diagnostics(fig, outer_cell, merged):
    content_spec, _ = panel_container(
        fig, outer_cell,
        "(c) Middle-stage recognition and trajectory-consistency diagnostics, representative methods",
        hspace=0.12)
    grid3 = content_spec.subgridspec(1, 3, width_ratios=[0.40, 0.30, 0.30], wspace=0.38)

    reps = REPRESENTATIVE_METHODS
    tick_labels = {"RF": "RF", "MTF-AViTK": "MTF-AViTK", "Multi-task TCN-GRU": "MT-TCN-GRU", "DC-PSR": "DC-PSR"}
    sub = merged[merged["Method"].isin(reps)].copy()
    sub["Method"] = pd.Categorical(sub["Method"], categories=reps, ordered=True)
    sub = sub.sort_values("Method")

    # --- block 1: M-Pre / M-Rec bars + M->E / M->L lines ---
    ax1 = fig.add_subplot(grid3[0])
    x = np.arange(len(reps))
    width = 0.32
    ax1.bar(x - width / 2, sub["M_Precision"], width=width, color="#3E7C99", label="M-Pre ↑")
    ax1.bar(x + width / 2, sub["M_Rec"], width=width, color="#2A8C7A", label="M-Rec ↑")
    ax1.set_ylabel("Score (higher better)")
    ax1.set_ylim(0, 1.12)
    ax1.set_xticks(x)
    ax1.set_xticklabels([tick_labels[m] for m in reps], rotation=0, ha="center", fontsize=6.8)
    ax2 = ax1.twinx()
    ax2.plot(x, sub["M_to_E"], color="#B0555E", marker="o", ms=4.5, lw=1.3, label="M→E ↓")
    ax2.plot(x, sub["M_to_L"], color="#D9A441", marker="s", ms=4.5, lw=1.3, label="M→L ↓")
    ax2.set_ylabel("Transition error rate (lower better)", fontsize=7.8)
    ax2.set_ylim(0, max(0.35, sub["M_to_E"].max() * 2.4))
    ax2.grid(False)
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="upper right", fontsize=6.5, ncol=1)

    # --- block 2: Rev / Jump ---
    ax3 = fig.add_subplot(grid3[1])
    ax3.bar(x - width / 2, sub["Rev"], width=width, color="#8A8D8F", label="Rev ↓")
    ax3.bar(x + width / 2, sub["Jump"], width=width, color="#C97B3D", label="Jump ↓")
    ax3.set_ylabel("Count (lower better)")
    ax3.set_xticks(x)
    ax3.set_xticklabels([tick_labels[m] for m in reps], rotation=0, ha="center", fontsize=6.8)
    ax3.legend(loc="upper right", fontsize=6.8)

    # --- block 3: Smooth ---
    ax4 = fig.add_subplot(grid3[2])
    colors = [METHOD_COLORS[m] for m in reps]
    ax4.bar(x, sub["Smooth"], width=0.55, color=colors)
    for xi, v in zip(x, sub["Smooth"]):
        ax4.text(xi, v + 0.003, f"{v:.4f}", ha="center", va="bottom", fontsize=6.8)
    ax4.set_ylabel("Smooth (lower better)")
    ax4.set_xticks(x)
    ax4.set_xticklabels([tick_labels[m] for m in reps], rotation=0, ha="center", fontsize=6.8)
    ax4.set_ylim(0, sub["Smooth"].max() * 1.35)

    return ax1, ax3, ax4


def main():
    apply_style()
    d1, acc_cons, ci_pair, tw_d1 = load()
    log_lines = []
    merged = build_heatmap_table(d1, tw_d1, log_lines)
    validate_headline(merged, log_lines)
    predictions_by_method = {m: load_predictions(m) for m in REPRESENTATIVE_METHODS}
    for m, df in predictions_by_method.items():
        assert len(df) == 304
    log_lines.append("v3: reused v1 load()/build_heatmap_table()/validate_headline()/load_predictions() unchanged.")

    fig = plt.figure(figsize=(15.5, 10.0))
    outer = GridSpec(2, 1, height_ratios=[0.565, 0.435], hspace=0.14, figure=fig,
                      left=0.045, right=0.985, top=0.99, bottom=0.03)
    top_row = outer[0].subgridspec(1, 2, width_ratios=[0.58, 0.42], wspace=0.09)

    panel_a_heatmap(fig, top_row[0], merged)
    panel_b_confusion(fig, top_row[1], predictions_by_method)
    panel_c_diagnostics(fig, outer[1], merged)

    paths = save_all(fig, OUT_DIR, "fig1_v3")
    log_lines.append(f"Saved outputs: {paths}")
    with open(os.path.join(LOG_DIR, "validation_v3.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
    print("\n".join(log_lines))
    print("Fig.1 v3 done.")


if __name__ == "__main__":
    main()
