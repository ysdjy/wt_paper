"""Fig. 5 — Degradation semantics and probability structure.

Inputs: full C6 probability/wear trajectory and saved C6 hidden representations.
Output: fig5_semantics.{svg,pdf,png} and data_manifest.json
Run: python figures/fig5_semantics/plot_fig5.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.palette import DC_PSR, STAGE_COLORS
from _shared.style import FIG_WIDTH, apply_publication_style
from _shared.utils_export import export_figure
from _shared.utils_io import read_csv, sha256, write_manifest
from _shared.utils_layout import add_panel_caption, hide_axis_frame


TRAJ_SOURCE = "补充材料/小论文/9_probability_wear_consistency_analysis/Data_5_4_A6_probability_wear_trajectory.csv"
REPR_SOURCE = "补充材料/小论文/10_第五章顶刊风格可视化/figures_representation_space/repr_hidden_hct.csv"
OUT_DIR = Path(__file__).resolve().parent
STAGES = ["early", "middle", "late"]
STAGE_LABELS = ["Early", "Middle", "Late"]
STAGE_MARKERS = {"early": "o", "middle": "^", "late": "s"}
CMAP_LIFE = LinearSegmentedColormap.from_list("life", ["#17324D", "#2A7F86", "#F0D89E"])


def pca_svd(matrix: np.ndarray):
    x = matrix.astype(float)
    x = x - x.mean(axis=0, keepdims=True)
    scale = x.std(axis=0, ddof=1, keepdims=True)
    scale[~np.isfinite(scale) | np.isclose(scale, 0)] = 1
    x /= scale
    u, s, _ = np.linalg.svd(x, full_matrices=False)
    scores = u[:, :2] * s[:2]
    explained = (s[:2] ** 2) / np.sum(s ** 2)
    return scores, explained


def ternary_xy(prob: np.ndarray):
    p_e, p_m, p_l = prob[:, 0], prob[:, 1], prob[:, 2]
    return np.column_stack([p_l + 0.5 * p_m, np.sqrt(3) / 2 * p_m])


def main() -> list[Path]:
    apply_publication_style()
    traj = read_csv(TRAJ_SOURCE).sort_values("run_id").reset_index(drop=True)
    numeric = ["run_id", "VB_true", "q_true", "q_pred", "prob_early", "prob_middle", "prob_late"]
    traj[numeric] = traj[numeric].apply(pd.to_numeric)
    traj["relative_life"] = (traj["run_id"] - traj["run_id"].min()) / (traj["run_id"].max() - traj["run_id"].min())

    repr_df = read_csv(REPR_SOURCE)
    repr_test = repr_df[(repr_df["split"] == "test_C6") & (repr_df["condition"] == "C6")].copy()
    hcols = [column for column in repr_test.columns if column.startswith("h_")]
    scores, explained = pca_svd(repr_test[hcols].to_numpy(float))
    repr_test["PC1"], repr_test["PC2"] = scores[:, 0], scores[:, 1]

    q_true, q_hat = traj["q_true"].to_numpy(float), traj["q_pred"].to_numpy(float)
    r2 = float(1 - np.sum((q_true - q_hat) ** 2) / np.sum((q_true - q_true.mean()) ** 2))
    rho = float(spearmanr(q_true, q_hat).statistic)
    mae = float(np.mean(np.abs(q_true - q_hat)))

    fig, axes = plt.subplots(2, 3, figsize=(FIG_WIDTH, 6.15))
    ax_a, ax_b, ax_c, ax_d, ax_e, ax_f = axes.ravel()
    fig.subplots_adjust(left=0.08, right=0.985, top=0.98, bottom=0.10, hspace=0.76, wspace=0.53)

    # a — stage-aware probability evolution.
    x = traj["relative_life"].to_numpy(float)
    for stage, column, label in zip(STAGES, ["prob_early", "prob_middle", "prob_late"], [r"$p_E$", r"$p_M$", r"$p_L$"]):
        ax_a.plot(x, traj[column], color=STAGE_COLORS[stage], label=label, lw=1.25)
    ax_a.set_xlabel("Relative life")
    ax_a.set_ylabel("Probability")
    ax_a.set_ylim(-0.02, 1.02)
    ax_a.legend(ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.01), columnspacing=0.8)

    # b — probability simplex trajectory.
    prob = traj[["prob_early", "prob_middle", "prob_late"]].to_numpy(float)
    xy = ternary_xy(prob)
    tri = np.array([[0, 0], [0.5, np.sqrt(3) / 2], [1, 0], [0, 0]])
    ax_b.plot(tri[:, 0], tri[:, 1], color="#4D4D4D", lw=0.8)
    for frac in [0.25, 0.5, 0.75]:
        ax_b.plot([frac, 0.5 + 0.5 * frac], [0, np.sqrt(3) / 2 * (1 - frac)], color="#E4E4E4", lw=0.42)
        ax_b.plot([1 - frac, 0.5 * (1 - frac)], [0, np.sqrt(3) / 2 * frac], color="#E4E4E4", lw=0.42)
        ax_b.plot([0.5 * frac, 1 - 0.5 * frac], [np.sqrt(3) / 2 * frac] * 2, color="#E4E4E4", lw=0.42)
    segments = np.stack([xy[:-1], xy[1:]], axis=1)
    line = LineCollection(segments, cmap=CMAP_LIFE, norm=mpl.colors.Normalize(0, 1), linewidth=1.5)
    line.set_array(x[:-1])
    ax_b.add_collection(line)
    idx = np.arange(0, len(xy), 14)
    ax_b.scatter(xy[idx, 0], xy[idx, 1], c=x[idx], cmap=CMAP_LIFE, vmin=0, vmax=1,
                 s=13, edgecolor="white", linewidth=0.25, zorder=3)
    ax_b.text(-0.03, -0.03, "Early", ha="right", va="top", fontsize=6.3, fontweight="bold")
    ax_b.text(0.96, -0.03, "Late", ha="left", va="top", fontsize=6.3, fontweight="bold")
    ax_b.text(0.5, np.sqrt(3) / 2 + 0.02, "Middle", ha="center", va="bottom", fontsize=6.3, fontweight="bold")
    ax_b.set_xlim(-0.10, 1.10)
    ax_b.set_ylim(-0.08, np.sqrt(3) / 2 + 0.08)
    ax_b.set_aspect("equal")
    hide_axis_frame(ax_b)
    cb_b = fig.colorbar(line, ax=ax_b, fraction=0.045, pad=0.025)
    cb_b.set_label("Relative life", fontsize=5.8)
    cb_b.ax.tick_params(labelsize=5.4, length=2)

    # c — continuous degradation-position agreement.
    density_cmap = LinearSegmentedColormap.from_list("density", ["#17324D", "#2A7F86", "#F0D89E"])
    hb = ax_c.hexbin(q_true, q_hat, gridsize=20, mincnt=1, bins="log", cmap=density_cmap,
                     linewidths=0.15, edgecolors="white")
    lo, hi = min(q_true.min(), q_hat.min()), max(q_true.max(), q_hat.max())
    ax_c.plot([lo, hi], [lo, hi], ls="--", color="#555555", lw=0.8)
    ax_c.set_xlabel(r"$q_{true}$")
    ax_c.set_ylabel(r"$\hat q$")
    ax_c.set_xlim(lo - 0.03, hi + 0.03)
    ax_c.set_ylim(lo - 0.03, hi + 0.03)
    ax_c.text(0.04, 0.95, rf"$R^2$ = {r2:.3f}" + "\n" + rf"$\rho$ = {rho:.3f}" + f"\nMAE = {mae:.3f}\nn = {len(traj)}",
              transform=ax_c.transAxes, ha="left", va="top", fontsize=5.8,
              bbox=dict(boxstyle="round,pad=0.20", facecolor="white", edgecolor="#C2C2C2", linewidth=0.5))
    cb_c = fig.colorbar(hb, ax=ax_c, fraction=0.045, pad=0.025)
    cb_c.set_label("Run density", fontsize=5.8)
    cb_c.ax.tick_params(labelsize=5.4, length=2)

    # d — deterministic PCA of saved real hidden representations.
    norm_q = mpl.colors.Normalize(repr_test["q_true"].min(), repr_test["q_true"].max())
    for stage in STAGES:
        sub = repr_test[repr_test["true_stage"].str.lower() == stage]
        ax_d.scatter(sub["PC1"], sub["PC2"], c=sub["q_true"], cmap=CMAP_LIFE, norm=norm_q,
                     marker=STAGE_MARKERS[stage], s=16, alpha=0.82, edgecolor="white", linewidth=0.25,
                     label=stage.title())
    ax_d.set_xlabel(f"PC1 ({100 * explained[0]:.1f}% var.)")
    ax_d.set_ylabel(f"PC2 ({100 * explained[1]:.1f}% var.)")
    ax_d.legend(ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.01), columnspacing=0.6, handletextpad=0.2)
    sm = mpl.cm.ScalarMappable(norm=norm_q, cmap=CMAP_LIFE)
    cb_d = fig.colorbar(sm, ax=ax_d, fraction=0.045, pad=0.025)
    cb_d.set_label("$q$", fontsize=5.8, rotation=0, labelpad=5)
    cb_d.ax.tick_params(labelsize=5.4, length=2)

    # e — physical wear semantics grouped by predicted degradation stage.
    rng = np.random.default_rng(20260821)
    groups = [traj.loc[traj["pred_stage"].str.lower() == stage, "VB_true"].to_numpy(float) for stage in STAGES]
    vp = ax_e.violinplot(groups, positions=[1, 2, 3], widths=0.72, showmeans=False, showmedians=False, showextrema=False)
    for body, stage in zip(vp["bodies"], STAGES):
        body.set_facecolor(STAGE_COLORS[stage])
        body.set_edgecolor("none")
        body.set_alpha(0.35)
    box = ax_e.boxplot(groups, positions=[1, 2, 3], widths=0.25, patch_artist=True, showfliers=False,
                       medianprops=dict(color="#222222", linewidth=1.0),
                       whiskerprops=dict(color="#4D4D4D", linewidth=0.7), capprops=dict(color="#4D4D4D", linewidth=0.7))
    for patch, stage in zip(box["boxes"], STAGES):
        patch.set_facecolor("white")
        patch.set_edgecolor(STAGE_COLORS[stage])
        patch.set_linewidth(0.8)
    for i, (stage, vals) in enumerate(zip(STAGES, groups), start=1):
        take = np.linspace(0, len(vals) - 1, min(40, len(vals)), dtype=int)
        ax_e.scatter(i + rng.uniform(-0.12, 0.12, len(take)), vals[take], s=7,
                     color=STAGE_COLORS[stage], alpha=0.35, edgecolor="none")
    ax_e.set_xticks([1, 2, 3], labels=STAGE_LABELS)
    ax_e.set_ylabel("True flank wear, VB")

    # f — compact evidence summary using only calculated values.
    hide_axis_frame(ax_f)
    ax_f.set_xlim(0, 1)
    ax_f.set_ylim(0, 1)
    medians = [float(np.median(group)) for group in groups]
    agreement = float((traj["true_stage"].str.lower() == traj["pred_stage"].str.lower()).mean())
    for i, (stage, x0) in enumerate(zip(STAGES, [0.18, 0.50, 0.82])):
        ax_f.scatter(x0, 0.72, s=250, color=STAGE_COLORS[stage], alpha=0.88, edgecolor="white", linewidth=0.8)
        ax_f.text(x0, 0.72, stage[0].upper(), ha="center", va="center", color="white", fontweight="bold")
        ax_f.text(x0, 0.56, f"median VB\n{medians[i]:.1f}", ha="center", va="top", fontsize=5.6)
        if i < 2:
            ax_f.annotate("", xy=(x0 + 0.18, 0.72), xytext=(x0 + 0.10, 0.72),
                          arrowprops=dict(arrowstyle="-|>", lw=0.9, color="#888888"))
    ax_f.text(0.50, 0.30, f"Stage agreement = {100 * agreement:.1f}%", ha="center", fontsize=6.2, color=DC_PSR, fontweight="bold")
    ax_f.text(0.50, 0.20, rf"Continuous alignment: $\rho$ = {rho:.3f}", ha="center", fontsize=6.0)
    ax_f.text(0.50, 0.10, "Probability order and physical wear share one lifecycle", ha="center", fontsize=5.4, color="#555555")

    add_panel_caption(fig, ax_a, "a", "Stage-aware probability evolution\nalong tool life", pad=0.041)
    add_panel_caption(fig, [ax_b, cb_b.ax], "b", "Ternary probability-simplex trajectory", pad=0.031)
    add_panel_caption(fig, [ax_c, cb_c.ax], "c", "Continuous q-estimation\nconsistency", pad=0.031)
    add_panel_caption(fig, [ax_d, cb_d.ax], "d", "Latent degradation manifold\n(deterministic PCA)", pad=0.031)
    add_panel_caption(fig, ax_e, "e", "Physical wear semantics\nby predicted stage", pad=0.041)
    add_panel_caption(fig, ax_f, "f", "Summary of degradation-semantic\nalignment", pad=0.041)

    write_manifest(OUT_DIR / "data_manifest.json", {
        "figure": "Fig.5 Degradation Semantics and Probability Structure", "audit_status": "passed",
        "sources": [
            {"path": TRAJ_SOURCE, "sha256": sha256(TRAJ_SOURCE), "table_or_rows": "full C6 lifecycle, 304 runs",
             "columns": ["run_id", "VB_true", "q_true", "q_pred", "true_stage", "pred_stage", "prob_early", "prob_middle", "prob_late"],
             "aggregation": "q statistics calculated across all 304 rows; wear grouped by predicted stage",
             "normalization": "run_id min-max normalized only to relative life; probabilities, q and VB remain on source scales",
             "bootstrap": "not used"},
            {"path": REPR_SOURCE, "sha256": sha256(REPR_SOURCE), "table_or_rows": "split=test_C6 and condition=C6, 304 rows",
             "columns": ["h_00–h_63", "q_true", "true_stage"],
             "aggregation": "feature standardization followed by deterministic two-component NumPy SVD PCA",
             "normalization": "feature-wise z standardization before PCA", "bootstrap": "not used"},
        ],
        "key_values": {"n": len(traj), "R2": r2, "Spearman_rho": rho, "MAE": mae,
                       "stage_agreement": agreement, "predicted_stage_median_VB": dict(zip(STAGE_LABELS, medians)),
                       "PCA_explained_variance": explained.tolist()},
        "warnings": ["The PCA panel uses saved real hidden features only; no retraining, UMAP/t-SNE optimization, or label fitting is performed."],
    })
    return export_figure(fig, OUT_DIR / "fig5_semantics")


if __name__ == "__main__":
    main()
