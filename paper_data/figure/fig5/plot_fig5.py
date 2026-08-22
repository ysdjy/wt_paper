"""
Fig.5 (paper Fig. 4-6): shared latent representation geometry and joint probability-position
evolution.

Inputs:
  - paper_data/07_figure_ready/fig5/hidden_representation.csv   304 rows x 88 cols (64-D shared
    hidden representation h_00..h_63 + true/pred stage, q_true, q_hat, p_E/M/L, uncertainty,
    entropy, misclassified). Already the frozen 64-D representation -- no network is re-run here.
  - paper_data/07_figure_ready/fig5/lifecycle_semantics.csv    304 rows, relative_life, prob_*,
    max_prob, q_pred -- drives the two 3D lifecycle panels.

No sklearn is installed in this environment, so PCA is implemented via numpy SVD in
_shared/data_utils.py::pca_2d. ONE PCA is fit on the 64-D representation and the SAME 2D
coordinates are reused for panels (a)/(b)/(c) -- only the point color changes -- per the task's
explicit requirement not to re-fit PCA per panel.

Panels (d)/(e) are 3D RIDGE-LINE / TRAJECTORY plots built directly from the 304 real observations,
not from an interpolated mesh: with only one z-value per real (x, stage) or (x, y) combination,
building a literal "surface" would require fabricating values between real samples along an axis
where no interpolation is scientifically justified. Ridge-lines/trajectories give the same visual
"joint evolution" reading the design doc asks for while keeping every plotted value traceable to
one of the 304 test runs.

Outputs: paper_data/figure/fig5/outputs/fig5_main.{png,pdf,svg}
Logs:    paper_data/figure/fig5/logs/validation.txt

Run: python paper_data/figure/fig5/plot_fig5.py
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_shared"))
from style import apply_style, save_all, STAGE_ORDER, STAGE_COLORS, STAGE_LABELS  # noqa: E402
import data_utils as du  # noqa: E402

HERE = os.path.dirname(__file__)
OUT_DIR = os.path.join(HERE, "outputs")
LOG_DIR = os.path.join(HERE, "logs")
os.makedirs(LOG_DIR, exist_ok=True)


def load():
    hidden = du.read_csv("07_figure_ready", "fig5", "hidden_representation.csv")
    lifecycle = du.read_csv("07_figure_ready", "fig5", "lifecycle_semantics.csv")
    return hidden, lifecycle


def fit_pca(hidden, log_lines):
    h_cols = [c for c in hidden.columns if c.startswith("h_")]
    assert len(h_cols) == 64, f"expected 64 hidden dims, got {len(h_cols)}"
    X = hidden[h_cols].values
    scores, explained, _ = du.pca_2d(X)
    log_lines.append(f"PASS: single PCA fit on 64-D hidden representation (n={X.shape[0]}), "
                     f"reused for panels (a)/(b)/(c). Explained variance ratio PC1={explained[0]:.3f}, PC2={explained[1]:.3f}.")
    return scores


def panel_pca_stage(ax, scores, hidden):
    for s in STAGE_ORDER:
        mask = hidden["true_stage"].values == s
        ax.scatter(scores[mask, 0], scores[mask, 1], s=10, color=STAGE_COLORS[s],
                   alpha=0.75, label=STAGE_LABELS[s], edgecolor="none")
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.set_title("(a) Shared latent PCA, colored by true stage", loc="left", fontweight="bold")
    ax.legend(loc="best", fontsize=6.5)


def panel_pca_q(ax, scores, hidden):
    sc = ax.scatter(scores[:, 0], scores[:, 1], s=10, c=hidden["q_true"].values, cmap="viridis", alpha=0.85)
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.set_title("(b) Same PCA coordinates, colored by q_true", loc="left", fontweight="bold")
    cbar = plt.colorbar(sc, ax=ax, fraction=0.045, pad=0.02)
    cbar.set_label("q_true", fontsize=6.5)
    cbar.ax.tick_params(labelsize=6)


def panel_pca_uncertainty(ax, scores, hidden, log_lines):
    sc = ax.scatter(scores[:, 0], scores[:, 1], s=10, c=hidden["uncertainty"].values, cmap="magma_r", alpha=0.85)
    mis = hidden["misclassified"].values.astype(bool)
    n_mis = mis.sum()
    if n_mis > 0:
        ax.scatter(scores[mis, 0], scores[mis, 1], s=38, facecolors="none",
                   edgecolors="black", linewidths=1.0, label=f"misclassified (n={n_mis})")
        ax.legend(loc="best", fontsize=6.3)
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.set_title("(c) Same PCA coordinates, colored by uncertainty", loc="left", fontweight="bold")
    cbar = plt.colorbar(sc, ax=ax, fraction=0.045, pad=0.02)
    cbar.set_label("uncertainty", fontsize=6.5)
    cbar.ax.tick_params(labelsize=6)
    log_lines.append(f"PASS: {n_mis} misclassified samples (of 304) outlined in panel (c) uncertainty view.")


def panel_stage_ridge_3d(ax, lifecycle):
    lc = lifecycle.sort_values("relative_life")
    x = lc["relative_life"].values
    stage_cols = [("prob_late", 2, "late"), ("prob_middle", 1, "middle"), ("prob_early", 0, "early")]
    for col, y_level, stage in stage_cols:
        z = lc[col].values
        y = np.full_like(x, y_level, dtype=float)
        ax.plot(x, y, z, color=STAGE_COLORS[stage], lw=1.4)
        # ridge fill: a flat ribbon polygon in the plane y=y_level (top edge follows the real
        # probability curve, bottom edge is z=0) -- built directly as a polygon since the (x,y)
        # point cloud is degenerate (constant y) and cannot be Delaunay-triangulated by plot_trisurf.
        top = list(zip(x, y, z))
        bottom = list(zip(x[::-1], y[::-1], np.zeros_like(z)))
        poly = Poly3DCollection([top + bottom], facecolor=STAGE_COLORS[stage], alpha=0.25, edgecolor="none")
        ax.add_collection3d(poly)
    ax.set_xlabel("Relative life", fontsize=7, labelpad=2)
    ax.set_ylabel("", fontsize=7)
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(["Early", "Middle", "Late"], fontsize=6.5)
    ax.set_zlabel("Stage probability", fontsize=7, labelpad=2)
    ax.set_title("(d) Stage-probability ridge lines over the C6 lifecycle", loc="left", fontweight="bold", fontsize=9)
    ax.view_init(elev=22, azim=-60)
    ax.tick_params(labelsize=6)


def panel_confidence_trajectory_3d(ax, lifecycle, log_lines):
    lc = lifecycle.sort_values("relative_life")
    x = lc["relative_life"].values
    y = lc["q_pred"].values
    z = lc["max_prob"].values
    stage_colors_arr = [STAGE_COLORS[s] for s in lc["pred_stage"].values]

    points = np.array([x, y, z]).T.reshape(-1, 1, 3)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    lc3d = Line3DCollection(segments, colors=stage_colors_arr[:-1], linewidths=1.6)
    ax.add_collection3d(lc3d)
    ax.scatter(x, y, z, c=stage_colors_arr, s=6, alpha=0.7, depthshade=False)
    # floor projection: q_pred trajectory at z=0 for spatial context (real values, just projected)
    ax.plot(x, y, np.zeros_like(z), color="grey", lw=0.8, alpha=0.5, ls="--")

    ax.set_xlim(x.min(), x.max())
    ax.set_ylim(y.min(), y.max())
    ax.set_zlim(0, 1)
    ax.set_xlabel("Relative life", fontsize=7, labelpad=2)
    ax.set_ylabel("q_pred (raw)", fontsize=7, labelpad=2)
    ax.set_zlabel("max probability\n(confidence)", fontsize=7, labelpad=2)
    ax.set_title("(e) Joint evolution: life × q_pred × confidence\n(color = predicted stage; dashed = q_pred floor projection)",
                loc="left", fontweight="bold", fontsize=9)
    ax.view_init(elev=22, azim=-60)
    ax.tick_params(labelsize=6)
    log_lines.append("PASS: panel (e) plots the 304 real (relative_life, q_pred, max_prob) observations directly as a 3D "
                     "trajectory + scatter -- no grid interpolation used, so every plotted value traces back to one test run.")


def main():
    apply_style()
    hidden, lifecycle = load()
    log_lines = []

    assert len(hidden) == 304, f"expected 304 samples, got {len(hidden)}"
    assert len(lifecycle) == 304
    assert set(hidden["true_stage"].unique()) <= set(STAGE_ORDER)
    log_lines.append("PASS: hidden_representation.csv and lifecycle_semantics.csv each have 304 rows (C6 common-universe test set).")

    scores = fit_pca(hidden, log_lines)

    fig = plt.figure(figsize=(13.5, 15.5))
    gs = GridSpec(2, 3, height_ratios=[1.0, 1.15], hspace=0.4, wspace=0.35, figure=fig)

    ax_a = fig.add_subplot(gs[0, 0])
    panel_pca_stage(ax_a, scores, hidden)
    ax_b = fig.add_subplot(gs[0, 1])
    panel_pca_q(ax_b, scores, hidden)
    ax_c = fig.add_subplot(gs[0, 2])
    panel_pca_uncertainty(ax_c, scores, hidden, log_lines)

    from matplotlib.gridspec import GridSpecFromSubplotSpec
    gs_3d = GridSpecFromSubplotSpec(1, 2, subplot_spec=gs[1, :], wspace=0.15)
    ax_d = fig.add_subplot(gs_3d[0], projection="3d")
    panel_stage_ridge_3d(ax_d, lifecycle)
    ax_e = fig.add_subplot(gs_3d[1], projection="3d")
    panel_confidence_trajectory_3d(ax_e, lifecycle, log_lines)

    fig.suptitle("Shared 64-D latent representation geometry and joint probability–position\n"
                 "evolution on PHM2010 D1/C6 (n=304): same PCA coordinates colored by stage/q/\n"
                 "uncertainty, plus lifecycle stage-probability and confidence trajectories",
                 fontsize=10.6, y=0.995)
    fig.subplots_adjust(top=0.90, bottom=0.03)

    paths = save_all(fig, OUT_DIR, "fig5_main")
    log_lines.append(f"Saved outputs: {paths}")

    with open(os.path.join(LOG_DIR, "validation.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
    print("\n".join(log_lines))
    print("Fig.5 done.")


if __name__ == "__main__":
    main()
