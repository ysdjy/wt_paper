from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from scipy.stats import spearmanr

from common import (
    CMAP_ABSOLUTE,
    CMAP_LIFE,
    OUT,
    apply_style,
    panel_label,
    pca_svd,
    read_csv,
    save_figure,
    write_plot_data,
)


TRAJ_SOURCE = "补充材料/小论文/9_probability_wear_consistency_analysis/Data_5_4_A6_probability_wear_trajectory.csv"
REPR_SOURCE = "补充材料/小论文/10_第五章顶刊风格可视化/figures_representation_space/repr_hidden_hct.csv"

STAGES = ["early", "middle", "late"]
STAGE_LABELS = ["Early", "Middle", "Late"]
STAGE_COLORS = {"early": "#315A7D", "middle": "#D9A441", "late": "#D55E00"}
STAGE_MARKERS = {"early": "o", "middle": "^", "late": "s"}


def ternary_xy(prob: np.ndarray) -> np.ndarray:
    # Vertices: Early=(0,0), Middle=(0.5,sqrt(3)/2), Late=(1,0)
    p_e, p_m, p_l = prob[:, 0], prob[:, 1], prob[:, 2]
    x = p_l + 0.5 * p_m
    y = (np.sqrt(3) / 2.0) * p_m
    return np.column_stack([x, y])


def make_figure():
    apply_style()
    traj = read_csv(TRAJ_SOURCE)
    numeric = ["run_id", "VB_true", "q_true", "q_pred", "prob_early", "prob_middle", "prob_late"]
    traj[numeric] = traj[numeric].apply(pd.to_numeric)
    traj = traj.sort_values("run_id").reset_index(drop=True)
    traj["relative_life"] = (traj["run_id"] - traj["run_id"].min()) / (traj["run_id"].max() - traj["run_id"].min())
    write_plot_data(traj[["run_id", "relative_life", "VB_true", "q_true", "q_pred", "true_stage",
                          "pred_stage", "prob_early", "prob_middle", "prob_late"]],
                    "fig5_D1_C6_lifecycle_semantics.csv")

    repr_df = read_csv(REPR_SOURCE)
    repr_test = repr_df[(repr_df["split"] == "test_C6") & (repr_df["condition"] == "C6")].copy()
    hcols = [c for c in repr_test.columns if c.startswith("h_")]
    scores, explained = pca_svd(repr_test[hcols].to_numpy(float), 2)
    repr_test["PC1"] = scores[:, 0]
    repr_test["PC2"] = scores[:, 1]
    pca_export = repr_test[["sample_id", "condition", "run_id", "true_stage", "q_true", "q_hat", "PC1", "PC2"]]
    write_plot_data(pca_export, "fig5_D1_C6_hidden_representation_PCA.csv")

    q_true = traj["q_true"].to_numpy(float)
    q_hat = traj["q_pred"].to_numpy(float)
    mae = float(np.mean(np.abs(q_true - q_hat)))
    r2 = float(1.0 - np.sum((q_true - q_hat) ** 2) / np.sum((q_true - q_true.mean()) ** 2))
    rho = float(spearmanr(q_true, q_hat).statistic)
    write_plot_data(pd.DataFrame([{"n": len(traj), "R2": r2, "Spearman_rho": rho, "MAE": mae}]),
                    "fig5_q_true_vs_q_hat_statistics.csv")

    fig = plt.figure(figsize=(7.2, 6.35))
    gs = fig.add_gridspec(3, 4, height_ratios=[1.0, 1.0, 0.92], width_ratios=[1.0, 1.0, 1.0, 1.0],
                          hspace=0.48, wspace=0.55)
    ax_b = fig.add_subplot(gs[0:2, 0:2])
    a_gs = gs[0, 2:4].subgridspec(2, 1, height_ratios=[3.0, 0.85], hspace=0.05)
    ax_a = fig.add_subplot(a_gs[0, 0])
    ax_aq = fig.add_subplot(a_gs[1, 0], sharex=ax_a)
    ax_c = fig.add_subplot(gs[1, 2:4])
    ax_d = fig.add_subplot(gs[2, 0:2])
    ax_e = fig.add_subplot(gs[2, 2:4])

    # a | full lifecycle probability trajectory + q-hat strip
    x = traj["relative_life"].to_numpy(float)
    for col, label, color in [
        ("prob_early", "$p_E$", STAGE_COLORS["early"]),
        ("prob_middle", "$p_M$", STAGE_COLORS["middle"]),
        ("prob_late", "$p_L$", STAGE_COLORS["late"]),
    ]:
        ax_a.plot(x, traj[col], color=color, label=label, lw=1.25)
    ax_a.set_ylabel("Probability")
    ax_a.set_ylim(-0.02, 1.02)
    ax_a.set_title("Full C6 lifecycle probability trajectory", loc="left", pad=5)
    ax_a.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.52, 1.03), columnspacing=1.0, handlelength=1.8)
    ax_a.tick_params(labelbottom=False)
    panel_label(ax_a, "a", x=-0.12)
    ax_aq.plot(x, q_hat, color="#333333", lw=0.9)
    ax_aq.fill_between(x, 0, q_hat, color="#BDBDBD", alpha=0.38, linewidth=0)
    ax_aq.set_ylabel(r"$\hat q$", rotation=0, labelpad=7)
    ax_aq.set_xlabel("Relative life")
    ax_aq.set_ylim(min(-0.02, q_hat.min() - 0.03), max(1.02, q_hat.max() + 0.03))
    ax_aq.spines["top"].set_visible(False)

    # b | ternary hero trajectory
    prob = traj[["prob_early", "prob_middle", "prob_late"]].to_numpy(float)
    xy = ternary_xy(prob)
    tri = np.array([[0, 0], [0.5, np.sqrt(3) / 2], [1, 0], [0, 0]])
    ax_b.plot(tri[:, 0], tri[:, 1], color="#4D4D4D", lw=0.8)
    # restrained probability grid
    for f in [0.25, 0.5, 0.75]:
        ax_b.plot([f, 0.5 + 0.5 * f], [0, (np.sqrt(3) / 2) * (1 - f)], color="#E2E2E2", lw=0.45)
        ax_b.plot([1 - f, 0.5 * (1 - f)], [0, (np.sqrt(3) / 2) * f], color="#E2E2E2", lw=0.45)
        ax_b.plot([0.5 * f, 1 - 0.5 * f], [(np.sqrt(3) / 2) * f] * 2, color="#E2E2E2", lw=0.45)
    segments = np.stack([xy[:-1], xy[1:]], axis=1)
    lc = LineCollection(segments, cmap=CMAP_LIFE, norm=mpl.colors.Normalize(0, 1), linewidth=1.5)
    lc.set_array(x[:-1])
    ax_b.add_collection(lc)
    idx = np.arange(0, len(xy), 12)
    ax_b.scatter(xy[idx, 0], xy[idx, 1], c=x[idx], cmap=CMAP_LIFE, vmin=0, vmax=1,
                 s=12, edgecolor="white", linewidth=0.25, zorder=3)
    ax_b.scatter(xy[0, 0], xy[0, 1], marker="o", s=35, facecolor="white", edgecolor="#17324D", lw=1.0, zorder=4)
    ax_b.scatter(xy[-1, 0], xy[-1, 1], marker="s", s=35, facecolor="#F3D9A3", edgecolor="#5C4A24", lw=0.8, zorder=4)
    ax_b.text(-0.035, -0.035, "Early", ha="right", va="top", fontsize=7.0, fontweight="bold")
    ax_b.text(1.035, -0.035, "Late", ha="left", va="top", fontsize=7.0, fontweight="bold")
    ax_b.text(0.5, np.sqrt(3) / 2 + 0.035, "Middle", ha="center", va="bottom", fontsize=7.0, fontweight="bold")
    ax_b.set_xlim(-0.10, 1.10)
    ax_b.set_ylim(-0.10, np.sqrt(3) / 2 + 0.10)
    ax_b.set_aspect("equal")
    ax_b.axis("off")
    ax_b.set_title("Ordered trajectory in probability simplex", loc="left", pad=4)
    panel_label(ax_b, "b", x=-0.04, y=0.98)
    cbar = fig.colorbar(lc, ax=ax_b, orientation="horizontal", fraction=0.045, pad=0.02, aspect=28)
    cbar.set_label("Relative life", fontsize=6.2)
    cbar.ax.tick_params(labelsize=5.8, width=0.5, length=2)

    # c | density relationship between q_true and q_hat
    hb = ax_c.hexbin(q_true, q_hat, gridsize=22, mincnt=1, bins="log", cmap=CMAP_ABSOLUTE,
                     linewidths=0.15, edgecolors="white")
    lo = min(q_true.min(), q_hat.min())
    hi = max(q_true.max(), q_hat.max())
    ax_c.plot([lo, hi], [lo, hi], ls="--", color="#4D4D4D", lw=0.8)
    ax_c.set_xlabel("$q_{true}$")
    ax_c.set_ylabel(r"$\hat q$")
    ax_c.set_xlim(lo - 0.03, hi + 0.03)
    ax_c.set_ylim(lo - 0.03, hi + 0.03)
    ax_c.set_title("Continuous degradation-position agreement", loc="left", pad=5)
    ax_c.text(0.03, 0.94, f"$R^2$ = {r2:.3f}\nSpearman $\\rho$ = {rho:.3f}\nMAE = {mae:.3f}",
              transform=ax_c.transAxes, ha="left", va="top", fontsize=6.2,
              bbox=dict(boxstyle="round,pad=0.22", facecolor="white", edgecolor="#C0C0C0", linewidth=0.5))
    cb_c = fig.colorbar(hb, ax=ax_c, fraction=0.045, pad=0.03)
    cb_c.set_label("Run density", fontsize=6.0)
    cb_c.ax.tick_params(labelsize=5.6, width=0.5, length=2)
    panel_label(ax_c, "c", x=-0.12)

    # d | real shared hidden representation, PCA only (no retraining, no label use)
    norm_q = mpl.colors.Normalize(repr_test["q_true"].min(), repr_test["q_true"].max())
    for stage in STAGES:
        sub = repr_test[repr_test["true_stage"] == stage]
        ax_d.scatter(sub["PC1"], sub["PC2"], c=sub["q_true"], cmap=CMAP_LIFE, norm=norm_q,
                     marker=STAGE_MARKERS[stage], s=17, alpha=0.82, edgecolor="#FFFFFF", linewidth=0.25,
                     label=stage.title())
    ax_d.set_xlabel(f"PC1 ({100 * explained[0]:.1f}% var.)")
    ax_d.set_ylabel(f"PC2 ({100 * explained[1]:.1f}% var.)")
    ax_d.set_title("Shared latent degradation manifold", loc="left", pad=5)
    ax_d.legend(ncol=3, loc="upper right", fontsize=5.7, handletextpad=0.2, columnspacing=0.7)
    sm = mpl.cm.ScalarMappable(norm=norm_q, cmap=CMAP_LIFE)
    cb_d = fig.colorbar(sm, ax=ax_d, fraction=0.045, pad=0.03)
    cb_d.ax.set_title("$q$", fontsize=6.0, pad=2)
    cb_d.ax.tick_params(labelsize=5.6, width=0.5, length=2)
    panel_label(ax_d, "d", x=-0.12)

    # e | physical wear semantics
    rng = np.random.default_rng(20260821)
    groups = [traj.loc[traj["pred_stage"] == stage, "VB_true"].to_numpy(float) for stage in STAGES]
    vp = ax_e.violinplot(groups, positions=np.arange(1, 4), widths=0.75,
                         showmeans=False, showmedians=False, showextrema=False)
    for body, stage in zip(vp["bodies"], STAGES):
        body.set_facecolor(STAGE_COLORS[stage])
        body.set_edgecolor("none")
        body.set_alpha(0.35)
    box = ax_e.boxplot(groups, positions=np.arange(1, 4), widths=0.25, patch_artist=True,
                       showfliers=False, medianprops=dict(color="#222222", linewidth=1.0),
                       whiskerprops=dict(color="#4D4D4D", linewidth=0.7),
                       capprops=dict(color="#4D4D4D", linewidth=0.7))
    for patch, stage in zip(box["boxes"], STAGES):
        patch.set_facecolor("white")
        patch.set_edgecolor(STAGE_COLORS[stage])
        patch.set_linewidth(0.8)
    for i, (stage, vals) in enumerate(zip(STAGES, groups), start=1):
        idx = np.linspace(0, len(vals) - 1, min(45, len(vals)), dtype=int) if len(vals) else np.array([], dtype=int)
        jitter = rng.uniform(-0.13, 0.13, len(idx))
        ax_e.scatter(i + jitter, vals[idx], s=7, color=STAGE_COLORS[stage], alpha=0.35,
                     edgecolor="none")
    ax_e.set_xticks([1, 2, 3], labels=STAGE_LABELS)
    ax_e.set_xlabel("Predicted degradation state")
    ax_e.set_ylabel("True flank wear, VB")
    ax_e.set_title("Physical wear semantics", loc="left", pad=5)
    panel_label(ax_e, "e", x=-0.12)

    fig.subplots_adjust(left=0.08, right=0.985, top=0.965, bottom=0.085)
    return fig


def main():
    return save_figure(make_figure(), OUT / "fig5_semantics", "fig5_semantics")


if __name__ == "__main__":
    main()
