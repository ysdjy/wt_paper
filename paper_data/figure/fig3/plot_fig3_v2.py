"""
Fig.3 v2 (paper Fig. 4-4): A1-A6 ablation mechanism band -- reference-style visual reconstruction.

DATA AND STATISTICS ARE UNCHANGED FROM v1 (plot_fig3.py): this script imports v1's load(),
recompute_classwise(), and validate() directly rather than recomputing anything differently, so
the two scripts are guaranteed to plot identical numbers. Only the visualization layer changed.
See paper_data/figure/fig3/README.md's "v2" section for what changed and why, and
reference/SOURCE.md for exactly what was (and was not) learned from the style-reference mockups.

Two style references were used:
  - reference/reference_mockup.png (PRIMARY, MATLAB-rendered): dual-axis bar+line combo panels,
    bottom-centered captions, A5/A6 callout annotations, highlighted A5/A6 background band.
  - reference/reference_mockup_alt_original.png (secondary, earlier Python draft): the
    "mechanism evidence path" flow-chain idea (Raw->+Fine->+Prior->Mixture->Ordered->Final boxes)
    and the "Ablation Pareto trajectory" (A1->A6 connected by arrows in Acc-vs-Smooth space) --
    both are new panels in v2, built from v1's own `A1_A6_delta_vs_A1.csv` (loaded by v1's load()
    but never actually plotted there) and `A1_A6_absolute.csv`, not from the mockup's numbers.

A third, unsolicited mockup was found at fig3/视觉参考效果图/ during this build (a bright
"dashboard poster" style with a large top banner title, icon call-out boxes, and fictional
numbers). It directly conflicts with this round's explicit hard rules (no top title; muted
navy/teal/gold palette already proven on fig1_v2) and was NOT used as a layout template -- only
its "A1->A6 mechanism flow-chain with per-stage annotations" content idea overlaps with (and
reinforces) what reference_mockup_alt_original.png already suggested, which is what panel (d)
below actually draws from. See reference/SOURCE.md for the fuller note.

Run: python paper_data/figure/fig3/plot_fig3_v2.py
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_shared"))
from style_v2 import (apply_style, save_all, panel_letter, panel_caption, figure_caption,
                       ABLATION_IDS, ABLATION_COLORS, STAGE_COLORS)  # noqa: E402
import data_utils as du  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
from plot_fig3 import load, recompute_classwise, validate, CONFIG_LABEL  # noqa: E402

HERE = os.path.dirname(__file__)
OUT_DIR = os.path.join(HERE, "outputs")
LOG_DIR = os.path.join(HERE, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

MECHANISM_SHORT = {
    "A1": ("Raw", "Temperature-scaled\nraw stage head"),
    "A2": ("+Fine", "+ fine-state stage\nprobability"),
    "A3": ("+Prior", "+ q-hat degradation\nprior"),
    "A4": ("Mixture", "weighted fine/prior\nmixture"),
    "A5": ("Ordered", "causal ordered\nfilter on A4"),
    "A6": ("Final", "blend of A4 mix\n+ A5 ordered"),
}


def with_id(df):
    df = df.copy()
    df["ID"] = pd.Categorical(df["Configuration"].map(CONFIG_LABEL), categories=ABLATION_IDS, ordered=True)
    return df.sort_values("ID")


def panel_predictive_dualaxis(fig, ax, absolute):
    absolute = with_id(absolute)
    x = np.arange(len(ABLATION_IDS))
    width = 0.32
    ax.bar(x - width / 2, absolute["Acc"].values * 100, width=width, color=STAGE_COLORS["early"], label="Acc")
    ax.bar(x + width / 2, absolute["Macro-F1"].values * 100, width=width, color=STAGE_COLORS["middle"], label="Macro-F1")
    ax.set_ylim(97.0, 99.3)
    ax.set_ylabel("Score % (higher better)")
    ax.set_xticks(x); ax.set_xticklabels(ABLATION_IDS)
    for cid in ("A5", "A6"):
        i = ABLATION_IDS.index(cid)
        ax.axvspan(i - 0.5, i + 0.5, color=ABLATION_COLORS[cid], alpha=0.10, zorder=0)

    ax2 = ax.twinx()
    smooth_vals = absolute["Smooth"].values
    ax2.plot(x, smooth_vals, color=ABLATION_COLORS["A5"], marker="o", ms=5, lw=1.6, label="Smooth ↓")
    for xi, yi in zip(x, smooth_vals):
        ax2.annotate(f"{yi:.4f}", (xi, yi), textcoords="offset points", xytext=(0, 7), fontsize=6.0,
                     ha="center", color="#8A5A00")
    ax2.set_ylabel("Smooth (lower better)", color="#8A5A00")
    ax2.tick_params(axis="y", labelcolor="#8A5A00")
    ax2.grid(False)

    smooth_a1, smooth_a5, smooth_a6 = smooth_vals[0], smooth_vals[4], smooth_vals[5]
    ax.annotate(f"A5: strongest smoothing\n(-{(smooth_a1-smooth_a5)/smooth_a1*100:.1f}% vs A1),\nclassification dip",
                xy=(4, absolute["Acc"].values[4] * 100), xytext=(2.55, 97.15), fontsize=6.3, color="#7A2E2E")
    ax.annotate(f"A6: balanced\n(-{(smooth_a1-smooth_a6)/smooth_a1*100:.1f}% Smooth vs A1,\naccuracy restored)",
                xy=(5, absolute["Acc"].values[5] * 100), xytext=(4.5, 98.75), fontsize=6.3, color=ABLATION_COLORS["A6"])

    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc="lower left", fontsize=6.8, ncol=1)
    panel_letter(ax, "b")
    panel_caption(fig, ax, "Overall predictive performance across A1–A6")


def panel_statewise(fig, ax, classwise):
    x = np.arange(len(ABLATION_IDS))
    for stage, col, marker in [("E_F1", STAGE_COLORS["early"], "o"),
                                ("M_F1_recomputed", STAGE_COLORS["middle"], "s"),
                                ("L_F1", STAGE_COLORS["late"], "^")]:
        label = {"E_F1": "E-F1", "M_F1_recomputed": "M-F1", "L_F1": "L-F1"}[stage]
        ax.plot(x, classwise[stage].values * 100, marker=marker, ms=4.5, lw=1.5, color=col, label=label)
    for cid in ("A5",):
        i = ABLATION_IDS.index(cid)
        ax.axvspan(i - 0.5, i + 0.5, color=ABLATION_COLORS[cid], alpha=0.10, zorder=0)
    ax.set_xticks(x); ax.set_xticklabels(ABLATION_IDS)
    ax.set_ylabel("Class F1 % (higher better)")
    ax.legend(loc="lower left", ncol=3, fontsize=6.8)
    panel_letter(ax, "c")
    panel_caption(fig, ax, "State-wise recognition profile (E/M/L-F1)")


def panel_consistency_dualaxis(fig, ax, absolute):
    absolute = with_id(absolute)
    m_to_e_col = [c for c in absolute.columns if c.startswith("M") and "E" in c and "→" in c][0]
    x = np.arange(len(ABLATION_IDS))
    width = 0.32
    ax.bar(x - width / 2, absolute["M-Rec"].values * 100, width=width, color=STAGE_COLORS["middle"], label="M-Rec ↑")
    ax2 = ax.twinx()
    ax2.plot(x, absolute[m_to_e_col].values * 100, color="#B0555E", marker="D", ms=4.5, lw=1.5, label="M→E ↓")
    ax2.set_ylabel("M→E transition error % (lower better)", color="#B0555E", fontsize=8.2)
    ax2.tick_params(axis="y", labelcolor="#B0555E")
    ax2.grid(False)
    ax.set_ylim(94, 100)
    ax.set_ylabel("M-Rec % (higher better)")
    ax.set_xticks(x); ax.set_xticklabels(ABLATION_IDS)
    for cid in ("A5",):
        i = ABLATION_IDS.index(cid)
        ax.axvspan(i - 0.5, i + 0.5, color=ABLATION_COLORS[cid], alpha=0.10, zorder=0)
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc="lower center", fontsize=6.8, ncol=2)
    panel_letter(ax, "d")
    panel_caption(fig, ax, "Middle-stage recall & M→E transition error")


def panel_mechanism_chain(fig, ax, delta):
    delta = with_id(delta)
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 1)
    ax.axis("off")
    box_w, box_h = 0.85, 0.62
    centers = np.linspace(0.6, 5.4, 6)
    for i, (cid, cx) in enumerate(zip(ABLATION_IDS, centers)):
        row = delta[delta["ID"] == cid].iloc[0]
        short, sub = MECHANISM_SHORT[cid]
        color = ABLATION_COLORS[cid]
        edge = ABLATION_COLORS["A6"] if cid == "A6" else "#8A8D8F"
        lw = 2.0 if cid == "A6" else 0.9
        box = FancyBboxPatch((cx - box_w / 2, 0.30), box_w, box_h,
                              boxstyle="round,pad=0.02,rounding_size=0.03",
                              linewidth=lw, edgecolor=edge, facecolor=color, alpha=0.28, zorder=2)
        ax.add_patch(box)
        ax.text(cx, 0.30 + box_h - 0.08, cid, ha="center", va="top", fontsize=9.5, fontweight="bold")
        ax.text(cx, 0.30 + box_h - 0.24, short, ha="center", va="top", fontsize=7.6, style="italic")
        ax.text(cx, 0.30 + box_h - 0.40, sub, ha="center", va="top", fontsize=6.0, color="#444444")
        if cid == "A1":
            delta_txt = "reference"
        else:
            delta_txt = f"ΔAcc {row['delta_Acc']*100:+.2f}pp\nΔM-F1 {row['delta_M-F1']*100:+.2f}pp\nSmooth benefit {-row['delta_Smooth']*100:+.2f}%"
        ax.text(cx, 0.20, delta_txt, ha="center", va="top", fontsize=6.0, color="#2A2A2A")
        if i < 5:
            arrow = FancyArrowPatch((cx + box_w / 2 + 0.03, 0.30 + box_h / 2),
                                     (centers[i + 1] - box_w / 2 - 0.03, 0.30 + box_h / 2),
                                     arrowstyle="-|>", mutation_scale=10, color="#666666", lw=1.1, zorder=1)
            ax.add_patch(arrow)
    panel_letter(ax, "a")
    panel_caption(fig, ax, "Mechanism evidence path: A1→A6 module progression (Δ vs. A1, from A1_A6_delta_vs_A1.csv)")


def panel_pareto_trajectory(fig, ax, absolute):
    absolute = with_id(absolute)
    xs = absolute["Acc"].values * 100
    ys = absolute["Smooth"].values
    for i in range(len(ABLATION_IDS) - 1):
        ax.annotate("", xy=(xs[i + 1], ys[i + 1]), xytext=(xs[i], ys[i]),
                    arrowprops=dict(arrowstyle="-|>", color="#B7BDC2", lw=1.3, shrinkA=8, shrinkB=8))
    for cid, x, y in zip(ABLATION_IDS, xs, ys):
        ax.scatter(x, y, s=90 if cid in ("A1", "A5", "A6") else 55, color=ABLATION_COLORS[cid],
                   edgecolor="black", linewidth=0.8, zorder=3)
        dx, dy = 0.05, 0.0006
        va = "bottom"
        if cid == "A5":
            dx, dy = 0.05, -0.0011
            va = "top"
        elif cid == "A6":
            dx, dy = 0.06, -0.0002
            va = "top"
        elif cid == "A2":
            dy = 0.0016
        elif cid == "A4":
            dy = -0.0016
            va = "top"
        ax.annotate(cid, (x + dx, y + dy), fontsize=7.2, fontweight="bold", va=va, color=ABLATION_COLORS[cid])
    ax.set_xlabel("Accuracy % (higher better →)")
    ax.set_ylabel("Smooth (lower better ↑ = worse)")
    ax.invert_yaxis()
    panel_letter(ax, "e", loc="upper right")
    panel_caption(fig, ax, "Ablation Pareto trajectory, A1→A6 (arrows show module-progression order)")


def panel_lifecycle_variation(fig, ax_local, ax_cum, local_var, cum_var):
    for cid in ABLATION_IDS:
        sub = local_var[local_var["ID"] == cid].sort_values("relative_tool_life")
        ax_local.plot(sub["relative_tool_life"], sub["local_variation_l1_smoothed"],
                       color=ABLATION_COLORS[cid], lw=1.5 if cid in ("A1", "A5", "A6") else 1.1,
                       label=cid, alpha=1.0 if cid in ("A1", "A5", "A6") else 0.7)
        subc = cum_var[cum_var["ID"] == cid].sort_values("relative_tool_life")
        ax_cum.plot(subc["relative_tool_life"], subc["cumulative_variation_l1"],
                    color=ABLATION_COLORS[cid], lw=1.5 if cid in ("A1", "A5", "A6") else 1.1,
                    label=cid, alpha=1.0 if cid in ("A1", "A5", "A6") else 0.7)
    a6_terminal = cum_var[cum_var["ID"] == "A6"].sort_values("relative_tool_life")["cumulative_variation_l1"].iloc[-1]
    a1_terminal = cum_var[cum_var["ID"] == "A1"].sort_values("relative_tool_life")["cumulative_variation_l1"].iloc[-1]
    ax_cum.annotate(f"A6 terminal = {a6_terminal:.2f}\n(A1 = {a1_terminal:.2f})",
                     xy=(1.0, a6_terminal), xytext=(0.62, a6_terminal + (a1_terminal - a6_terminal) * 0.35),
                     fontsize=6.3, color=ABLATION_COLORS["A6"])
    ax_local.set_xlabel("Relative tool life")
    ax_local.set_ylabel("Local prob. variation\n(smoothed, L1)")
    ax_local.legend(loc="upper right", ncol=6, fontsize=6.2, columnspacing=0.7, handlelength=1.2)
    panel_letter(ax_local, "f")
    panel_caption(fig, ax_local, "Lifecycle local probability variation")

    ax_cum.set_xlabel("Relative tool life")
    ax_cum.set_ylabel("Cumulative prob.\nvariation (L1)")
    panel_letter(ax_cum, "g")
    panel_caption(fig, ax_cum, "Cumulative probability variation")


def main():
    apply_style()
    absolute, traj, local_var, cum_var, delta = load()
    classwise = recompute_classwise(traj)
    log_lines = []
    validate(absolute, classwise, log_lines)
    log_lines.append("v2: reused v1 load()/recompute_classwise()/validate() unchanged -- see fig3/logs/validation.txt "
                     "(v1) for the full numeric validation; this log only records v2-specific layout notes.")
    assert "ID" in local_var.columns and "ID" in cum_var.columns

    fig = plt.figure(figsize=(14.5, 18.5))
    gs = GridSpec(5, 2, height_ratios=[0.62, 1.0, 1.0, 1.0, 1.0], hspace=1.05, wspace=0.32,
                  figure=fig, left=0.075, right=0.96, top=0.985, bottom=0.09)

    ax_chain = fig.add_subplot(gs[0, :])
    panel_mechanism_chain(fig, ax_chain, delta)

    ax_pred = fig.add_subplot(gs[1, 0])
    panel_predictive_dualaxis(fig, ax_pred, absolute)
    ax_state = fig.add_subplot(gs[1, 1])
    panel_statewise(fig, ax_state, classwise)

    ax_cons = fig.add_subplot(gs[2, 0])
    panel_consistency_dualaxis(fig, ax_cons, absolute)
    ax_pareto = fig.add_subplot(gs[2, 1])
    panel_pareto_trajectory(fig, ax_pareto, absolute)

    ax_local = fig.add_subplot(gs[3:, 0])
    ax_cum = fig.add_subplot(gs[3:, 1])
    panel_lifecycle_variation(fig, ax_local, ax_cum, local_var, cum_var)

    figure_caption(fig, "消融实验",
                   subtitle="Fig. 4-4  A1→A6 module-progression mechanism: predictive performance, consistency, and lifecycle probability dynamics")

    paths = save_all(fig, OUT_DIR, "fig3_v2_reference_style")
    log_lines.append(f"Saved outputs: {paths}")
    with open(os.path.join(LOG_DIR, "validation_v2.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
    print("\n".join(log_lines))
    print("Fig.3 v2 done.")


if __name__ == "__main__":
    main()
