"""
Fig.1 v2 (paper Fig. 4-2): PHM2010 D1 core-task overall performance -- reference-style visual
reconstruction.

DATA AND STATISTICS ARE UNCHANGED FROM v1 (plot_fig1.py): this script imports v1's load(),
build_heatmap_table(), validate_headline(), load_predictions() functions directly rather than
recomputing anything, so the two scripts are guaranteed to plot identical numbers. Only the
visualization layer (layout, palette, panel captions, spacing) is new. See
paper_data/figure/fig1/README.md for what changed and why, and reference/SOURCE.md for exactly
what was (and was not) learned from the style-reference mockup.

Run: python paper_data/figure/fig1/plot_fig1_v2.py
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_shared"))
from style_v2 import (apply_style, save_all, panel_letter, panel_caption, figure_caption,
                       METHOD_ORDER, METHOD_COLORS, REPRESENTATIVE_METHODS, STAGE_ORDER,
                       BENEFIT_CMAP)  # noqa: E402
import data_utils as du  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
from plot_fig1 import load, build_heatmap_table, validate_headline, load_predictions, HEATMAP_METRICS  # noqa: E402

HERE = os.path.dirname(__file__)
OUT_DIR = os.path.join(HERE, "outputs")
LOG_DIR = os.path.join(HERE, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

BACKBONE_COMPARISON_METRICS = [
    ("Acc", "Acc", "higher"), ("MacroF1", "Macro-F1", "higher"), ("M_F1", "M-F1", "higher"),
    ("M_Rec", "M-Rec", "higher"), ("Smooth", "Smooth", "lower"),
]


def panel_heatmap(fig, ax, merged):
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
            ax.text(j, i, txt, ha="center", va="center", fontsize=6.2,
                     color="white" if grid[i, j] > 0.55 else "#2A2A2A")
    for i, m in enumerate(merged["Method"]):
        if m == "DC-PSR":
            ax.get_yticklabels()[i].set_color(METHOD_COLORS["DC-PSR"])
            ax.get_yticklabels()[i].set_fontweight("bold")
        elif m == "Multi-task TCN-GRU":
            ax.get_yticklabels()[i].set_color(METHOD_COLORS["Multi-task TCN-GRU"])
            ax.get_yticklabels()[i].set_fontweight("bold")
    panel_letter(ax, "a")
    cbar = plt.colorbar(im, ax=ax, fraction=0.016, pad=0.008)
    cbar.set_label("within-column benefit\n(1 = best; raw value in cell)", fontsize=6.5)
    cbar.ax.tick_params(labelsize=6)
    panel_caption(fig, ax, "9-method × metric performance landscape on PHM2010 D1 (n=304)")


def panel_pareto(fig, ax, acc_cons):
    order = acc_cons.sort_values("Acc")
    xs = order["Acc"].values * 100
    ys = order["Smooth"].values
    frontier_x, frontier_y = [], []
    best_smooth = np.inf
    for x, y in sorted(zip(xs, ys), key=lambda t: -t[0]):
        if y < best_smooth:
            frontier_x.append(x)
            frontier_y.append(y)
            best_smooth = y
    ax.plot(frontier_x, frontier_y, color="#B7BDC2", lw=1.0, ls="--", zorder=1)

    for _, r in acc_cons.iterrows():
        color = METHOD_COLORS.get(r["Method"], "#888888")
        emphasize = r["Method"] in ("DC-PSR", "Multi-task TCN-GRU")
        ax.scatter(r["Acc"] * 100, r["Smooth"], s=75 if emphasize else 42,
                   color=color, edgecolor="black" if emphasize else "none", linewidth=0.9,
                   zorder=3 if emphasize else 2)
        dx, dy = 0.3, 0.006
        if r["Method"] == "DC-PSR":
            dx, dy = -7.6, 0.008
        elif r["Method"] == "Multi-task TCN-GRU":
            dx, dy = -15.5, -0.012
        ax.annotate(r["Method"], (r["Acc"] * 100 + dx, r["Smooth"] + dy), fontsize=6.4, color=color)
    ax.set_xlabel("Accuracy % (higher better →)")
    ax.set_ylabel("Smooth (lower better ↑ = worse)")
    ax.invert_yaxis()
    panel_letter(ax, "b")
    panel_caption(fig, ax, "Accuracy–consistency trade-off (dashed = non-dominated frontier)")


def panel_backbone_comparison(fig, gs_slot, merged):
    gs5 = GridSpecFromSubplotSpec(1, 5, subplot_spec=gs_slot, wspace=0.65)
    bb = merged[merged["Method"] == "Multi-task TCN-GRU"].iloc[0]
    dc = merged[merged["Method"] == "DC-PSR"].iloc[0]
    axes = []
    for i, (col, label, direction) in enumerate(BACKBONE_COMPARISON_METRICS):
        ax = fig.add_subplot(gs5[i])
        axes.append(ax)
        v_bb, v_dc = bb[col], dc[col]
        ax.plot([0, 1], [v_bb, v_dc], color="#B7BDC2", lw=1.3, zorder=1)
        ax.scatter([0], [v_bb], marker="D", s=48, color=METHOD_COLORS["Multi-task TCN-GRU"],
                   edgecolor="black", linewidth=0.6, zorder=3)
        ax.scatter([1], [v_dc], marker="o", s=52, color=METHOD_COLORS["DC-PSR"],
                   edgecolor="black", linewidth=0.6, zorder=3)
        pad = (max(v_bb, v_dc) - min(v_bb, v_dc)) * 0.9 + 1e-4
        ax.set_ylim(min(v_bb, v_dc) - pad, max(v_bb, v_dc) + pad)
        ax.set_xlim(-0.5, 1.5)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["MT-\nTCN", "DC-\nPSR"], fontsize=6.2)
        ax.set_xlabel(f"{label} {'↑' if direction=='higher' else '↓'}", fontsize=7.3, labelpad=3)
        txt_pad = pad * 0.55
        ax.text(0, v_bb + (txt_pad if v_bb >= v_dc else -txt_pad), f"{v_bb:.4f}" if col == "Smooth" else f"{v_bb:.3f}",
                fontsize=6.0, ha="center", va="bottom" if v_bb >= v_dc else "top", color=METHOD_COLORS["Multi-task TCN-GRU"])
        ax.text(1, v_dc + (txt_pad if v_dc >= v_bb else -txt_pad), f"{v_dc:.4f}" if col == "Smooth" else f"{v_dc:.3f}",
                fontsize=6.0, ha="center", va="bottom" if v_dc >= v_bb else "top", color=METHOD_COLORS["DC-PSR"])
        ax.grid(False)
        ax.tick_params(axis="y", labelsize=6.2)
    panel_letter(axes[0], "c")
    handles = [plt.Line2D([0], [0], marker="D", color="none", markerfacecolor=METHOD_COLORS["Multi-task TCN-GRU"], markeredgecolor="black", markersize=6, label="Multi-task TCN-GRU"),
               plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=METHOD_COLORS["DC-PSR"], markeredgecolor="black", markersize=6, label="DC-PSR")]
    axes[2].legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 1.32), ncol=2, fontsize=6.8, frameon=False)
    panel_caption(fig, axes[2], "Controlled comparison: DC-PSR vs. its Multi-task TCN-GRU backbone")


def panel_confusion(fig, gs_row, predictions_by_method):
    axes = [fig.add_subplot(gs_row[i]) for i in range(4)]
    for i, (ax, method) in enumerate(zip(axes, REPRESENTATIVE_METHODS)):
        dfp = predictions_by_method[method]
        counts, row_norm = du.confusion_counts(dfp["true_stage"].values, dfp["pred_stage"].values, labels=STAGE_ORDER)
        im = ax.imshow(row_norm, cmap=BENEFIT_CMAP, vmin=0, vmax=1)
        for r in range(3):
            for c in range(3):
                color = "white" if row_norm[r, c] > 0.55 else "#2A2A2A"
                ax.text(c, r, f"{row_norm[r, c]:.3f}\n({counts[r, c]})", ha="center", va="center",
                         fontsize=6.0, color=color)
        ax.set_xticks(range(3)); ax.set_xticklabels(["E", "M", "L"], fontsize=7)
        ax.set_yticks(range(3)); ax.set_yticklabels(["E", "M", "L"], fontsize=7)
        ax.grid(False)
        if i == 0:
            ax.set_ylabel("True", fontsize=6.8)
        ax.set_xlabel("Predicted", fontsize=6.5)
        panel_caption(fig, ax, method, fontsize=7.6)
        for lbl in ax.get_xticklabels() + ax.get_yticklabels():
            pass
    panel_letter(axes[0], "d")


def panel_middle_diagnostics(fig, ax, merged):
    reps = ["RF", "MTF-AViTK", "Multi-task TCN-GRU", "DC-PSR"]
    sub = merged[merged["Method"].isin(reps)].copy()
    metrics = [("M_Precision", "M-Pre", "higher"), ("M_Rec", "M-Rec", "higher"),
               ("M_to_E", "M→E", "lower"), ("M_to_L", "M→L", "lower"),
               ("Smooth", "Smooth", "lower")]
    x = np.arange(len(metrics))
    width = 0.2
    for i, m in enumerate(reps):
        r = sub[sub["Method"] == m].iloc[0]
        vals = [r[c] for c, _, _ in metrics]
        ax.bar(x + (i - 1.5) * width, vals, width=width, color=METHOD_COLORS[m], label=m)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{lab} {'↑' if d=='higher' else '↓'}" for _, lab, d in metrics])
    ax.set_ylabel("Value")
    ax.legend(loc="upper right", ncol=4, fontsize=6.6)
    panel_letter(ax, "e")
    panel_caption(fig, ax, "Middle-stage & trajectory-consistency diagnostics, representative methods")


def main():
    apply_style()
    d1, acc_cons, ci_pair, tw_d1 = load()
    log_lines = []
    merged = build_heatmap_table(d1, tw_d1, log_lines)
    validate_headline(merged, log_lines)
    predictions_by_method = {m: load_predictions(m) for m in REPRESENTATIVE_METHODS}
    log_lines.append("v2: reused v1 load()/build_heatmap_table()/validate_headline()/load_predictions() unchanged -- see fig1/logs/validation.txt (v1) for the full numeric validation; this log only records v2-specific layout notes.")

    fig = plt.figure(figsize=(13.8, 15.5))
    # IMPORTANT: left/right/top/bottom are fixed HERE (at GridSpec construction), not via a later
    # fig.subplots_adjust() call -- panel_caption() reads ax.get_position() to place text below
    # each panel, so the final layout must be settled *before* any panel is drawn/captioned, or
    # every caption ends up positioned for a layout that gets reflowed out from under it.
    gs = GridSpec(4, 4, height_ratios=[1.5, 1.05, 1.15, 1.0], hspace=0.95, wspace=0.4, figure=fig,
                  left=0.07, right=0.98, top=0.985, bottom=0.155)

    ax_heat = fig.add_subplot(gs[0, :])
    panel_heatmap(fig, ax_heat, merged)

    ax_pareto = fig.add_subplot(gs[1, :2])
    panel_pareto(fig, ax_pareto, acc_cons)
    panel_backbone_comparison(fig, gs[1, 2:], merged)

    panel_confusion(fig, GridSpecFromSubplotSpec(1, 4, subplot_spec=gs[2, :], wspace=0.4), predictions_by_method)

    ax_diag = fig.add_subplot(gs[3, :])
    panel_middle_diagnostics(fig, ax_diag, merged)

    figure_caption(fig, "主比较", subtitle="Fig. 4-2  Overall performance and discrimination–consistency trade-off on PHM2010 D1")

    paths = save_all(fig, OUT_DIR, "fig1_v2_reference_style")
    log_lines.append(f"Saved outputs: {paths}")
    with open(os.path.join(LOG_DIR, "validation_v2.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
    print("\n".join(log_lines))
    print("Fig.1 v2 done.")


if __name__ == "__main__":
    main()
