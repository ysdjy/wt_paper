"""
Fig.4 (paper Fig. 4-5): ordered degradation semantics -- lifecycle probability trajectory,
probability simplex, continuous degradation-position (q) agreement, and physical wear (VB)
semantics. Four panels designed as one "same C6 lifecycle in four projections" story, not four
independent plots (per DCPSR_Chapter4_CN_Detailed.docx 4.5).

Inputs (all under paper_data/07_figure_ready/fig5/):
  - lifecycle_semantics.csv   304 rows, run-level VB_true/VB_smooth/q_true/q_pred/probs/relative_life
  - simplex_trajectory.csv    304 rows, run-level p_E/p_M/p_L for the ternary view
  - q_agreement.csv           304 rows, q_true vs RAW (unrenormalized) q_pred pairs
  - wear_by_predicted_stage.csv  3-row aggregate, used only to cross-check panel (d) group means

VB unit: micrometers (um), confirmed via DCPSR_Chapter4_CN_Detailed.docx ("VB (um)"; VB means
100.55/126.29/205.46 um match this project's data exactly) -- 00_metadata/Q_DEFINITIONS.md itself
does not state the unit, so the docx is the authoritative source for this fact.

q agreement formula: R^2 is the coefficient of determination 1-SS_res/SS_tot using RAW q_pred
as-is (NOT squared Pearson correlation, NOT q_pred_norm) -- see _shared/data_utils.py docstring
and paper_data/figure/FIGURE_PROGRESS.md for the verification that distinguishes these.

Outputs: paper_data/figure/fig4/outputs/fig4_main.{png,pdf,svg}
Logs:    paper_data/figure/fig4/logs/validation.txt

Run: python paper_data/figure/fig4/plot_fig4.py
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec
from matplotlib.collections import LineCollection
from scipy import stats

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_shared"))
from style import apply_style, save_all, STAGE_ORDER, STAGE_COLORS, STAGE_LABELS  # noqa: E402
import data_utils as du  # noqa: E402

HERE = os.path.dirname(__file__)
OUT_DIR = os.path.join(HERE, "outputs")
LOG_DIR = os.path.join(HERE, "logs")
os.makedirs(LOG_DIR, exist_ok=True)


def load():
    lifecycle = du.read_csv("07_figure_ready", "fig5", "lifecycle_semantics.csv")
    simplex = du.read_csv("07_figure_ready", "fig5", "simplex_trajectory.csv")
    q_agree = du.read_csv("07_figure_ready", "fig5", "q_agreement.csv")
    wear_agg = du.read_csv("07_figure_ready", "fig5", "wear_by_predicted_stage.csv")
    return lifecycle, simplex, q_agree, wear_agg


def panel_lifecycle(fig, gs_slot, lifecycle):
    lc = lifecycle.sort_values("relative_life").reset_index(drop=True)
    gsx = GridSpecFromSubplotSpec(2, 1, subplot_spec=gs_slot, height_ratios=[2.0, 1.0], hspace=0.12)
    ax_p = fig.add_subplot(gsx[0])
    ax_q = fig.add_subplot(gsx[1], sharex=ax_p)

    # background shading by true_stage contiguous runs
    stage_ids = lc["true_stage"].values
    x = lc["relative_life"].values
    start = 0
    for i in range(1, len(stage_ids) + 1):
        if i == len(stage_ids) or stage_ids[i] != stage_ids[start]:
            ax_p.axvspan(x[start], x[i - 1] if i - 1 < len(x) else x[-1],
                        color=STAGE_COLORS[stage_ids[start]], alpha=0.07, lw=0)
            start = i

    ax_p.stackplot(x, lc["prob_early"], lc["prob_middle"], lc["prob_late"],
                    colors=[STAGE_COLORS["early"], STAGE_COLORS["middle"], STAGE_COLORS["late"]],
                    alpha=0.85, labels=["p(Early)", "p(Middle)", "p(Late)"])
    ax_p.set_ylabel("Stage\nprobability")
    ax_p.set_ylim(0, 1)
    ax_p.set_title("(a) Full C6 lifecycle: stage probability + degradation position (n=304)", loc="left", fontweight="bold")
    ax_p.legend(loc="lower left", ncol=3, fontsize=6.5, frameon=True, facecolor="white",
                framealpha=0.88, edgecolor="none")
    plt.setp(ax_p.get_xticklabels(), visible=False)

    ax_q.plot(x, lc["q_true"], color="black", lw=1.3, label="q_true (condition-relative wear position)")
    ax_q.plot(x, lc["q_pred"], color="#C1272D", lw=1.1, alpha=0.85, label="q_pred (raw model head)")
    ax_q.set_ylabel("q")
    ax_q.set_xlabel("Relative life  (run_id-12)/303")
    ax_q.set_ylim(0, 1.02)
    ax_q.legend(loc="upper left", fontsize=6.3, ncol=2)


def panel_simplex(ax, simplex):
    x, y = du.ternary_coords(simplex["prob_early"], simplex["prob_middle"], simplex["prob_late"])
    rel_life = simplex["relative_life"].values
    order = np.argsort(simplex["run_id"].values)
    x, y, rel_life = x[order], y[order], rel_life[order]

    tri_x = [0, 1, 0.5, 0]
    tri_y = [0, 0, np.sqrt(3) / 2, 0]
    ax.plot(tri_x, tri_y, color="black", lw=0.9)
    ax.text(-0.06, -0.03, "Early", fontsize=7.5, color=STAGE_COLORS["early"], fontweight="bold", ha="right")
    ax.text(1.06, -0.03, "Late", fontsize=7.5, color=STAGE_COLORS["late"], fontweight="bold", ha="left")
    ax.text(0.5, np.sqrt(3) / 2 + 0.03, "Middle", fontsize=7.5, color=STAGE_COLORS["middle"], fontweight="bold", ha="center")

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    lc = LineCollection(segments, cmap="viridis", array=rel_life[:-1], linewidth=1.6, alpha=0.9)
    ax.add_collection(lc)
    sc = ax.scatter(x, y, c=rel_life, cmap="viridis", s=6, zorder=3)
    cbar = plt.colorbar(sc, ax=ax, fraction=0.045, pad=0.02)
    cbar.set_label("relative life", fontsize=6.5)
    cbar.ax.tick_params(labelsize=6)

    ax.set_xlim(-0.15, 1.15)
    ax.set_ylim(-0.12, np.sqrt(3) / 2 + 0.12)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("(b) Ordered trajectory in the probability simplex", loc="left", fontweight="bold")


def panel_q_agreement(ax, q_agree, log_lines):
    yt = q_agree["q_true"].values
    yp = q_agree["q_pred"].values
    assert (q_agree["q_comparison_definition"] == "q_true_vs_raw_q_pred_no_renormalization").all()
    r2 = du.r2_coefficient_of_determination(yt, yp)
    rho = stats.spearmanr(yt, yp)[0]
    mae = np.abs(yt - yp).mean()

    assert np.isclose(r2, 0.748, atol=0.01), r2
    assert np.isclose(rho, 0.963, atol=0.01), rho
    assert np.isclose(mae, 0.113, atol=0.01), mae
    log_lines.append(f"PASS: q agreement (raw q_pred vs q_true, n=304): R2={r2:.4f} (~0.748), "
                      f"Spearman rho={rho:.4f} (~0.963), MAE={mae:.4f} (~0.113).")

    hb = ax.hexbin(yt, yp, gridsize=28, cmap="Blues", mincnt=1)
    ax.plot([0, 1], [0, 1], color="#C1272D", lw=1.0, ls="--", label="y = x")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("q_true (condition-relative wear position)")
    ax.set_ylabel("q_pred (raw model head, no renorm.)")
    ax.set_title("(c) Continuous degradation-position agreement", loc="left", fontweight="bold")
    ax.text(0.03, 0.97, f"R² = {r2:.3f}\nSpearman ρ = {rho:.3f}\nMAE = {mae:.3f}",
            transform=ax.transAxes, va="top", ha="left", fontsize=7.5,
            bbox=dict(boxstyle="round", fc="white", ec="#888888", alpha=0.9))
    ax.legend(loc="lower right", fontsize=6.5)
    cbar = plt.colorbar(hb, ax=ax, fraction=0.045, pad=0.02)
    cbar.set_label("count", fontsize=6.5)
    cbar.ax.tick_params(labelsize=6)


def panel_wear_violin(ax, lifecycle, wear_agg, log_lines):
    rng = np.random.default_rng(0)
    positions = {"early": 0, "middle": 1, "late": 2}
    parts_data = [lifecycle[lifecycle["pred_stage"] == s]["VB_true"].values for s in STAGE_ORDER]
    vp = ax.violinplot(parts_data, positions=[positions[s] for s in STAGE_ORDER],
                        showextrema=False, widths=0.8)
    for body, s in zip(vp["bodies"], STAGE_ORDER):
        body.set_facecolor(STAGE_COLORS[s])
        body.set_alpha(0.35)
        body.set_edgecolor(STAGE_COLORS[s])
    bp = ax.boxplot(parts_data, positions=[positions[s] for s in STAGE_ORDER], widths=0.14,
                     showfliers=False, patch_artist=True,
                     medianprops=dict(color="black", lw=1.3),
                     boxprops=dict(facecolor="white", edgecolor="black", lw=0.8),
                     whiskerprops=dict(color="black", lw=0.8), capprops=dict(color="black", lw=0.8))
    for s in STAGE_ORDER:
        vals = lifecycle[lifecycle["pred_stage"] == s]["VB_true"].values
        jitter = rng.normal(0, 0.045, size=len(vals))
        ax.scatter(positions[s] + jitter, vals, s=5, color=STAGE_COLORS[s], alpha=0.55, zorder=3)

    means_computed = {}
    for s in STAGE_ORDER:
        vals = lifecycle[lifecycle["pred_stage"] == s]["VB_true"].values
        means_computed[s] = vals.mean()
        agg_row = wear_agg[wear_agg["predicted_stage"] == s].iloc[0]
        assert np.isclose(vals.mean(), agg_row["VB_mean"], atol=1e-6), (s, vals.mean(), agg_row["VB_mean"])
        assert np.isclose(np.median(vals), agg_row["VB_median"], atol=1e-6), s
    log_lines.append(f"PASS: recomputed per-pred-stage VB_true mean/median from lifecycle_semantics.csv "
                      f"exactly match wear_by_predicted_stage.csv for all 3 stages.")
    assert np.isclose(means_computed["early"], 100.55, atol=0.05), means_computed["early"]
    assert np.isclose(means_computed["middle"], 126.29, atol=0.05), means_computed["middle"]
    assert np.isclose(means_computed["late"], 205.46, atol=0.05), means_computed["late"]
    ratio = means_computed["late"] / means_computed["early"]
    assert np.isclose(ratio, 2.04, atol=0.02), ratio
    log_lines.append(f"PASS: VB means Early={means_computed['early']:.2f}, Middle={means_computed['middle']:.2f}, "
                      f"Late={means_computed['late']:.2f} um (~100.55/126.29/205.46); Late/Early ratio={ratio:.3f} (~2.04).")

    for s in STAGE_ORDER:
        ax.annotate(f"mean={means_computed[s]:.1f}", (positions[s], means_computed[s]),
                    xytext=(positions[s] + 0.32, means_computed[s]), fontsize=6.3, color=STAGE_COLORS[s])

    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels([STAGE_LABELS[s] for s in STAGE_ORDER])
    ax.set_ylabel("True flank wear VB (μm)")
    ax.set_title("(d) Physical wear anchor: VB_true grouped by predicted stage", loc="left", fontweight="bold")


def main():
    apply_style()
    lifecycle, simplex, q_agree, wear_agg = load()
    log_lines = []

    assert len(lifecycle) == 304 and len(simplex) == 304 and len(q_agree) == 304
    assert set(lifecycle["true_stage"].unique()) <= set(STAGE_ORDER)
    log_lines.append("PASS: lifecycle_semantics/simplex_trajectory/q_agreement each have 304 rows (C6 common-universe test set).")

    fig = plt.figure(figsize=(13.5, 15.5))
    gs = GridSpec(3, 2, height_ratios=[1.0, 1.15, 0.9], hspace=0.55, wspace=0.28, figure=fig)

    panel_lifecycle(fig, gs[0, :], lifecycle)

    ax_simplex = fig.add_subplot(gs[1, 0])
    panel_simplex(ax_simplex, simplex)

    ax_q = fig.add_subplot(gs[1, 1])
    panel_q_agreement(ax_q, q_agree, log_lines)

    ax_wear = fig.add_subplot(gs[2, :])
    panel_wear_violin(ax_wear, lifecycle, wear_agg, log_lines)

    fig.suptitle("DC-PSR ordered degradation semantics on PHM2010 D1/C6 (n=304): lifecycle probability,\n"
                 "probability-simplex trajectory, continuous degradation-position agreement, and physical wear anchor",
                 fontsize=10.8, y=0.995)
    fig.subplots_adjust(top=0.90, bottom=0.05)

    paths = save_all(fig, OUT_DIR, "fig4_main")
    log_lines.append(f"Saved outputs: {paths}")

    with open(os.path.join(LOG_DIR, "validation.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
    print("\n".join(log_lines))
    print("Fig.4 done.")


if __name__ == "__main__":
    main()
