"""
Fig.5 v2 (paper Fig. 4-6): shared latent representation geometry and joint probability-position
evolution -- reference-style visual reconstruction.

DATA AND STATISTICS ARE UNCHANGED FROM v1 (plot_fig5.py): this script reuses v1's load() and
fit_pca() functions directly (identical 64-D hidden representation, identical single numpy-SVD
PCA fit reused across panels a/b/c) so the two scripts are guaranteed to plot the same geometry.
Only the visualization layer changed. Style reference: reference/reference_mockup_partial_panel_d_only.png
(figures/fig5_semantics_refined/fig5_semantics_refined.png, panel (d) ONLY -- see
reference/SOURCE.md; this project has no existing mockup for the 3D surface panels, which are
designed fresh here using the same navy/teal/gold palette established across all 5 figures).

Run: python paper_data/figure/fig5/plot_fig5_v2.py
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec
from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_shared"))
from style_v2 import (apply_style, save_all, panel_letter, panel_caption, figure_caption,
                       STAGE_ORDER, STAGE_COLORS, STAGE_LABELS, STAGE_MARKERS,
                       DEGRADATION_CMAP)  # noqa: E402
import data_utils as du  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
from plot_fig5 import load, fit_pca  # noqa: E402

HERE = os.path.dirname(__file__)
OUT_DIR = os.path.join(HERE, "outputs")
LOG_DIR = os.path.join(HERE, "logs")
os.makedirs(LOG_DIR, exist_ok=True)


def _order_line(ax, scores, order_key, **kw):
    order = np.argsort(order_key)
    ax.plot(scores[order, 0], scores[order, 1], color="#B7BDC2", lw=0.8, ls="--", zorder=1, **kw)


def panel_pca_stage(fig, ax, scores, hidden):
    _order_line(ax, scores, hidden["q_true"].values)
    for s in STAGE_ORDER:
        mask = hidden["true_stage"].values == s
        ax.scatter(scores[mask, 0], scores[mask, 1], s=16, color=STAGE_COLORS[s], marker=STAGE_MARKERS[s],
                   alpha=0.8, label=STAGE_LABELS[s], edgecolor="none", zorder=2)
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.legend(loc="best", fontsize=7, markerscale=1.3)
    panel_letter(ax, "a")
    panel_caption(fig, ax, "Shared latent PCA, colored + shaped by true stage")


def panel_pca_q(fig, ax, scores, hidden):
    _order_line(ax, scores, hidden["q_true"].values)
    for s in STAGE_ORDER:
        mask = hidden["true_stage"].values == s
        sc = ax.scatter(scores[mask, 0], scores[mask, 1], s=18, c=hidden["q_true"].values[mask],
                        cmap=DEGRADATION_CMAP, vmin=0, vmax=1, marker=STAGE_MARKERS[s], alpha=0.88,
                        edgecolor="none", zorder=2)
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    cbar = plt.colorbar(sc, ax=ax, fraction=0.045, pad=0.02)
    cbar.set_label("$q_{true}$", fontsize=7)
    cbar.ax.tick_params(labelsize=6)
    panel_letter(ax, "b")
    panel_caption(fig, ax, "Same coordinates, colored by q (shape = true stage)")


def panel_pca_uncertainty(fig, ax, scores, hidden, log_lines):
    _order_line(ax, scores, hidden["q_true"].values)
    for s in STAGE_ORDER:
        mask = hidden["true_stage"].values == s
        sc = ax.scatter(scores[mask, 0], scores[mask, 1], s=18, c=hidden["uncertainty"].values[mask],
                        cmap="magma_r", marker=STAGE_MARKERS[s], alpha=0.88, edgecolor="none", zorder=2)
    mis = hidden["misclassified"].values.astype(bool)
    n_mis = mis.sum()
    if n_mis > 0:
        ax.scatter(scores[mis, 0], scores[mis, 1], s=60, facecolors="none",
                   edgecolors="#B0555E", linewidths=1.3, label=f"misclassified (n={n_mis})")
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    cbar = plt.colorbar(sc, ax=ax, fraction=0.045, pad=0.02)
    cbar.set_label("uncertainty", fontsize=7)
    cbar.ax.tick_params(labelsize=6)
    if n_mis > 0:
        ax.legend(loc="best", fontsize=6.8)
    panel_letter(ax, "c")
    panel_caption(fig, ax, "Same coordinates, colored by uncertainty (shape = true stage)")
    log_lines.append(f"PASS: {n_mis} misclassified samples (of 304) outlined in panel (c).")


def panel_stage_ridge_3d(fig, ax, lifecycle):
    lc = lifecycle.sort_values("relative_life")
    x = lc["relative_life"].values
    stage_cols = [("prob_late", 2, "late"), ("prob_middle", 1, "middle"), ("prob_early", 0, "early")]
    for col, y_level, stage in stage_cols:
        z = lc[col].values
        y = np.full_like(x, y_level, dtype=float)
        ax.plot(x, y, z, color=STAGE_COLORS[stage], lw=1.5)
        top = list(zip(x, y, z))
        bottom = list(zip(x[::-1], y[::-1], np.zeros_like(z)))
        poly = Poly3DCollection([top + bottom], facecolor=STAGE_COLORS[stage], alpha=0.28, edgecolor="none")
        ax.add_collection3d(poly)
    ax.set_xlabel("Relative life", fontsize=7.5, labelpad=3)
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(["Early", "Middle", "Late"], fontsize=7)
    ax.set_zlabel("Stage probability", fontsize=7.5, labelpad=3)
    ax.view_init(elev=24, azim=-58)
    ax.tick_params(labelsize=6.5)
    panel_letter(ax, "d")
    panel_caption(fig, ax, "Stage-probability ridge lines over the C6 lifecycle", pad=0.02)


def panel_confidence_trajectory_3d(fig, ax, lifecycle, log_lines):
    lc = lifecycle.sort_values("relative_life")
    x = lc["relative_life"].values
    y = lc["q_pred"].values
    z = lc["max_prob"].values
    stage_colors_arr = [STAGE_COLORS[s] for s in lc["pred_stage"].values]

    points = np.array([x, y, z]).T.reshape(-1, 1, 3)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    lc3d = Line3DCollection(segments, colors=stage_colors_arr[:-1], linewidths=1.8)
    ax.add_collection3d(lc3d)
    ax.scatter(x, y, z, c=stage_colors_arr, s=8, alpha=0.75, depthshade=False)
    ax.plot(x, y, np.zeros_like(z), color="#B7BDC2", lw=0.9, alpha=0.6, ls="--")

    ax.set_xlim(x.min(), x.max())
    ax.set_ylim(y.min(), y.max())
    ax.set_zlim(0, 1)
    ax.set_xlabel("Relative life", fontsize=7.5, labelpad=3)
    ax.set_ylabel("$q_{pred}$ (raw)", fontsize=7.5, labelpad=3)
    ax.set_zlabel("Max probability\n(confidence)", fontsize=7.5, labelpad=3)
    ax.view_init(elev=24, azim=-58)
    ax.tick_params(labelsize=6.5)
    panel_letter(ax, "e")
    panel_caption(fig, ax, "Joint evolution: life × q_pred × confidence (color = predicted stage)", pad=0.02)
    log_lines.append("PASS: panel (e) plots the 304 real observations directly (no grid interpolation).")


def main():
    apply_style()
    hidden, lifecycle = load()
    log_lines = []
    assert len(hidden) == 304 and len(lifecycle) == 304
    log_lines.append("PASS: hidden_representation.csv and lifecycle_semantics.csv each have 304 rows.")

    scores = fit_pca(hidden, log_lines)

    fig = plt.figure(figsize=(14.5, 15.0))
    gs = GridSpec(2, 3, height_ratios=[1.0, 1.15], hspace=0.55, wspace=0.4, figure=fig,
                  left=0.06, right=0.97, top=0.985, bottom=0.115)

    panel_pca_stage(fig, fig.add_subplot(gs[0, 0]), scores, hidden)
    panel_pca_q(fig, fig.add_subplot(gs[0, 1]), scores, hidden)
    panel_pca_uncertainty(fig, fig.add_subplot(gs[0, 2]), scores, hidden, log_lines)

    gs_3d = GridSpecFromSubplotSpec(1, 2, subplot_spec=gs[1, :], wspace=0.18)
    panel_stage_ridge_3d(fig, fig.add_subplot(gs_3d[0], projection="3d"), lifecycle)
    panel_confidence_trajectory_3d(fig, fig.add_subplot(gs_3d[1], projection="3d"), lifecycle, log_lines)

    figure_caption(fig, "表示几何", subtitle="Fig. 4-6  Shared latent representation geometry and joint probability–position evolution")

    paths = save_all(fig, OUT_DIR, "fig5_v2_reference_style")
    log_lines.append(f"Saved outputs: {paths}")
    with open(os.path.join(LOG_DIR, "validation_v2.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
    print("\n".join(log_lines))
    print("Fig.5 v2 done.")


if __name__ == "__main__":
    main()
