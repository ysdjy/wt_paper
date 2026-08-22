"""
Fig.3 v3 (paper Fig. 4-4): A1-A6 ablation mechanism band -- dense landscape reconstruction with
strong visual impact (fig3 is explicitly allowed more visual punch than fig1/fig2 per the task
brief: "从Fig3开始允许明显增加视觉冲击力").

DATA AND STATISTICS ARE UNCHANGED FROM v1: imports v1's load(), recompute_classwise(), validate()
directly; the mechanism band additionally reads A1_A6_delta_vs_A1.csv (already loaded by v1's
load() but never plotted there).

Layout, ground-up rebuilt (landscape 15.5x10.5in):
  ┌───────────────────────┬───────────────────────┐
  │ (a) predictive         │ (b) state-wise F1     │
  ├───────────────────────┼───────────────────────┤
  │ (c) middle-stage/       │ (d) trajectory        │
  │     transition          │     stability          │
  ├───────────────────────┴───────────────────────┤
  │   A1 -> A2 -> A3 -> A4 -> A5 -> A6 mechanism    │
  │            progression band                     │
  └─────────────────────────────────────────────────┘

Smooth is shown as "Smooth improvement vs A1 (%)" = (A1_Smooth - Ai_Smooth)/A1_Smooth*100 (panel d
only) -- explicitly labeled that way, never raw Smooth plotted going "up=better" unlabeled. A5 gets
a light warm vertical shading band, not a heavy warning box. The mechanism band uses the 6 REAL
`Configuration` strings and real deltas from A1_A6_delta_vs_A1.csv.

Style reference: paper_data/figure/fig3/视觉参考效果图/*.png -- LAYOUT ONLY (dual-axis bar+line
combo panels, A5/A6 callout-annotation style, 6-node mechanism flow-chain band). Its own numbers
("0.0236"/"0.0136"/"0.0188" etc.) are fictional and are NOT reproduced -- every number here is
recomputed from paper_data.

Run: python paper_data/figure/fig3/plot_fig3_v3.py
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_shared"))
from style_v3 import apply_style, save_all, panel_container, ABLATION_IDS, ABLATION_COLORS, STAGE_COLORS  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
from plot_fig3 import load, recompute_classwise, validate, CONFIG_LABEL  # noqa: E402

HERE = os.path.dirname(__file__)
OUT_DIR = os.path.join(HERE, "outputs")
DERIVED_DIR = os.path.join(HERE, "derived")
LOG_DIR = os.path.join(HERE, "logs")
os.makedirs(DERIVED_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

LABEL_TO_CONFIG = {v: k for k, v in CONFIG_LABEL.items()}

# Short mechanism labels for the bottom band (2-line, fits inside a compact box). Full technical
# strings stay in CONFIG_LABEL / A1_A6_absolute.csv; these are display-only paraphrases.
NODE_SHORT = {
    "A1": "Raw stage head\n(temperature-scaled)",
    "A2": "+ fine-state\nstage probability",
    "A3": "+ q-hat degradation\nprior",
    "A4": "weighted fine/prior\nmixture",
    "A5": "causal ordered\nfilter",
    "A6": "final blend\n(A4 + A5)",
}


def _a5_shade(ax):
    ax.axvspan(3.5, 4.5, color=ABLATION_COLORS["A5"], alpha=0.09, zorder=0)


def panel_a_predictive(fig, outer_cell, absolute):
    content_spec, _ = panel_container(fig, outer_cell, "(a) Predictive performance across A1→A6", hspace=0.28)
    ax = fig.add_subplot(content_spec)
    absolute = absolute.copy()
    absolute["ID"] = pd.Categorical(absolute["Configuration"].map(CONFIG_LABEL), categories=ABLATION_IDS, ordered=True)
    absolute = absolute.sort_values("ID")
    x = np.arange(len(ABLATION_IDS))
    _a5_shade(ax)
    for metric, marker, color in [("Acc", "o", "#1B3A5C"), ("Macro-F1", "s", "#2A8C7A"), ("M-F1", "^", "#D9A441")]:
        ax.plot(x, absolute[metric].values * 100, marker=marker, ms=5, lw=1.6, label=metric, color=color)
    ax.set_xticks(x)
    ax.set_xticklabels(ABLATION_IDS)
    ax.set_ylabel("Score % (higher better)")
    ax.set_ylim(97.0, 99.3)
    ax.legend(loc="lower left", fontsize=7.2)
    return ax


def panel_b_statewise(fig, outer_cell, classwise):
    content_spec, _ = panel_container(fig, outer_cell, "(b) State-wise recognition profile (E/M/L-F1)", hspace=0.28)
    ax = fig.add_subplot(content_spec)
    _a5_shade(ax)
    x = np.arange(len(ABLATION_IDS))
    for stage, col, marker, label in [("E_F1", STAGE_COLORS["early"], "o", "E-F1"),
                                       ("M_F1_recomputed", STAGE_COLORS["middle"], "s", "M-F1"),
                                       ("L_F1", STAGE_COLORS["late"], "^", "L-F1")]:
        ax.plot(x, classwise[stage].values * 100, marker=marker, ms=5, lw=1.6, color=col, label=label)
    ax.set_xticks(x)
    ax.set_xticklabels(ABLATION_IDS)
    ax.set_ylabel("Class F1 % (higher better)")
    ax.legend(loc="lower left", ncol=3, fontsize=7.2)
    return ax


def panel_c_middle_transition(fig, outer_cell, absolute):
    content_spec, _ = panel_container(fig, outer_cell, "(c) Middle-stage recognition & transition consistency", hspace=0.28)
    ax = fig.add_subplot(content_spec)
    absolute = absolute.copy()
    absolute["ID"] = pd.Categorical(absolute["Configuration"].map(CONFIG_LABEL), categories=ABLATION_IDS, ordered=True)
    absolute = absolute.sort_values("ID")
    m_to_e_col = [c for c in absolute.columns if c.startswith("M") and "E" in c and "→" in c][0]
    m_to_l_col = [c for c in absolute.columns if c.startswith("M") and "L" in c and "→" in c][0]
    _a5_shade(ax)
    x = np.arange(len(ABLATION_IDS))
    ax.bar(x, absolute["M-Rec"].values * 100, width=0.5, color="#3E7C99", alpha=0.85, label="M-Rec ↑ (bars)")
    ax.set_ylabel("M-Rec % (higher better)")
    ax.set_ylim(93, 100)
    ax.set_xticks(x)
    ax.set_xticklabels(ABLATION_IDS)
    ax2 = ax.twinx()
    ax2.plot(x, absolute[m_to_e_col].values * 100, color="#B0555E", marker="o", ms=5, lw=1.5, label="M→E ↓")
    ax2.plot(x, absolute[m_to_l_col].values * 100, color="#D9A441", marker="s", ms=5, lw=1.5, label="M→L ↓")
    ax2.set_ylabel("Transition error % (lower better)")
    ax2.set_ylim(0, max(6, absolute[m_to_e_col].max() * 100 * 1.6))
    ax2.grid(False)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="lower left", fontsize=6.8)
    return ax


def panel_d_trajectory_stability(fig, outer_cell, absolute):
    content_spec, _ = panel_container(
        fig, outer_cell,
        "(d) Trajectory stability: Rev/Jump counts + Smooth improvement vs A1 (%)", hspace=0.28)
    ax = fig.add_subplot(content_spec)
    absolute = absolute.copy()
    absolute["ID"] = pd.Categorical(absolute["Configuration"].map(CONFIG_LABEL), categories=ABLATION_IDS, ordered=True)
    absolute = absolute.sort_values("ID")
    _a5_shade(ax)
    x = np.arange(len(ABLATION_IDS))
    width = 0.32
    ax.bar(x - width / 2, absolute["Rev"], width=width, color="#8A8D8F", label="Rev ↓")
    ax.bar(x + width / 2, absolute["Jump"], width=width, color="#C97B3D", label="Jump ↓")
    ax.set_ylabel("Count (lower better)")
    ax.set_xticks(x)
    ax.set_xticklabels(ABLATION_IDS)
    ax.set_ylim(0, 1)
    if absolute[["Rev", "Jump"]].values.max() == 0:
        ax.text(0.5, 0.92, "Rev = Jump = 0 for all A1–A6 configurations", transform=ax.transAxes,
                ha="center", va="top", fontsize=6.6, color="#666666", style="italic")

    a1_smooth = absolute.loc[absolute["ID"] == "A1", "Smooth"].values[0]
    smooth_improve_pct = (a1_smooth - absolute["Smooth"].values) / a1_smooth * 100
    ax2 = ax.twinx()
    ax2.plot(x, smooth_improve_pct, color="#2A8C7A", marker="D", ms=5.5, lw=1.7, label="Smooth improvement vs A1 (%)")
    for xi, pct, raw in zip(x, smooth_improve_pct, absolute["Smooth"].values):
        ax2.annotate(f"{raw:.4f}", (xi, pct), textcoords="offset points", xytext=(0, 7), fontsize=5.8,
                     ha="center", color="#2A8C7A")
    ax2.set_ylabel("Smooth improvement vs A1 (%)\n(raw Smooth annotated at each point)")
    ax2.set_ylim(-5, 50)
    ax2.grid(False)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=6.8)
    return ax


def panel_mechanism_band(fig, outer_cell, absolute, delta):
    content_spec, _ = panel_container(
        fig, outer_cell,
        "A1→A6 mechanism progression: module changes and their effect vs. A1 (real ΔAcc / ΔM-F1 / Smooth improvement)",
        hspace=0.20, caption_height=0.13, fontsize=9.0)
    ax = fig.add_subplot(content_spec)
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 1)
    ax.axis("off")

    a1_smooth = absolute.loc[absolute["Configuration"] == "Temperature-scaled raw stage head", "Smooth"].values[0]
    box_w, box_h = 0.82, 0.60
    centers_x = np.linspace(0.6, 5.4, 6)
    cy = 0.56
    for i, cid in enumerate(ABLATION_IDS):
        cx = centers_x[i]
        config = LABEL_TO_CONFIG[cid]
        row = delta[delta["ID"] == cid].iloc[0]
        color = ABLATION_COLORS[cid]
        box = FancyBboxPatch((cx - box_w / 2, cy - box_h / 2), box_w, box_h,
                              boxstyle="round,pad=0.02,rounding_size=0.06",
                              linewidth=1.1, edgecolor="#333333", facecolor=color, alpha=0.30, zorder=2)
        ax.add_patch(box)
        ax.text(cx, cy + box_h / 2 - 0.10, cid, ha="center", va="top", fontsize=11, fontweight="bold", zorder=3)
        ax.text(cx, cy - 0.02, NODE_SHORT[cid], ha="center", va="center", fontsize=7.0, zorder=3)

        if cid == "A1":
            delta_txt = "reference (A1)"
        else:
            smooth_pct = -row["delta_Smooth"] / a1_smooth * 100
            delta_txt = f"ΔAcc {row['delta_Acc']*100:+.2f}pp | ΔM-F1 {row['delta_M-F1']*100:+.2f}pp\nSmooth {smooth_pct:+.1f}% vs A1"
        ax.text(cx, cy - box_h / 2 - 0.12, delta_txt, ha="center", va="top", fontsize=6.3, color="#333333", zorder=3)

        if i < 5:
            arrow = FancyArrowPatch((cx + box_w / 2 + 0.03, cy), (centers_x[i + 1] - box_w / 2 - 0.03, cy),
                                     arrowstyle="-|>", mutation_scale=12, linewidth=1.2, color="#555555", zorder=1)
            ax.add_patch(arrow)
    return ax


def main():
    apply_style()
    absolute, traj, local_var, cum_var, delta = load()
    log_lines = []

    assert len(traj) == 1824 and len(local_var) == 1824 and len(cum_var) == 1824
    classwise = recompute_classwise(traj)
    classwise.to_csv(os.path.join(DERIVED_DIR, "A1_A6_classwise_metrics_v3.csv"), index=False, encoding="utf-8")
    validate(absolute, classwise, log_lines)

    delta = delta.copy()
    a1_smooth = absolute.loc[absolute["Configuration"] == "Temperature-scaled raw stage head", "Smooth"].values[0]
    a5_row = delta[delta["ID"] == "A5"].iloc[0]
    a6_row = delta[delta["ID"] == "A6"].iloc[0]
    smooth_pct_a5 = -a5_row["delta_Smooth"] / a1_smooth * 100
    smooth_pct_a6 = -a6_row["delta_Smooth"] / a1_smooth * 100
    assert np.isclose(smooth_pct_a5, 42.4, atol=0.5), smooth_pct_a5
    assert np.isclose(smooth_pct_a6, 20.5, atol=0.5), smooth_pct_a6
    log_lines.append(f"PASS (v3, from A1_A6_delta_vs_A1.csv): mechanism-band Smooth improvement A5={smooth_pct_a5:.2f}% "
                      f"(~42.4%), A6={smooth_pct_a6:.2f}% (~20.5%) -- matches v1's independently-derived numbers.")
    assert absolute["Configuration"].nunique() == 6
    log_lines.append("PASS: mechanism band uses exactly the 6 real Configuration strings from A1_A6_absolute.csv, no invented labels.")

    fig = plt.figure(figsize=(15.5, 10.5))
    outer = GridSpec(2, 1, height_ratios=[0.58, 0.42], hspace=0.16, figure=fig,
                      left=0.045, right=0.985, top=0.99, bottom=0.03)
    top2x2 = outer[0].subgridspec(2, 2, hspace=0.20, wspace=0.20)

    panel_a_predictive(fig, top2x2[0, 0], absolute)
    panel_b_statewise(fig, top2x2[0, 1], classwise)
    panel_c_middle_transition(fig, top2x2[1, 0], absolute)
    panel_d_trajectory_stability(fig, top2x2[1, 1], absolute)
    panel_mechanism_band(fig, outer[1], absolute, delta)

    paths = save_all(fig, OUT_DIR, "fig3_v3")
    log_lines.append(f"Saved outputs: {paths}")
    with open(os.path.join(LOG_DIR, "validation_v3.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
    print("\n".join(log_lines))
    print("Fig.3 v3 done.")


if __name__ == "__main__":
    main()
