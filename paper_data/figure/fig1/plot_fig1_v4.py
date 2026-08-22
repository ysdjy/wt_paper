"""
Fig.1 v4 (paper Fig. 4-2): PHM2010 D1 core-task overall performance -- publication-grade
true-physical-size refinement (178 x 120 mm master size).

DATA UNCHANGED FROM v1/v2/v3: imports v1's load(), build_heatmap_table(), validate_headline(),
load_predictions() directly. Only the visualization layer changed again. See
paper_data/figure/V4_DESIGN_AUDIT.md for the full rationale and paper_data/figure/fig1/README.md's
"v4" section for what changed vs v3 and why.

Run: python paper_data/figure/fig1/plot_fig1_v4.py
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Rectangle

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_shared"))
from style_v4 import (apply_style, save_all, panel_container, sub_caption, master_figsize_in,
                       METHOD_ORDER, METHOD_COLORS, REPRESENTATIVE_METHODS, REPRESENTATIVE_METHODS_5,
                       STAGE_ORDER, BENEFIT_CMAP, CONFUSION_CMAP, LW_MAIN, LW_AUX)  # noqa: E402
import data_utils as du  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
from plot_fig1 import load, build_heatmap_table, validate_headline, load_predictions, HEATMAP_METRICS  # noqa: E402

HERE = os.path.dirname(__file__)
OUT_DIR = os.path.join(HERE, "outputs")
LOG_DIR = os.path.join(HERE, "logs")
os.makedirs(LOG_DIR, exist_ok=True)


def panel_a_heatmap(fig, outer_cell, merged):
    content_spec, _ = panel_container(fig, outer_cell,
                                       "(a) 9-method × metric performance landscape\non PHM2010 D1 (n=304)",
                                       hspace=0.42, caption_height=0.115, fontsize=8.4)
    inner = content_spec.subgridspec(2, 1, height_ratios=[0.88, 0.12], hspace=0.85)
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
    ax.set_yticklabels(merged["Method"].tolist(), fontsize=6.9)
    ax.set_xticks(np.arange(n_metrics))
    ax.set_xticklabels([f"{lab}{'↑' if d=='higher' else '↓'}" for _, d, lab in HEATMAP_METRICS], fontsize=6.9)
    ax.grid(False)
    for i in range(n_methods):
        for j in range(n_metrics):
            col = HEATMAP_METRICS[j][0]
            v = raw[i, j]
            txt = f"{int(v)}" if col in ("Rev", "Jump") else f"{v:.3f}"
            ax.text(j, i, txt, ha="center", va="center", fontsize=6.3,
                     color="white" if grid[i, j] > 0.55 else "#232323")
    # thin colored row outlines instead of colored tick text (brief explicit requirement)
    for i, m in enumerate(merged["Method"]):
        if m == "DC-PSR":
            ax.add_patch(Rectangle((-0.5, i - 0.5), n_metrics, 1, fill=False,
                                    edgecolor=METHOD_COLORS["DC-PSR"], linewidth=1.3, zorder=5))
        elif m == "Multi-task TCN-GRU":
            ax.add_patch(Rectangle((-0.5, i - 0.5), n_metrics, 1, fill=False,
                                    edgecolor=METHOD_COLORS["Multi-task TCN-GRU"], linewidth=1.3, zorder=5))

    cbar = plt.colorbar(im, cax=cbar_ax, orientation="horizontal")
    cbar.set_label("benefit", fontsize=6.2, labelpad=1)
    cbar.ax.tick_params(labelsize=6.5, pad=1)
    cbar.set_ticks([0, 1])
    cbar.set_ticklabels(["low", "high"])
    return ax


def panel_b_confusion(fig, outer_cell, predictions_by_method):
    content_spec, _ = panel_container(
        fig, outer_cell,
        "(b) Representative confusion matrices\n(rows=true, cols=predicted; row-normalized)",
        hspace=0.42, caption_height=0.115, fontsize=8.4)
    # reserve a slim column on the right for one shared colorbar
    body_cbar = content_spec.subgridspec(1, 2, width_ratios=[0.90, 0.10], wspace=0.14)
    body, cbar_col = body_cbar[0], body_cbar[1]
    grid2x2 = body.subgridspec(2, 2, wspace=0.30, hspace=0.62)

    axes = []
    im_ref = None
    for idx, method in enumerate(REPRESENTATIVE_METHODS):
        r, c = divmod(idx, 2)
        ax = fig.add_subplot(grid2x2[r, c])
        axes.append(ax)
        # Short single-line label tied to its own axes via set_title(y<0) rather than another
        # nested GridSpec level -- robust because it's positioned relative to the axes transform
        # itself (moves correctly with the axes under any layout), not a separately-guessed cell.
        ax.set_title(method, y=-0.34, fontsize=7.2, color=METHOD_COLORS.get(method, "#333333"),
                     fontweight="bold", pad=0)
        dfp = predictions_by_method[method]
        counts, row_norm = du.confusion_counts(dfp["true_stage"].values, dfp["pred_stage"].values, labels=STAGE_ORDER)
        im = ax.imshow(row_norm, cmap=CONFUSION_CMAP, vmin=0, vmax=1, aspect="equal")
        im_ref = im
        for i in range(3):
            for j in range(3):
                color = "white" if row_norm[i, j] > 0.55 else "#232323"
                ax.text(j, i, f"{row_norm[i, j]:.2f}\n({counts[i, j]})", ha="center", va="center",
                         fontsize=6.5, color=color)
        ax.set_xticks(range(3)); ax.set_xticklabels(["E", "M", "L"], fontsize=6.6)
        ax.set_yticks(range(3)); ax.set_yticklabels(["E", "M", "L"], fontsize=6.6)
        ax.grid(False)
        ax.tick_params(length=1.6)

    cax = fig.add_subplot(cbar_col)
    cbar = plt.colorbar(im_ref, cax=cax)
    cbar.set_label("proportion", fontsize=6.2, labelpad=2)
    cbar.ax.tick_params(labelsize=6.5)
    return axes


def panel_c_diagnostics(fig, outer_cell, merged, d1, ci_pair):
    content_spec, _ = panel_container(
        fig, outer_cell,
        "(c) Middle-stage recognition & trajectory-consistency landscape,\nrepresentative methods",
        hspace=0.62, caption_height=0.10, fontsize=8.4)

    reps = REPRESENTATIVE_METHODS_5
    sub = merged[merged["Method"].isin(reps)].copy()
    sub["Method"] = pd.Categorical(sub["Method"], categories=reps, ordered=True)
    sub = sub.sort_values("Method")

    ax = fig.add_subplot(content_spec)
    x = np.arange(len(reps))
    width = 0.19

    ax.bar(x - 1.5 * width, sub["M_Precision"], width=width, color="#2F6FB3", label="M-Pre ↑")
    ax.bar(x - 0.5 * width, sub["M_Rec"], width=width, color="#2E8B57", label="M-Rec ↑")
    ax.bar(x + 0.5 * width, sub["M_to_E"], width=width, color="#E76F51", alpha=0.55,
           edgecolor="#E76F51", hatch="////", label="M→E ↓")
    ax.bar(x + 1.5 * width, sub["M_to_L"], width=width, color="#D39B23", alpha=0.55,
           edgecolor="#D39B23", hatch="////", label="M→L ↓")
    ax.set_ylabel("Score (0–1 metrics)")
    ax.set_ylim(0, 1.05)
    ax.set_xticks(x)
    # Rev/Jump folded into the x-tick label itself (2nd line) instead of a floating annotation --
    # avoids any collision with the legend/inset above, and keeps every real count traceable.
    xtick_labels = []
    for _, r in sub.iterrows():
        rev, jump = int(r["Rev"]), int(r["Jump"])
        xtick_labels.append(f"{r['Method']}\n(Rev={rev}, Jump={jump})" if (rev or jump) else str(r["Method"]))
    ax.set_xticklabels(xtick_labels, fontsize=6.5)

    ax2 = ax.twinx()
    ax2.plot(x, sub["Smooth"], color="#175E5A", lw=LW_MAIN, marker="D", ms=4.2, zorder=5, label="Smooth ↓")
    for xi, v in zip(x, sub["Smooth"]):
        ax2.annotate(f"{v:.3f}", (xi, v), textcoords="offset points", xytext=(0, 5),
                     ha="center", fontsize=6.5, color="#175E5A")
    ax2.set_ylabel("Smooth ↓ (lower better)", color="#175E5A", fontsize=7.6)
    ax2.set_ylim(0, sub["Smooth"].max() * 1.9)
    ax2.tick_params(axis="y", labelcolor="#175E5A", labelsize=6.6)
    ax2.grid(False)

    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=6.5, ncol=5, columnspacing=0.7,
              handlelength=1.3, bbox_to_anchor=(0.0, 1.14))

    # --- small bootstrap-CI inset (Acc, representative methods) in reclaimed corner whitespace ---
    inset = ax.inset_axes([0.68, 0.60, 0.31, 0.36])
    inset.set_facecolor("white")
    inset.patch.set_alpha(1.0)
    inset.set_zorder(10)
    ci_rows = []
    for m in reps:
        if m in ci_pair["Method"].values:
            ci_rows.append(ci_pair[ci_pair["Method"] == m].iloc[0])
        else:
            ci_rows.append(d1[d1["Method"] == m].iloc[0])
    for yi, r in enumerate(ci_rows):
        lo, hi, mid = r["Acc_CI_low"] * 100, r["Acc_CI_high"] * 100, r["Acc"] * 100
        color = METHOD_COLORS.get(r["Method"], "#555555")
        inset.plot([lo, hi], [yi, yi], color=color, lw=1.4, solid_capstyle="round")
        inset.plot(mid, yi, "o", color=color, ms=2.6, mec="black", mew=0.2)
    inset.set_yticks(range(len(ci_rows)))
    inset.set_yticklabels([r["Method"] for r in ci_rows], fontsize=6.5)
    inset.set_xlabel("Acc % (95% CI)", fontsize=6.5, labelpad=1)
    inset.tick_params(axis="x", labelsize=6.5, length=1.5)
    inset.tick_params(axis="y", length=1.5)
    inset.set_title("bootstrap 95% CI", fontsize=6.6, pad=2)
    inset.grid(True, lw=0.3, alpha=0.25)
    for spine in inset.spines.values():
        spine.set_linewidth(0.5)
    return ax


def main():
    apply_style()
    d1, acc_cons, ci_pair, tw_d1 = load()
    log_lines = []
    merged = build_heatmap_table(d1, tw_d1, log_lines)
    validate_headline(merged, log_lines)
    predictions_by_method = {m: load_predictions(m) for m in REPRESENTATIVE_METHODS}
    for m, df in predictions_by_method.items():
        assert len(df) == 304
    log_lines.append("v4: reused v1 load()/build_heatmap_table()/validate_headline()/load_predictions() unchanged.")
    log_lines.append("v4: master physical size 178x120mm (7.008x4.724in), true-scale typography, no post-hoc shrink.")

    fig = plt.figure(figsize=master_figsize_in("fig1"))
    outer = GridSpec(2, 1, height_ratios=[0.565, 0.435], hspace=0.30, figure=fig,
                      left=0.065, right=0.985, top=0.99, bottom=0.075)
    top_row = outer[0].subgridspec(1, 2, width_ratios=[0.58, 0.42], wspace=0.14)

    panel_a_heatmap(fig, top_row[0], merged)
    panel_b_confusion(fig, top_row[1], predictions_by_method)
    panel_c_diagnostics(fig, outer[1], merged, d1, ci_pair)

    paths = save_all(fig, OUT_DIR, "fig1_v4")
    log_lines.append(f"Saved outputs: {paths}")
    with open(os.path.join(LOG_DIR, "validation_v4.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
    print("\n".join(log_lines))
    print("Fig.1 v4 done.")


if __name__ == "__main__":
    main()
