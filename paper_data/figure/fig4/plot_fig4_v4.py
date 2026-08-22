"""
Fig.4 v4 (paper Fig. 4-5): ordered degradation semantics -- publication-grade true-physical-size
refinement (178 x 128 mm master size).

DATA UNCHANGED FROM v1/v2/v3: imports v1's load() and the same R^2/Spearman/MAE formula directly.
Two content changes this round (both documented in paper_data/figure/fig4/README.md's "v4"
section and paper_data/figure/V4_DESIGN_AUDIT.md):
  1. Panel (d) ("latent manifold overview") now reads the SHARED PCA coordinates from
     paper_data/figure/_shared/derived/shared_pca_scores_v4.csv (built once by
     prepare_shared_pca_v4.py) instead of fitting its own independent PCA -- guarantees Fig.4(d)
     and Fig.5(a)/(b)/(c) show geometrically identical latent geometry.
  2. Panel (b)'s probability-simplex vertex convention switches to the ORIGINAL PAPER's own
     convention (代码/7.3主实验.py::plot_probability_simplex): Early=bottom-left,
     Middle=bottom-right, Late=top (x = p_middle + 0.5*p_late, y = (sqrt(3)/2)*p_late). This is a
     coordinate-LABELING change for consistency with the rest of the thesis -- same real 304
     (p_E,p_M,p_L) triples, same trajectory, just which corner is which.

Run: python paper_data/figure/fig4/plot_fig4_v4.py
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.collections import LineCollection
from scipy import stats

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_shared"))
from style_v4 import (apply_style, save_all, panel_container, master_figsize_in,
                       STAGE_ORDER, STAGE_COLORS, STAGE_LABELS, STAGE_MARKERS,
                       DEGRADATION_CMAP, LW_MAIN, LW_AUX)  # noqa: E402
import data_utils as du  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
from plot_fig4 import load  # noqa: E402

HERE = os.path.dirname(__file__)
OUT_DIR = os.path.join(HERE, "outputs")
LOG_DIR = os.path.join(HERE, "logs")
SHARED_PCA_PATH = os.path.join(HERE, "..", "_shared", "derived", "shared_pca_scores_v4.csv")
os.makedirs(LOG_DIR, exist_ok=True)


def paper_simplex_coords(p_early, p_middle, p_late):
    """代码/7.3主实验.py's own convention: Early=bottom-left, Middle=bottom-right, Late=top."""
    p_middle = np.asarray(p_middle, dtype=float)
    p_late = np.asarray(p_late, dtype=float)
    x = p_middle + 0.5 * p_late
    y = (np.sqrt(3) / 2) * p_late
    return x, y


def panel_a_lifecycle(fig, outer_cell, lifecycle):
    content_spec, _ = panel_container(fig, outer_cell,
                                       "(a) Full C6 lifecycle: stage probability\n+ degradation position (n=304)",
                                       hspace=0.55, caption_height=0.115, fontsize=8.4)
    inner = content_spec.subgridspec(2, 1, height_ratios=[2.0, 1.0], hspace=0.22)
    ax_p = fig.add_subplot(inner[0])
    ax_q = fig.add_subplot(inner[1], sharex=ax_p)

    lc = lifecycle.sort_values("relative_life").reset_index(drop=True)
    x = lc["relative_life"].values
    stage_ids = lc["true_stage"].values
    seen_start = 0.0
    prev_stage = stage_ids[0]
    for i in range(1, len(x)):
        if stage_ids[i] != prev_stage:
            ax_p.axvspan(seen_start, x[i - 1], color=STAGE_COLORS[prev_stage], alpha=0.09, lw=0)
            ax_q.axvspan(seen_start, x[i - 1], color=STAGE_COLORS[prev_stage], alpha=0.09, lw=0)
            seen_start = x[i]
            prev_stage = stage_ids[i]
    ax_p.axvspan(seen_start, x[-1], color=STAGE_COLORS[prev_stage], alpha=0.09, lw=0)
    ax_q.axvspan(seen_start, x[-1], color=STAGE_COLORS[prev_stage], alpha=0.09, lw=0)

    for col, key, label in [("prob_early", "early", "$p_E$"), ("prob_middle", "middle", "$p_M$"),
                             ("prob_late", "late", "$p_L$")]:
        ax_p.plot(x, lc[col], color=STAGE_COLORS[key], lw=LW_MAIN, label=label)
        ax_p.fill_between(x, 0, lc[col], color=STAGE_COLORS[key], alpha=0.10)
    ax_p.set_ylabel("Probability")
    ax_p.set_ylim(0, 1.02)
    ax_p.legend(loc="lower left", ncol=3, fontsize=6.6, frameon=True, facecolor="white",
                framealpha=0.85, edgecolor="none")
    plt.setp(ax_p.get_xticklabels(), visible=False)
    ax_p.tick_params(labelsize=7.0)

    ax_q.plot(x, lc["q_true"], color="black", lw=LW_MAIN, label="$q_{true}$")
    ax_q.plot(x, lc["q_pred"], color="#C0392B", lw=LW_AUX, alpha=0.9, label="$q_{pred}$ (raw)")
    ax_q.set_ylabel("$q$", fontsize=8.0)
    ax_q.set_xlabel("Relative life", fontsize=8.0)
    ax_q.set_ylim(0, 1.02)
    ax_q.legend(loc="upper left", ncol=2, fontsize=6.6)
    ax_q.tick_params(labelsize=7.0)
    return ax_p, ax_q


def panel_b_simplex(fig, outer_cell, simplex):
    content_spec, _ = panel_container(fig, outer_cell,
                                       "(b) Ordered trajectory in the\nprobability simplex",
                                       hspace=0.55, caption_height=0.115, fontsize=8.4)
    ax = fig.add_subplot(content_spec)

    order = np.argsort(simplex["run_id"].values)
    p_e = simplex["prob_early"].values[order]
    p_m = simplex["prob_middle"].values[order]
    p_l = simplex["prob_late"].values[order]
    rel_life = simplex["relative_life"].values[order]
    x, y = paper_simplex_coords(p_e, p_m, p_l)

    tri_x = [0, 1, 0.5, 0]
    tri_y = [0, 0, np.sqrt(3) / 2, 0]
    ax.plot(tri_x, tri_y, color="black", lw=0.9)
    ax.text(-0.05, -0.05, "Early", fontsize=7.4, color=STAGE_COLORS["early"], fontweight="bold", ha="right")
    ax.text(1.05, -0.05, "Middle", fontsize=7.4, color=STAGE_COLORS["middle"], fontweight="bold", ha="left")
    ax.text(0.5, np.sqrt(3) / 2 + 0.04, "Late", fontsize=7.4, color=STAGE_COLORS["late"], fontweight="bold", ha="center")

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    lc3 = LineCollection(segments, cmap=DEGRADATION_CMAP, array=rel_life[:-1], linewidth=1.9, alpha=0.92)
    ax.add_collection(lc3)
    ax.scatter(x[1:-1], y[1:-1], c=rel_life[1:-1], cmap=DEGRADATION_CMAP, s=8, zorder=3)
    ax.scatter([x[0]], [y[0]], s=55, facecolor="white", edgecolor=STAGE_COLORS["early"], linewidth=1.6, zorder=4)
    ax.scatter([x[-1]], [y[-1]], s=55, marker="s", facecolor=STAGE_COLORS["late"], edgecolor="black", linewidth=0.7, zorder=4)
    mid_i = len(x) // 2
    ax.annotate("", xy=(x[mid_i + 4], y[mid_i + 4]), xytext=(x[mid_i], y[mid_i]),
                arrowprops=dict(arrowstyle="-|>", color="#333333", lw=1.3), zorder=5)

    sm = plt.cm.ScalarMappable(cmap=DEGRADATION_CMAP, norm=plt.Normalize(0, 1))
    cbar = plt.colorbar(sm, ax=ax, orientation="horizontal", fraction=0.05, pad=0.10, shrink=0.75)
    cbar.set_label("Relative life", fontsize=6.8)
    cbar.ax.tick_params(labelsize=6.5)

    ax.set_xlim(-0.18, 1.20)
    ax.set_ylim(-0.16, np.sqrt(3) / 2 + 0.15)
    ax.set_aspect("equal")
    ax.axis("off")
    return ax


def panel_c_q_agreement(fig, outer_cell, q_agree, log_lines):
    content_spec, _ = panel_container(fig, outer_cell,
                                       "(c) Continuous degradation-position\nagreement (raw q_pred, no renorm.)",
                                       hspace=0.55, caption_height=0.115, fontsize=8.2)
    ax = fig.add_subplot(content_spec)

    yt = q_agree["q_true"].values
    yp = q_agree["q_pred"].values
    assert (q_agree["q_comparison_definition"] == "q_true_vs_raw_q_pred_no_renormalization").all()
    r2 = du.r2_coefficient_of_determination(yt, yp)
    rho = stats.spearmanr(yt, yp)[0]
    mae = np.abs(yt - yp).mean()
    assert np.isclose(r2, 0.748, atol=0.01) and np.isclose(rho, 0.963, atol=0.01) and np.isclose(mae, 0.113, atol=0.01)
    log_lines.append(f"PASS: q agreement recomputed live: R2={r2:.4f}, rho={rho:.4f}, MAE={mae:.4f}, n={len(yt)}.")

    hb = ax.hexbin(yt, yp, gridsize=22, cmap="bone_r", mincnt=1)
    ax.plot([0, 1], [0, 1], color="#8A8D8F", lw=1.0, ls="--")
    bins = np.linspace(0, 1, 18)
    bin_idx = np.digitize(yt, bins) - 1
    bc, bm = [], []
    for b in range(len(bins) - 1):
        mask = bin_idx == b
        if mask.sum() >= 2:
            bc.append((bins[b] + bins[b + 1]) / 2)
            bm.append(np.median(yp[mask]))
    ax.plot(bc, bm, color=STAGE_COLORS["middle"], lw=1.5, marker="o", ms=3)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xlabel("$q_{true}$", fontsize=8.0)
    ax.set_ylabel("$q_{pred}$ (raw)", fontsize=8.0)
    ax.text(0.03, 0.97, f"$R^2$={r2:.3f}\n$\\rho$={rho:.3f}\nMAE={mae:.3f}\n$n$={len(yt)}",
            transform=ax.transAxes, va="top", ha="left", fontsize=6.8,
            bbox=dict(boxstyle="round", fc="white", ec="#CCCCCC", alpha=0.92))
    ax.tick_params(labelsize=7.0)
    cbar = plt.colorbar(hb, ax=ax, fraction=0.045, pad=0.02)
    cbar.set_label("count", fontsize=6.6)
    cbar.ax.tick_params(labelsize=6.5)
    return ax


def panel_d_shared_manifold(fig, outer_cell, shared_pca, log_lines):
    content_spec, _ = panel_container(fig, outer_cell,
                                       "(d) Shared latent manifold overview\n(same PCA as Fig.5; see Fig.5 for full analysis)",
                                       hspace=0.55, caption_height=0.13, fontsize=8.0)
    ax = fig.add_subplot(content_spec)

    order = np.argsort(shared_pca["q_true"].values)
    ax.plot(shared_pca["PC1"].values[order], shared_pca["PC2"].values[order],
            color="#B7BDC2", lw=0.9, ls="--", zorder=1)
    for s in STAGE_ORDER:
        mask = shared_pca["true_stage"].values == s
        sc = ax.scatter(shared_pca["PC1"].values[mask], shared_pca["PC2"].values[mask], s=16,
                         c=shared_pca["q_true"].values[mask], cmap=DEGRADATION_CMAP, vmin=0, vmax=1,
                         marker=STAGE_MARKERS[s], edgecolor="none", alpha=0.88, zorder=2)
    mid = order[len(order) // 2]
    nxt = order[min(len(order) - 1, len(order) // 2 + 6)]
    ax.annotate("", xy=(shared_pca["PC1"].values[nxt], shared_pca["PC2"].values[nxt]),
                xytext=(shared_pca["PC1"].values[mid], shared_pca["PC2"].values[mid]),
                arrowprops=dict(arrowstyle="-|>", color="#333333", lw=1.3), zorder=4)
    ax.text(0.97, 0.06, "increasing degradation →", transform=ax.transAxes, fontsize=6.6,
            color="#333333", style="italic", ha="right",
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85))
    cbar = plt.colorbar(sc, ax=ax, fraction=0.045, pad=0.02)
    cbar.set_label("$q_{true}$", fontsize=6.8)
    cbar.ax.tick_params(labelsize=6.5)
    ax.set_xlabel("PC1", fontsize=8.0)
    ax.set_ylabel("PC2", fontsize=8.0)
    ax.tick_params(labelsize=7.0)
    log_lines.append(f"PASS: panel(d) reads shared PCA coordinates from {SHARED_PCA_PATH} "
                      f"(no independent PCA fit in this script).")
    return ax


def panel_e_wear(fig, outer_cell, lifecycle, wear_agg, log_lines):
    content_spec, _ = panel_container(fig, outer_cell,
                                       "(e) Physical wear semantics: VB_true\ngrouped by predicted stage",
                                       hspace=0.55, caption_height=0.115, fontsize=8.2)
    ax = fig.add_subplot(content_spec)
    rng = np.random.default_rng(0)
    positions = {"early": 0, "middle": 1, "late": 2}
    parts_data = [lifecycle[lifecycle["pred_stage"] == s]["VB_true"].values for s in STAGE_ORDER]
    vp = ax.violinplot(parts_data, positions=[positions[s] for s in STAGE_ORDER], showextrema=False, widths=0.72)
    for body, s in zip(vp["bodies"], STAGE_ORDER):
        body.set_facecolor(STAGE_COLORS[s]); body.set_alpha(0.28); body.set_edgecolor(STAGE_COLORS[s])
    ax.boxplot(parts_data, positions=[positions[s] for s in STAGE_ORDER], widths=0.13, showfliers=False,
               patch_artist=True, medianprops=dict(color="black", lw=1.3),
               boxprops=dict(facecolor="white", edgecolor="black", lw=0.7),
               whiskerprops=dict(color="black", lw=0.7), capprops=dict(color="black", lw=0.7))
    means_computed = {}
    for s in STAGE_ORDER:
        vals = lifecycle[lifecycle["pred_stage"] == s]["VB_true"].values
        jitter = rng.normal(0, 0.045, size=len(vals))  # x-only jitter, never y
        ax.scatter(positions[s] + jitter, vals, s=5, color=STAGE_COLORS[s], alpha=0.5, zorder=3)
        means_computed[s] = vals.mean()
        agg_row = wear_agg[wear_agg["predicted_stage"] == s].iloc[0]
        assert np.isclose(vals.mean(), agg_row["VB_mean"], atol=1e-6)
    log_lines.append("PASS: panel(e) recomputed per-predicted-stage VB_true means match wear_by_predicted_stage.csv.")
    for s in STAGE_ORDER:
        assert 70 <= means_computed[s] <= 240
    log_lines.append(f"PASS: VB means Early={means_computed['early']:.2f}, Middle={means_computed['middle']:.2f}, "
                      f"Late={means_computed['late']:.2f} um, linear axis 70-240 um (no significance test added -- "
                      f"the real gap between groups is large enough to be self-evident without one; see README).")
    for s in STAGE_ORDER:
        ax.annotate(f"mean={means_computed[s]:.1f}", (positions[s], means_computed[s]),
                    xytext=(positions[s] + 0.30, means_computed[s]), fontsize=6.6, color=STAGE_COLORS[s])
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels([STAGE_LABELS[s] for s in STAGE_ORDER], fontsize=7.6)
    ax.set_ylabel("True flank wear, VB (μm)", fontsize=8.0)
    ax.set_xlabel("Predicted degradation state", fontsize=8.0)
    ax.set_ylim(65, 245)
    ax.tick_params(labelsize=7.0)
    return ax


def main():
    apply_style()
    lifecycle, simplex, q_agree, wear_agg = load()
    shared_pca = du.read_csv("figure", "_shared", "derived", "shared_pca_scores_v4.csv")
    log_lines = []

    assert len(lifecycle) == 304 and len(simplex) == 304 and len(q_agree) == 304 and len(shared_pca) == 304
    log_lines.append("PASS: all 4 input tables (3 fig4-native + 1 shared PCA) have 304 rows.")

    fig = plt.figure(figsize=master_figsize_in("fig4"))
    outer = GridSpec(2, 1, height_ratios=[0.52, 0.48], hspace=0.42, figure=fig,
                      left=0.06, right=0.97, top=0.99, bottom=0.06)
    top_row = outer[0].subgridspec(1, 3, width_ratios=[1.15, 0.85, 1.0], wspace=0.35)
    bot_row = outer[1].subgridspec(1, 2, width_ratios=[1.0, 1.0], wspace=0.30)

    panel_a_lifecycle(fig, top_row[0], lifecycle)
    panel_b_simplex(fig, top_row[1], simplex)
    panel_c_q_agreement(fig, top_row[2], q_agree, log_lines)
    panel_d_shared_manifold(fig, bot_row[0], shared_pca, log_lines)
    panel_e_wear(fig, bot_row[1], lifecycle, wear_agg, log_lines)

    paths = save_all(fig, OUT_DIR, "fig4_v4")
    log_lines.append(f"Saved outputs: {paths}")
    with open(os.path.join(LOG_DIR, "validation_v4.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
    print("\n".join(log_lines))
    print("Fig.4 v4 done.")


if __name__ == "__main__":
    main()
