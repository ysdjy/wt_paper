"""
Fig.3 v4 (paper Fig. 4-4): A1-A6 ablation mechanism band -- publication-grade true-physical-size
refinement (178 x 130 mm master size).

DATA UNCHANGED FROM v1/v2/v3: imports v1's load(), recompute_classwise(), validate() directly.
Only the visualization layer changed again. See paper_data/figure/V4_DESIGN_AUDIT.md for the full
rationale and this figure's README "v4" section for what changed vs v3 and why.

Structural change this round (not just cosmetic): v3's panel (d) spent a full panel on Rev/Jump
bars that are real zeros for all 6 configs. v4 repurposes that panel to show the real lifecycle
local + cumulative probability-variation curves (already loaded by v1's load() but underused in
this combination), with Rev=Jump=0 reduced to a one-line annotation.

Run: python paper_data/figure/fig3/plot_fig3_v4.py
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_shared"))
from style_v4 import (apply_style, save_all, panel_container, master_figsize_in,
                       ABLATION_IDS, ABLATION_COLORS, STAGE_COLORS, LW_MAIN, LW_AUX)  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
from plot_fig3 import load, recompute_classwise, validate, CONFIG_LABEL  # noqa: E402

HERE = os.path.dirname(__file__)
OUT_DIR = os.path.join(HERE, "outputs")
LOG_DIR = os.path.join(HERE, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LABEL_TO_CONFIG = {v: k for k, v in CONFIG_LABEL.items()}


def _id_order(absolute):
    absolute = absolute.copy()
    absolute["_ID"] = absolute["Configuration"].map(CONFIG_LABEL)
    absolute["_ID"] = pd.Categorical(absolute["_ID"], categories=ABLATION_IDS, ordered=True)
    return absolute.sort_values("_ID").reset_index(drop=True)


def panel_a_predictive(fig, outer_cell, absolute):
    content_spec, _ = panel_container(
        fig, outer_cell, "(a) Predictive performance across A1→A6\n(Smooth shown as improvement vs A1, %)",
        hspace=0.85, caption_height=0.115, fontsize=8.4)
    ax = fig.add_subplot(content_spec)
    a = _id_order(absolute)
    x = np.arange(len(ABLATION_IDS))
    ax.axvspan(3.5, 4.5, color=ABLATION_COLORS["A5"], alpha=0.10, zorder=0)
    width = 0.24
    for i, (col, color) in enumerate([("Acc", "#2F6FB3"), ("Macro-F1", "#2E8B57"), ("M-F1", "#E76F51")]):
        ax.bar(x + (i - 1) * width, a[col] * 100, width=width, color=color, label=col)
    ax.set_ylabel("Score (%)")
    ax.set_ylim(96.8, 99.3)
    ax.set_xticks(x)
    ax.set_xticklabels(ABLATION_IDS, fontsize=7.6)

    a1_smooth = a.loc[a["_ID"] == "A1", "Smooth"].values[0]
    smooth_improve = (a1_smooth - a["Smooth"]) / a1_smooth * 100
    ax2 = ax.twinx()
    ax2.plot(x, smooth_improve, color="#175E5A", lw=LW_MAIN, marker="D", ms=4.2, zorder=6,
             label="Smooth improvement (%)")
    ax2.set_ylabel("Smooth improvement (%)", color="#175E5A", fontsize=7.4, labelpad=2)
    ax2.set_ylim(-5, 55)
    ax2.tick_params(axis="y", labelcolor="#175E5A", labelsize=6.7)
    ax2.grid(False)
    for xi, v, raw in zip(x, smooth_improve, a["Smooth"]):
        ax2.annotate(f"{raw:.4f}", (xi, v), textcoords="offset points", xytext=(0, 6),
                     ha="center", fontsize=6.5, color="#175E5A")

    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="lower center", bbox_to_anchor=(0.5, 1.01), fontsize=6.5,
              ncol=4, columnspacing=0.8, handlelength=1.3)
    return ax


def panel_b_statewise(fig, outer_cell, classwise):
    content_spec, _ = panel_container(fig, outer_cell, "(b) State-wise recognition profile\n(E/M/L-F1)",
                                       hspace=1.10, caption_height=0.115, fontsize=8.4)
    ax = fig.add_subplot(content_spec)
    x = np.arange(len(ABLATION_IDS))
    ax.axvspan(3.5, 4.5, color=ABLATION_COLORS["A5"], alpha=0.10, zorder=0)
    for col, color, marker, label in [("E_F1", STAGE_COLORS["early"], "o", "E-F1"),
                                       ("M_F1_recomputed", STAGE_COLORS["middle"], "^", "M-F1"),
                                       ("L_F1", STAGE_COLORS["late"], "s", "L-F1")]:
        ax.plot(x, classwise[col] * 100, color=color, lw=LW_MAIN, marker=marker, ms=4.5, label=label)
    ax.set_ylabel("Class F1 (%)")
    ax.set_xticks(x)
    ax.set_xticklabels(ABLATION_IDS, fontsize=7.6)
    ax.set_ylim(96.9, 101.7)
    ax.legend(loc="upper left", fontsize=6.5, ncol=3, columnspacing=0.7)
    ax.annotate("A5: strongest filtering,\nlargest dip", xy=(4, 97.1), xytext=(3.95, 101.1),
                ha="center", fontsize=6.5, color="#7A4A1A",
                arrowprops=dict(arrowstyle="-", color="#7A4A1A", lw=0.6, alpha=0.7))
    ax.annotate("A6: recovery", xy=(5, 98.4), xytext=(5.0, 100.7), ha="center",
                fontsize=6.5, color="#2E8B57",
                arrowprops=dict(arrowstyle="-", color="#2E8B57", lw=0.6, alpha=0.7))
    return ax


def panel_c_middle_transition(fig, outer_cell, absolute):
    content_spec, _ = panel_container(
        fig, outer_cell, "(c) Middle-stage recall & transition error: classification\nlargely unchanged A1–A4 despite shifting probability geometry",
        hspace=0.42, caption_height=0.13, fontsize=8.0)
    ax = fig.add_subplot(content_spec)
    a = _id_order(absolute)
    x = np.arange(len(ABLATION_IDS))
    ax.axvspan(3.5, 4.5, color=ABLATION_COLORS["A5"], alpha=0.10, zorder=0)
    width = 0.32
    ax.bar(x - width / 2, a["M-Rec"] * 100, width=width, color="#2F6FB3", label="M-Rec ↑")
    m_to_e_col = [c for c in a.columns if c.startswith("M") and "E" in c and ("→" in c or "to_E" in c)][0]
    m_to_l_col = [c for c in a.columns if c.startswith("M") and "L" in c and ("→" in c or "to_L" in c)][0]
    ax.set_ylabel("M-Rec (%)")
    ax.set_ylim(94, 100)
    ax.set_xticks(x)
    ax.set_xticklabels(ABLATION_IDS, fontsize=7.6)

    ax2 = ax.twinx()
    ax2.plot(x, a[m_to_e_col] * 100, color="#E76F51", lw=LW_AUX, marker="o", ms=3.6, label="M→E ↓")
    ax2.plot(x, a[m_to_l_col] * 100, color="#D39B23", lw=LW_AUX, marker="s", ms=3.6, label="M→L ↓")
    ax2.set_ylabel("Trans. error (%)", fontsize=7.4, labelpad=2)
    ax2.set_ylim(-1, 8)
    ax2.tick_params(axis="y", labelsize=6.7)
    ax2.grid(False)

    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=6.5, ncol=3, columnspacing=0.8)
    return ax


def panel_d_lifecycle(fig, outer_cell, local_var, cum_var, absolute):
    content_spec, _ = panel_container(
        fig, outer_cell, "(d) Lifecycle probability variation (local + cumulative);\nRev=Jump=0 for all A1–A6 (real)",
        hspace=1.35, caption_height=0.115, fontsize=8.2)
    grid = content_spec.subgridspec(1, 2, wspace=0.42)
    ax_local = fig.add_subplot(grid[0])
    ax_cum = fig.add_subplot(grid[1])

    for cid in ABLATION_IDS:
        sub = local_var[local_var["ID"] == cid].sort_values("relative_tool_life")
        ax_local.plot(sub["relative_tool_life"], sub["local_variation_l1_smoothed"],
                      color=ABLATION_COLORS[cid], lw=1.1, alpha=1.0 if cid in ("A1", "A5", "A6") else 0.7,
                      label=cid)
        subc = cum_var[cum_var["ID"] == cid].sort_values("relative_tool_life")
        ax_cum.plot(subc["relative_tool_life"], subc["cumulative_variation_l1"],
                    color=ABLATION_COLORS[cid], lw=1.1, alpha=1.0 if cid in ("A1", "A5", "A6") else 0.7)

    ax_local.set_xlabel("Relative tool life", fontsize=7.4, labelpad=1.5)
    ax_local.set_ylabel("Local variation (L1)", fontsize=7.4)
    # ncol=6 in one row was wider than ax_local's own box and overflowed into ax_cum's area
    # (matplotlib legends aren't clipped to their axes) -- 3x2 keeps the legend within ax_local.
    ax_local.legend(loc="upper right", fontsize=6.5, ncol=3, columnspacing=0.5, handlelength=0.9,
                     labelspacing=0.25)
    ax_cum.set_xlabel("Relative tool life", fontsize=7.4, labelpad=1.5)
    ax_cum.set_ylabel("Cumulative variation (L1)", fontsize=7.4)
    return ax_local, ax_cum


def panel_mechanism_band(fig, outer_cell, absolute, delta):
    content_spec, _ = panel_container(
        fig, outer_cell, "(e) A1→A6 mechanism progression: module changes and real Δ vs A1",
        hspace=0.55, caption_height=0.16, fontsize=8.4)
    ax = fig.add_subplot(content_spec)
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 1)
    ax.axis("off")

    short_desc = {
        "A1": "Temperature-scaled\nraw stage head",
        "A2": "+ fine-state\nstage probability",
        "A3": "+ q-hat degradation\nposition prior",
        "A4": "weighted fine/prior\nmixture",
        "A5": "causal ordered\nfilter",
        "A6": "final blend\n(A4 + A5)",
    }
    a = _id_order(absolute)
    d = delta.copy()
    d["_ID"] = d["Configuration"].map(CONFIG_LABEL)

    box_w, gap = 0.86, 0.14
    for i, cid in enumerate(ABLATION_IDS):
        x0 = i * (box_w + gap) + 0.06
        color = ABLATION_COLORS[cid]
        face = color if cid in ("A5", "A6") else "#F2F2F2"
        edge = color
        alpha_face = 0.55 if cid in ("A5", "A6") else 1.0
        box = FancyBboxPatch((x0, 0.42), box_w, 0.42, boxstyle="round,pad=0.02,rounding_size=0.03",
                              linewidth=1.1, edgecolor=edge, facecolor=face, alpha=1.0, zorder=3)
        ax.add_patch(box)
        ax.text(x0 + box_w / 2, 0.75, cid, ha="center", va="center", fontsize=8.0, fontweight="bold", zorder=4)
        ax.text(x0 + box_w / 2, 0.56, short_desc[cid], ha="center", va="center", fontsize=6.5, zorder=4)

        drow = d[d["_ID"] == cid].iloc[0]
        smooth_imp = -drow["delta_Smooth"] / a.loc[a["_ID"] == "A1", "Smooth"].values[0] * 100
        if cid == "A1":
            delta_txt = "reference"
        else:
            delta_txt = f"ΔAcc {drow['delta_Acc']*100:+.2f}pp\nSmooth {smooth_imp:+.1f}% vs A1"
        ax.text(x0 + box_w / 2, 0.22, delta_txt, ha="center", va="center", fontsize=6.5, color="#333333")

        if i < len(ABLATION_IDS) - 1:
            arrow = FancyArrowPatch((x0 + box_w + 0.01, 0.63), (x0 + box_w + gap - 0.01, 0.63),
                                     arrowstyle="-|>", mutation_scale=8, linewidth=1.0, color="#555555", zorder=2)
            ax.add_patch(arrow)
    return ax


def main():
    apply_style()
    absolute, traj, local_var, cum_var, delta = load()
    log_lines = []
    assert len(traj) == 1824 and len(local_var) == 1824 and len(cum_var) == 1824
    classwise = recompute_classwise(traj)
    validate(absolute, classwise, log_lines)

    a = _id_order(absolute)
    a1_4 = a[a["_ID"].isin(["A1", "A2", "A3", "A4"])]
    assert a1_4["Acc"].nunique() == 1 and a1_4["Macro-F1"].nunique() == 1, "A1-A4 must be identical"
    log_lines.append("v4: confirmed A1-A4 Acc/Macro-F1 byte-identical (rendered flat, not exaggerated).")
    log_lines.append("v4: panel (d) restructured to show real lifecycle local+cumulative variation "
                     "(A1_A6_lifecycle_variation.csv / A1_A6_cumulative_variation.csv), replacing v3's "
                     "near-all-zero Rev/Jump panel; Rev=Jump=0 kept as a one-line annotation.")

    fig = plt.figure(figsize=master_figsize_in("fig3"))
    outer = GridSpec(2, 1, height_ratios=[0.78, 0.22], hspace=0.34, figure=fig,
                      left=0.055, right=0.985, top=0.985, bottom=0.05)
    top2x2 = outer[0].subgridspec(2, 2, wspace=0.50, hspace=0.80)

    panel_a_predictive(fig, top2x2[0, 0], absolute)
    panel_b_statewise(fig, top2x2[0, 1], classwise)
    panel_c_middle_transition(fig, top2x2[1, 0], absolute)
    panel_d_lifecycle(fig, top2x2[1, 1], local_var, cum_var, absolute)
    panel_mechanism_band(fig, outer[1], absolute, delta)

    paths = save_all(fig, OUT_DIR, "fig3_v4")
    log_lines.append(f"Saved outputs: {paths}")
    with open(os.path.join(LOG_DIR, "validation_v4.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
    print("\n".join(log_lines))
    print("Fig.3 v4 done.")


if __name__ == "__main__":
    main()
