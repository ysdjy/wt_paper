"""
Fig.4 v3 (paper Fig. 4-5): ordered degradation semantics -- dense landscape reconstruction.

DATA AND STATISTICS ARE UNCHANGED FROM v1: imports v1's load() directly (lifecycle_semantics.csv,
simplex_trajectory.csv, q_agreement.csv, wear_by_predicted_stage.csv, all real 304-row C6 test
data) and reuses the same R^2/Spearman/MAE formula (coefficient of determination on RAW q_pred,
NOT squared Pearson r -- see _shared/data_utils.py::r2_coefficient_of_determination).

Panel (d) "latent manifold": v1/v2 fig4 has NO such panel (fig4's own inputs -- lifecycle/simplex/
q_agreement/wear -- carry no hidden-representation data). v1's fig4 README explicitly anticipated
this exact situation: "Fig.4 若放 latent manifold, only保留一个简洁二维overview; 更系统的分析留给
Fig.5". So panel (d) here reuses the REAL 64-D hidden_representation.csv (304 rows, same file
fig5 uses) with a single fresh PCA fit (numpy SVD via data_utils.pca_2d, computed independently
here -- not copied from fig5's own PCA run) and a deliberately simple single view: q-colored,
stage-marker-shaped points, a thin q-sorted trajectory line, one arrow showing increasing
degradation. This is intentionally simpler than fig5's own 3-panel (stage/q/uncertainty) PCA
treatment, to avoid duplicating fig5's narrative.

Layout, ground-up rebuilt (landscape 15.5x10.0in, top row ~52%, bottom row ~48%):
  ┌────────────┬────────────┬────────────┐
  │ (a) lifecycle │ (b) simplex │ (c) q agreement │
  ├────────────┴──────┬─────┴────────────┤
  │ (d) latent manifold │ (e) physical wear  │
  └─────────────────────┴────────────────────┘

Style reference: paper_data/figure/fig4/视觉参考效果图/*.png -- LAYOUT ONLY (5-panel arrangement,
top-row-3/bottom-row-2 proportions). Its own R²/MAE/Spearman numbers (though close in shape),
lifecycle curve shape, point-cloud density/shape counts, and LOG-scale VB axis (10^1-10^4) are
NOT reproduced -- VB axis here is LINEAR ~70-240 um (real data range), and every number is
recomputed live from paper_data.

Run: python paper_data/figure/fig4/plot_fig4_v3.py
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.collections import LineCollection
from scipy import stats

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_shared"))
from style_v3 import (apply_style, save_all, panel_container, STAGE_ORDER, STAGE_COLORS,
                       STAGE_LABELS, STAGE_MARKERS, DEGRADATION_CMAP)  # noqa: E402
import data_utils as du  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
from plot_fig4 import load  # noqa: E402

HERE = os.path.dirname(__file__)
OUT_DIR = os.path.join(HERE, "outputs")
LOG_DIR = os.path.join(HERE, "logs")
os.makedirs(LOG_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# panel (a): lifecycle probability + q strip
# ---------------------------------------------------------------------------
def panel_a_lifecycle(fig, outer_cell, lifecycle):
    content_spec, _ = panel_container(fig, outer_cell, "(a) Full C6 lifecycle: stage probability + degradation position",
                                       hspace=0.30, caption_height=0.075)
    inner = content_spec.subgridspec(2, 1, height_ratios=[0.62, 0.38], hspace=0.10)
    ax_p = fig.add_subplot(inner[0])
    ax_q = fig.add_subplot(inner[1], sharex=ax_p)

    lc = lifecycle.sort_values("relative_life").reset_index(drop=True)
    x = lc["relative_life"].values
    stage_ids = lc["true_stage"].values
    seen_start = 0.0
    prev_stage = stage_ids[0]
    for i in range(1, len(x)):
        if stage_ids[i] != prev_stage:
            ax_p.axvspan(seen_start, x[i - 1], color=STAGE_COLORS[prev_stage], alpha=0.08, lw=0)
            ax_q.axvspan(seen_start, x[i - 1], color=STAGE_COLORS[prev_stage], alpha=0.08, lw=0)
            seen_start = x[i]
            prev_stage = stage_ids[i]
    ax_p.axvspan(seen_start, x[-1], color=STAGE_COLORS[prev_stage], alpha=0.08, lw=0)
    ax_q.axvspan(seen_start, x[-1], color=STAGE_COLORS[prev_stage], alpha=0.08, lw=0)

    for col, stage, label in [("prob_early", "early", "$p_E$"), ("prob_middle", "middle", "$p_M$"),
                               ("prob_late", "late", "$p_L$")]:
        ax_p.plot(x, lc[col], color=STAGE_COLORS[stage], lw=1.4, label=label)
        ax_p.fill_between(x, 0, lc[col], color=STAGE_COLORS[stage], alpha=0.12)
    ax_p.set_ylabel("Probability")
    ax_p.set_ylim(0, 1.03)
    ax_p.legend(loc="center left", ncol=1, fontsize=7.2, frameon=True, facecolor="white",
                framealpha=0.85, edgecolor="none")
    plt.setp(ax_p.get_xticklabels(), visible=False)

    ax_q.plot(x, lc["q_true"], color="#1A1A1A", lw=1.3, label="$q_{true}$")
    ax_q.plot(x, lc["q_pred"], color="#B0555E", lw=1.1, alpha=0.85, label="$q_{pred}$ (raw)")
    ax_q.set_ylabel("$q$")
    ax_q.set_xlabel("Relative life")
    ax_q.set_ylim(0, 1.02)
    ax_q.legend(loc="upper left", fontsize=7.0, ncol=2)
    return ax_p, ax_q


# ---------------------------------------------------------------------------
# panel (b): probability simplex
# ---------------------------------------------------------------------------
def panel_b_simplex(fig, outer_cell, simplex):
    content_spec, _ = panel_container(fig, outer_cell, "(b) Ordered trajectory in the probability simplex",
                                       hspace=0.10, caption_height=0.075)
    ax = fig.add_subplot(content_spec)

    x, y = du.ternary_coords(simplex["prob_early"], simplex["prob_middle"], simplex["prob_late"])
    rel_life = simplex["relative_life"].values
    order = np.argsort(simplex["run_id"].values)
    x, y, rel_life = x[order], y[order], rel_life[order]

    tri_x, tri_y = [0, 1, 0.5, 0], [0, 0, np.sqrt(3) / 2, 0]
    ax.plot(tri_x, tri_y, color="black", lw=0.9)
    ax.text(-0.06, -0.035, "Early", fontsize=8, color=STAGE_COLORS["early"], fontweight="bold", ha="right")
    ax.text(1.06, -0.035, "Late", fontsize=8, color=STAGE_COLORS["late"], fontweight="bold", ha="left")
    ax.text(0.5, np.sqrt(3) / 2 + 0.04, "Middle", fontsize=8, color=STAGE_COLORS["middle"], fontweight="bold", ha="center")

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    lc = LineCollection(segments, cmap=DEGRADATION_CMAP, array=rel_life[:-1], linewidth=2.0, alpha=0.9)
    ax.add_collection(lc)
    ax.scatter(x[1:-1:6], y[1:-1:6], c=rel_life[1:-1:6], cmap=DEGRADATION_CMAP, s=10, zorder=3)
    ax.scatter([x[0]], [y[0]], s=95, facecolor="white", edgecolor=STAGE_COLORS["early"], linewidth=1.8, zorder=4)
    ax.scatter([x[-1]], [y[-1]], s=95, marker="s", facecolor=STAGE_COLORS["late"], edgecolor="black", linewidth=0.8, zorder=4)
    mid_i = len(x) // 2
    ax.annotate("", xy=(x[mid_i + 8], y[mid_i + 8]), xytext=(x[mid_i], y[mid_i]),
                arrowprops=dict(arrowstyle="-|>", color="#333333", lw=1.3), zorder=5)

    sm = plt.cm.ScalarMappable(cmap=DEGRADATION_CMAP, norm=plt.Normalize(0, 1))
    cbar = plt.colorbar(sm, ax=ax, orientation="horizontal", fraction=0.05, pad=0.08, shrink=0.72)
    cbar.set_label("Relative life / q", fontsize=7)
    cbar.ax.tick_params(labelsize=6.3)

    ax.set_xlim(-0.16, 1.16)
    ax.set_ylim(-0.14, np.sqrt(3) / 2 + 0.15)
    ax.set_aspect("equal")
    ax.axis("off")
    return ax


# ---------------------------------------------------------------------------
# panel (c): q agreement
# ---------------------------------------------------------------------------
def panel_c_q_agreement(fig, outer_cell, q_agree, log_lines):
    content_spec, _ = panel_container(fig, outer_cell, "(c) Continuous degradation-position agreement",
                                       hspace=0.28, caption_height=0.075)
    ax = fig.add_subplot(content_spec)

    yt = q_agree["q_true"].values
    yp = q_agree["q_pred"].values
    assert (q_agree["q_comparison_definition"] == "q_true_vs_raw_q_pred_no_renormalization").all()
    r2 = du.r2_coefficient_of_determination(yt, yp)
    rho = stats.spearmanr(yt, yp)[0]
    mae = np.abs(yt - yp).mean()
    assert np.isclose(r2, 0.748, atol=0.01) and np.isclose(rho, 0.963, atol=0.01) and np.isclose(mae, 0.113, atol=0.01)
    log_lines.append(f"PASS (v3): q agreement recomputed live: R2={r2:.4f} (~0.748), rho={rho:.4f} (~0.963), MAE={mae:.4f} (~0.113).")

    hb = ax.hexbin(yt, yp, gridsize=26, cmap="Blues", mincnt=1)
    ax.plot([0, 1], [0, 1], color="#B0555E", lw=1.0, ls="--", label="y = x")

    bins = np.linspace(0, 1, 21)
    bin_idx = np.digitize(yt, bins) - 1
    bc, bm = [], []
    for b in range(len(bins) - 1):
        mask = bin_idx == b
        if mask.sum() >= 2:
            bc.append((bins[b] + bins[b + 1]) / 2)
            bm.append(np.median(yp[mask]))
    ax.plot(bc, bm, color="#2A8C7A", lw=1.8, marker="o", ms=3, label="Binned median")

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("$q_{true}$")
    ax.set_ylabel("$q_{pred}$ (raw, no renorm.)")
    ax.text(0.03, 0.97, f"$R^2$={r2:.3f}\nSpearman $\\rho$={rho:.3f}\nMAE={mae:.3f}\n$n$={len(yt)}",
            transform=ax.transAxes, va="top", ha="left", fontsize=7.4,
            bbox=dict(boxstyle="round", fc="white", ec="#CCCCCC", alpha=0.92))
    ax.legend(loc="lower right", fontsize=6.8)
    cbar = plt.colorbar(hb, ax=ax, fraction=0.045, pad=0.02)
    cbar.set_label("count", fontsize=6.8)
    cbar.ax.tick_params(labelsize=6)
    return ax


# ---------------------------------------------------------------------------
# panel (d): latent manifold (simple single view; real 304-row hidden_representation.csv)
# ---------------------------------------------------------------------------
def panel_d_manifold(fig, outer_cell, log_lines):
    content_spec, _ = panel_container(fig, outer_cell,
                                       "(d) Shared latent manifold (64-D hidden representation, PCA; simple overview -- see Fig.5 for full analysis)",
                                       hspace=0.16, caption_height=0.085, fontsize=8.6)
    ax = fig.add_subplot(content_spec)

    hidden = du.read_csv("07_figure_ready", "fig5", "hidden_representation.csv")
    assert len(hidden) == 304
    h_cols = [c for c in hidden.columns if c.startswith("h_")]
    assert len(h_cols) == 64
    scores, explained, _ = du.pca_2d(hidden[h_cols].values)
    log_lines.append(f"PASS (v3): panel(d) fresh PCA fit on real 304x64 hidden_representation.csv "
                      f"(independent of fig5's own PCA run); PC1={explained[0]:.3f}, PC2={explained[1]:.3f} var.")

    order = np.argsort(hidden["q_true"].values)
    ax.plot(scores[order, 0], scores[order, 1], color="#B7BDC2", lw=0.9, ls="--", zorder=1)
    for s in STAGE_ORDER:
        mask = hidden["true_stage"].values == s
        sc = ax.scatter(scores[mask, 0], scores[mask, 1], s=20, c=hidden["q_true"].values[mask],
                         cmap=DEGRADATION_CMAP, vmin=0, vmax=1, marker=STAGE_MARKERS[s],
                         edgecolor="none", alpha=0.88, zorder=2)
    # arrow indicating increasing degradation, along the q-sorted trajectory
    mid = order[len(order) // 2]
    nxt = order[len(order) // 2 + 6]
    ax.annotate("", xy=(scores[nxt, 0], scores[nxt, 1]), xytext=(scores[mid, 0], scores[mid, 1]),
                arrowprops=dict(arrowstyle="-|>", color="#333333", lw=1.5), zorder=4)
    ax.text(0.03, 0.05, "increasing degradation →", transform=ax.transAxes, fontsize=6.8, color="#333333", style="italic")

    handles = [plt.Line2D([0], [0], marker=STAGE_MARKERS[s], color="none", markerfacecolor="#888888",
                           markeredgecolor="none", markersize=7, label=STAGE_LABELS[s]) for s in STAGE_ORDER]
    ax.legend(handles=handles, loc="lower right", fontsize=6.8, title="true stage", title_fontsize=6.5,
              frameon=True, facecolor="white", framealpha=0.9, edgecolor="none")
    cbar = plt.colorbar(sc, ax=ax, fraction=0.04, pad=0.02)
    cbar.set_label("$q_{true}$", fontsize=7)
    cbar.ax.tick_params(labelsize=6)
    ax.set_xlabel(f"PC1 ({explained[0]*100:.1f}% var.)")
    ax.set_ylabel(f"PC2 ({explained[1]*100:.1f}% var.)")
    return ax


# ---------------------------------------------------------------------------
# panel (e): physical wear (linear um axis)
# ---------------------------------------------------------------------------
def panel_e_wear(fig, outer_cell, lifecycle, wear_agg, log_lines):
    content_spec, _ = panel_container(fig, outer_cell, "(e) Physical wear semantics: VB_true grouped by predicted stage",
                                       hspace=0.16, caption_height=0.075)
    ax = fig.add_subplot(content_spec)

    rng = np.random.default_rng(0)
    positions = {"early": 0, "middle": 1, "late": 2}
    parts = [lifecycle[lifecycle["pred_stage"] == s]["VB_true"].values for s in STAGE_ORDER]
    vp = ax.violinplot(parts, positions=[positions[s] for s in STAGE_ORDER], showextrema=False, widths=0.75)
    for body, s in zip(vp["bodies"], STAGE_ORDER):
        body.set_facecolor(STAGE_COLORS[s]); body.set_alpha(0.30); body.set_edgecolor(STAGE_COLORS[s])
    ax.boxplot(parts, positions=[positions[s] for s in STAGE_ORDER], widths=0.13, showfliers=False,
               patch_artist=True, medianprops=dict(color="black", lw=1.4),
               boxprops=dict(facecolor="white", edgecolor="black", lw=0.8),
               whiskerprops=dict(color="black", lw=0.8), capprops=dict(color="black", lw=0.8))

    means = {}
    for s in STAGE_ORDER:
        vals = lifecycle[lifecycle["pred_stage"] == s]["VB_true"].values
        jitter = rng.normal(0, 0.045, size=len(vals))
        ax.scatter(positions[s] + jitter, vals, s=6, color=STAGE_COLORS[s], alpha=0.55, zorder=3)
        means[s] = vals.mean()
        agg = wear_agg[wear_agg["predicted_stage"] == s].iloc[0]
        assert np.isclose(vals.mean(), agg["VB_mean"], atol=1e-6)
    ratio = means["late"] / means["early"]
    assert np.isclose(ratio, 2.04, atol=0.02)
    log_lines.append(f"PASS (v3): VB means Early={means['early']:.2f}, Middle={means['middle']:.2f}, "
                      f"Late={means['late']:.2f} um (linear axis); Late/Early={ratio:.3f} (~2.04).")

    for s in STAGE_ORDER:
        ax.annotate(f"mean={means[s]:.1f}", (positions[s], means[s]),
                    xytext=(positions[s] + 0.30, means[s]), fontsize=6.6, color=STAGE_COLORS[s])
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels([STAGE_LABELS[s] for s in STAGE_ORDER])
    ax.set_ylabel("True flank wear, VB (μm)")
    ax.set_xlabel("Predicted degradation state")
    ax.set_ylim(65, 245)  # linear, real data range -- NOT log
    return ax


def main():
    apply_style()
    lifecycle, simplex, q_agree, wear_agg = load()
    log_lines = []
    assert len(lifecycle) == 304 and len(simplex) == 304 and len(q_agree) == 304
    log_lines.append("PASS: lifecycle_semantics/simplex_trajectory/q_agreement each have 304 rows.")

    fig = plt.figure(figsize=(15.5, 10.0))
    outer = GridSpec(2, 1, height_ratios=[0.52, 0.48], hspace=0.20, figure=fig,
                      left=0.045, right=0.985, top=0.99, bottom=0.03)
    top3 = outer[0].subgridspec(1, 3, width_ratios=[0.36, 0.30, 0.34], wspace=0.14)
    bot2 = outer[1].subgridspec(1, 2, width_ratios=[0.52, 0.48], wspace=0.13)

    panel_a_lifecycle(fig, top3[0], lifecycle)
    panel_b_simplex(fig, top3[1], simplex)
    panel_c_q_agreement(fig, top3[2], q_agree, log_lines)
    panel_d_manifold(fig, bot2[0], log_lines)
    panel_e_wear(fig, bot2[1], lifecycle, wear_agg, log_lines)

    paths = save_all(fig, OUT_DIR, "fig4_v3")
    log_lines.append(f"Saved outputs: {paths}")
    with open(os.path.join(LOG_DIR, "validation_v3.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
    print("\n".join(log_lines))
    print("Fig.4 v3 done.")


if __name__ == "__main__":
    main()
