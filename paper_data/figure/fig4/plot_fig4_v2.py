"""
Fig.4 v2 (paper Fig. 4-5): ordered degradation semantics -- reference-style visual reconstruction.

DATA AND STATISTICS ARE UNCHANGED FROM v1 (plot_fig4.py): this script reuses v1's load() function
and re-runs the exact same R2/Spearman/MAE and VB-mean validation formulas (copied, not altered)
so the two scripts are guaranteed to plot identical numbers. Only the visualization layer changed.
See paper_data/figure/fig4/README.md for what changed and reference/SOURCE.md for exactly what
was (and was not) learned from the style-reference mockup (figures/fig5_semantics_refined,
panels a/b/c/e only -- its panel (d) is fig5's subject, not fig4's).

Run: python paper_data/figure/fig4/plot_fig4_v2.py
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.collections import LineCollection
from scipy import stats

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_shared"))
from style_v2 import (apply_style, save_all, panel_letter, panel_caption, figure_caption,
                       STAGE_ORDER, STAGE_COLORS, STAGE_LABELS, DEGRADATION_CMAP)  # noqa: E402
import data_utils as du  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
from plot_fig4 import load  # noqa: E402

HERE = os.path.dirname(__file__)
OUT_DIR = os.path.join(HERE, "outputs")
LOG_DIR = os.path.join(HERE, "logs")
os.makedirs(LOG_DIR, exist_ok=True)


def panel_lifecycle(fig, gs_slot, lifecycle):
    lc = lifecycle.sort_values("relative_life").reset_index(drop=True)
    from matplotlib.gridspec import GridSpecFromSubplotSpec
    gsx = GridSpecFromSubplotSpec(2, 1, subplot_spec=gs_slot, height_ratios=[2.0, 1.0], hspace=0.1)
    ax_p = fig.add_subplot(gsx[0])
    ax_q = fig.add_subplot(gsx[1], sharex=ax_p)

    x = lc["relative_life"].values
    stage_ids = lc["true_stage"].values
    seen_start = 0.0
    prev_stage = stage_ids[0]
    zones = []
    for i in range(1, len(x)):
        if stage_ids[i] != prev_stage:
            zones.append((seen_start, x[i - 1], prev_stage))
            seen_start = x[i]
            prev_stage = stage_ids[i]
    zones.append((seen_start, x[-1], prev_stage))
    for start, end, stage in zones:
        ax_p.axvspan(start, end, color=STAGE_COLORS[stage], alpha=0.08, lw=0)
        ax_q.axvspan(start, end, color=STAGE_COLORS[stage], alpha=0.08, lw=0)
    for start, end, stage in zones[:-1]:
        ax_p.axvline(end, color="#8A8D8F", lw=0.7, ls="--", alpha=0.7)
        ax_q.axvline(end, color="#8A8D8F", lw=0.7, ls="--", alpha=0.7)
    for start, end, stage in zones:
        if end - start > 0.08:
            ax_p.text((start + end) / 2, 0.965, f"{STAGE_LABELS[stage]} zone", ha="center", va="top",
                      fontsize=6.6, color=STAGE_COLORS[stage], fontweight="bold")

    ax_p.plot(x, lc["prob_early"], color=STAGE_COLORS["early"], lw=1.3, label="$p_E$")
    ax_p.plot(x, lc["prob_middle"], color=STAGE_COLORS["middle"], lw=1.3, label="$p_M$")
    ax_p.plot(x, lc["prob_late"], color=STAGE_COLORS["late"], lw=1.3, label="$p_L$")
    ax_p.set_ylabel("Probability")
    ax_p.set_ylim(0, 1.03)
    ax_p.legend(loc="upper left", ncol=3, fontsize=7.2, bbox_to_anchor=(0.01, 0.86), frameon=False)
    plt.setp(ax_p.get_xticklabels(), visible=False)

    ax_q.fill_between(x, 0, lc["q_pred"], color="#8A8D8F", alpha=0.35)
    ax_q.plot(x, lc["q_pred"], color="#3A3A3A", lw=1.1)
    ax_q.set_ylabel(r"$\hat{q}$")
    ax_q.set_ylim(0, 1.0)
    ax_q.set_xlabel("Relative life")

    panel_letter(ax_p, "a")
    panel_caption(fig, ax_q, "Full lifecycle probability trajectory")


def panel_simplex(fig, ax, simplex):
    x, y = du.ternary_coords(simplex["prob_early"], simplex["prob_middle"], simplex["prob_late"])
    rel_life = simplex["relative_life"].values
    order = np.argsort(simplex["run_id"].values)
    x, y, rel_life = x[order], y[order], rel_life[order]

    tri_x = [0, 1, 0.5, 0]
    tri_y = [0, 0, np.sqrt(3) / 2, 0]
    ax.plot(tri_x, tri_y, color="black", lw=0.9)
    ax.text(-0.06, -0.035, "Early", fontsize=8, color=STAGE_COLORS["early"], fontweight="bold", ha="right")
    ax.text(1.06, -0.035, "Late", fontsize=8, color=STAGE_COLORS["late"], fontweight="bold", ha="left")
    ax.text(0.5, np.sqrt(3) / 2 + 0.035, "Middle", fontsize=8, color=STAGE_COLORS["middle"], fontweight="bold", ha="center")

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    lc = LineCollection(segments, cmap=DEGRADATION_CMAP, array=rel_life[:-1], linewidth=1.7, alpha=0.9)
    ax.add_collection(lc)
    ax.scatter(x[1:-1], y[1:-1], c=rel_life[1:-1], cmap=DEGRADATION_CMAP, s=7, zorder=3)
    ax.scatter([x[0]], [y[0]], s=90, facecolor="white", edgecolor=STAGE_COLORS["early"], linewidth=1.8, zorder=4)
    ax.scatter([x[-1]], [y[-1]], s=90, marker="s", facecolor=STAGE_COLORS["late"], edgecolor="black", linewidth=0.8, zorder=4)
    ax.text(x[0] - 0.02, y[0] - 0.05, "start", fontsize=6.8, ha="right", color="#555555")
    ax.text(x[-1] + 0.02, y[-1] - 0.05, "end", fontsize=6.8, ha="left", color="#555555")

    sm = plt.cm.ScalarMappable(cmap=DEGRADATION_CMAP, norm=plt.Normalize(0, 1))
    cbar = plt.colorbar(sm, ax=ax, orientation="horizontal", fraction=0.05, pad=0.10, shrink=0.75)
    cbar.set_label("Relative life", fontsize=7)
    cbar.ax.tick_params(labelsize=6.3)

    ax.set_xlim(-0.16, 1.16)
    ax.set_ylim(-0.15, np.sqrt(3) / 2 + 0.14)
    ax.set_aspect("equal")
    ax.axis("off")
    panel_letter(ax, "b")
    panel_caption(fig, ax, "Ordered trajectory in probability simplex", pad=0.075)


def panel_q_agreement(fig, ax, q_agree, log_lines):
    yt = q_agree["q_true"].values
    yp = q_agree["q_pred"].values
    assert (q_agree["q_comparison_definition"] == "q_true_vs_raw_q_pred_no_renormalization").all()
    r2 = du.r2_coefficient_of_determination(yt, yp)
    rho = stats.spearmanr(yt, yp)[0]
    mae = np.abs(yt - yp).mean()
    assert np.isclose(r2, 0.748, atol=0.01) and np.isclose(rho, 0.963, atol=0.01) and np.isclose(mae, 0.113, atol=0.01)
    log_lines.append(f"PASS (v2, recomputed independently): R2={r2:.4f}, rho={rho:.4f}, MAE={mae:.4f}, n={len(yt)}.")

    hb = ax.hexbin(yt, yp, gridsize=26, cmap="bone_r", mincnt=1, norm=plt.matplotlib.colors.LogNorm())
    ax.plot([0, 1], [0, 1], color="#8A8D8F", lw=1.0, ls="--")

    bins = np.linspace(0, 1, 21)
    bin_idx = np.digitize(yt, bins) - 1
    bin_centers, bin_medians = [], []
    for b in range(len(bins) - 1):
        mask = bin_idx == b
        if mask.sum() >= 2:
            bin_centers.append((bins[b] + bins[b + 1]) / 2)
            bin_medians.append(np.median(yp[mask]))
    ax.plot(bin_centers, bin_medians, color=STAGE_COLORS["middle"], lw=1.8, marker="o", ms=3, label="Binned median")

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel(r"$q_{true}$")
    ax.set_ylabel(r"$\hat{q}$")
    ax.text(0.03, 0.88, f"$R^2$ = {r2:.3f}\nSpearman $\\rho$ = {rho:.3f}\nMAE = {mae:.3f}\n$n$ = {len(yt)}",
            transform=ax.transAxes, va="top", ha="left", fontsize=7.6,
            bbox=dict(boxstyle="round", fc="white", ec="#CCCCCC", alpha=0.92))
    ax.legend(loc="lower right", fontsize=6.8)
    cbar = plt.colorbar(hb, ax=ax, fraction=0.045, pad=0.02)
    cbar.set_label("Run density", fontsize=6.8)
    cbar.ax.tick_params(labelsize=6)
    panel_letter(ax, "c")
    panel_caption(fig, ax, "Continuous degradation-position agreement")


def panel_wear(fig, ax, lifecycle, wear_agg, log_lines):
    rng = np.random.default_rng(0)
    positions = {"early": 0, "middle": 1, "late": 2}
    parts_data = [lifecycle[lifecycle["pred_stage"] == s]["VB_true"].values for s in STAGE_ORDER]
    vp = ax.violinplot(parts_data, positions=[positions[s] for s in STAGE_ORDER], showextrema=False, widths=0.75)
    for body, s in zip(vp["bodies"], STAGE_ORDER):
        body.set_facecolor(STAGE_COLORS[s]); body.set_alpha(0.30); body.set_edgecolor(STAGE_COLORS[s])
    ax.boxplot(parts_data, positions=[positions[s] for s in STAGE_ORDER], widths=0.13, showfliers=False,
               patch_artist=True, medianprops=dict(color="black", lw=1.4),
               boxprops=dict(facecolor="white", edgecolor="black", lw=0.8),
               whiskerprops=dict(color="black", lw=0.8), capprops=dict(color="black", lw=0.8))
    means_computed = {}
    for s in STAGE_ORDER:
        vals = lifecycle[lifecycle["pred_stage"] == s]["VB_true"].values
        jitter = rng.normal(0, 0.045, size=len(vals))
        ax.scatter(positions[s] + jitter, vals, s=6, color=STAGE_COLORS[s], alpha=0.55, zorder=3)
        means_computed[s] = vals.mean()
        agg_row = wear_agg[wear_agg["predicted_stage"] == s].iloc[0]
        assert np.isclose(vals.mean(), agg_row["VB_mean"], atol=1e-6)
        assert np.isclose(np.median(vals), agg_row["VB_median"], atol=1e-6)
    medians = [np.median(lifecycle[lifecycle["pred_stage"] == s]["VB_true"].values) for s in STAGE_ORDER]
    ax.plot([positions[s] for s in STAGE_ORDER], medians, color="#8A8D8F", lw=1.1, ls="--", zorder=2)
    log_lines.append("PASS (v2, recomputed independently): per-pred-stage VB_true mean/median match wear_by_predicted_stage.csv for all 3 stages.")
    ratio = means_computed["late"] / means_computed["early"]
    assert np.isclose(ratio, 2.04, atol=0.02)
    log_lines.append(f"PASS: VB means Early={means_computed['early']:.2f}, Middle={means_computed['middle']:.2f}, Late={means_computed['late']:.2f} um; Late/Early={ratio:.3f} (~2.04).")

    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels([STAGE_LABELS[s] for s in STAGE_ORDER])
    ax.set_ylabel("True flank wear, VB (μm)")
    ax.set_xlabel("Predicted degradation state")
    panel_letter(ax, "d")
    panel_caption(fig, ax, "Physical wear semantics")


def main():
    apply_style()
    lifecycle, simplex, q_agree, wear_agg = load()
    log_lines = []
    assert len(lifecycle) == 304 and len(simplex) == 304 and len(q_agree) == 304
    log_lines.append("PASS: lifecycle_semantics/simplex_trajectory/q_agreement each have 304 rows.")

    fig = plt.figure(figsize=(14.2, 12.8))
    gs = GridSpec(3, 2, height_ratios=[1.0, 1.15, 0.95], hspace=0.62, wspace=0.28, figure=fig,
                  left=0.065, right=0.97, top=0.985, bottom=0.165)

    panel_lifecycle(fig, gs[0, :], lifecycle)
    panel_simplex(fig, fig.add_subplot(gs[1, 0]), simplex)
    panel_q_agreement(fig, fig.add_subplot(gs[1, 1]), q_agree, log_lines)
    panel_wear(fig, fig.add_subplot(gs[2, :]), lifecycle, wear_agg, log_lines)

    figure_caption(fig, "退化语义", subtitle="Fig. 4-5  Ordered degradation semantics: lifecycle probability, simplex trajectory, q agreement, and physical wear")

    paths = save_all(fig, OUT_DIR, "fig4_v2_reference_style")
    log_lines.append(f"Saved outputs: {paths}")
    with open(os.path.join(LOG_DIR, "validation_v2.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
    print("\n".join(log_lines))
    print("Fig.4 v2 done.")


if __name__ == "__main__":
    main()
