"""
Fig4-2 (主比较) panel-first rendering: each panel(ax, ...) function draws into a given Axes and
is independently testable via render_previews() below, which saves one standalone PNG per panel
to outputs/panel_previews/ for visual review before assembly. Run this file directly to produce
all 5 previews; run assemble.py afterward for the final composite.
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "_shared"))
import data_utils as du  # noqa: E402
import style as st  # noqa: E402

HERE = os.path.dirname(__file__)
FIG_DIR = os.path.normpath(os.path.join(HERE, ".."))
DERIVED_DIR = os.path.join(FIG_DIR, "derived")
PREVIEW_DIR = os.path.join(FIG_DIR, "outputs", "panel_previews")
os.makedirs(PREVIEW_DIR, exist_ok=True)

st.apply_style()

# Row-1 (a)/(b)/(c) share one axes row (same GridSpec height/position), so their captions only
# align in figure-space if they use the SAME axes-fraction y offset -- previously a=-0.42 (deep,
# driven by panel (a)'s rotated 9-method x-tick labels), b=-0.24, c=-0.30, which visually
# misaligned the three caption baselines despite equal plot heights. Refinement round: one shared
# constant, all three panels reference it.
ROW1_CAPTION_Y = -0.40

METHOD_ID_MAP = {
    "RF": "rf", "TCN-GRU": "tcn_gru", "Multi-task TCN-GRU": "multitask_tcn_gru",
    "DC-PSR": "dc_psr", "HTT-Net (adapted)": "htt_net",
    "Multi-source Attention": "multi_source_attention", "MTF-AViTK": "mtf_avitk",
    "Dynamic GIN + TGP": "dynamic_gin_tgp", "DP2Net-adapted": "dp2net_adapted",
}


def load_all():
    main_df = pd.read_csv(os.path.join(DERIVED_DIR, "D1_heatmap_table.csv"), encoding="utf-8")
    ac_df = pd.read_csv(os.path.join(DERIVED_DIR, "accuracy_consistency_points.csv"), encoding="utf-8")
    ci_df = pd.read_csv(os.path.join(DERIVED_DIR, "B11_B12_controlled_comparison.csv"), encoding="utf-8")
    rep_df = pd.read_csv(os.path.join(DERIVED_DIR, "representative_recomputed.csv"), encoding="utf-8")
    paired_df = pd.read_csv(os.path.join(DERIVED_DIR, "B11_B12_paired_bootstrap_effects.csv"), encoding="utf-8")
    main_df["Method"] = pd.Categorical(main_df["Method"], st.METHOD_ORDER, ordered=True)
    main_df = main_df.sort_values("Method").reset_index(drop=True)
    return main_df, ac_df, ci_df, rep_df, paired_df


# ---------------------------------------------------------------------------
# (a) Overall method comparison: Acc / Macro-F1 / M-F1, grouped hatched bars, 9 methods
# ---------------------------------------------------------------------------
def panel_a(ax, main_df):
    x = np.arange(len(st.METHOD_ORDER))
    w = 0.26
    st.add_highlight_for_last_group(ax, x_center=x[-1], half_width=0.5)

    st.hatched_bar(ax, x - w, main_df["Acc"].values, w, "#0072B2", st.HATCHES["h1"], label="Acc")
    st.hatched_bar(ax, x, main_df["MacroF1"].values, w, "#009E73", st.HATCHES["h2"], label="Macro-F1")
    st.hatched_bar(ax, x + w, main_df["M_F1"].values, w, "#D55E00", st.HATCHES["h3"], label="M-F1")

    ax.set_xticks(x)
    ax.set_xticklabels(st.METHOD_ORDER, rotation=33, ha="right", fontsize=7.0, rotation_mode="anchor")
    ax.tick_params(axis="x", pad=1.5)
    ax.set_ylim(0.35, 1.05)
    ax.set_ylabel("Score")
    st.style_axis(ax, add_arrows=True)
    ax.legend(loc="lower left", ncol=3, bbox_to_anchor=(0.0, 1.0), fontsize=6.8,
              handlelength=1.4, columnspacing=0.9, handletextpad=0.4)
    st.panel_caption_below(ax, "(a) Overall classification\nperformance, 9 methods", y=ROW1_CAPTION_Y)


# ---------------------------------------------------------------------------
# (b) Accuracy vs Smooth trade-off scatter (raw axes, Smooth explicitly labeled lower=better)
# ---------------------------------------------------------------------------
def panel_b(ax, ac_df):
    # Only the scientifically-notable outlier (worst Smooth) gets an inline label at this scale --
    # panel (a) already lists every method name on its x-axis, so labeling all 9 points here would
    # only duplicate that and (at this panel's true physical width) collide (found during
    # panel-first visual review of the assembled composite, fixed here).
    # Plain gray markers for every other baseline, no inline text at all -- panel (a) already
    # names every method, and any inline label here (incl. the previous "Multi-source Attention"
    # one) risked crowding the y-axis/plot-area edge. Panel (b)'s only job is to make the
    # backbone->DC-PSR relation legible, per explicit refinement-round instruction.
    for _, r in ac_df.iterrows():
        m = r["Method"]
        if m in ("DC-PSR", "Multi-task TCN-GRU"):
            continue
        ax.scatter(r["Acc"], r["Smooth"], s=24, color="#B0B4B8", edgecolor="white",
                   linewidth=0.4, zorder=3)
    # Multi-task TCN-GRU and DC-PSR sit almost exactly on top of each other at this panel's data
    # scale (Acc differs by 0.0033, Smooth by 0.0048 -- well under a pixel once rendered at the
    # composite's true physical column width), so inline text labels for both collide no matter
    # how they are offset. The legend (marker shape + color) already identifies them unambiguously
    # -- dropped the redundant inline labels rather than fighting an unwinnable placement problem.
    # This is itself a real, disclosed finding: DC-PSR and its backbone are visually
    # indistinguishable in raw accuracy-consistency position at this scale; panel (c)'s CI strip
    # is what actually shows they are statistically close, which is the correct place for that claim.
    for m, marker, color in [("Multi-task TCN-GRU", "D", st.METHOD_COLORS["Multi-task TCN-GRU"]),
                              ("DC-PSR", "*", st.METHOD_COLORS["DC-PSR"])]:
        r = ac_df[ac_df["Method"] == m].iloc[0]
        ax.scatter(r["Acc"], r["Smooth"], s=110 if marker == "*" else 70, marker=marker,
                   color=color, edgecolor="white", linewidth=0.6, zorder=5, label=m)

    ax.set_xlabel("Accuracy (↑ better)")
    ax.set_ylabel("Smooth (↓ better)")
    ax.set_ylim(-0.015, ac_df["Smooth"].max() * 1.30)
    st.style_axis(ax, add_arrows=True)
    # Legend style unified with (a)/(c): horizontal row floating above the axes (was
    # "upper right" tucked inside the plot, inconsistent with its neighbors).
    ax.legend(loc="lower left", ncol=2, bbox_to_anchor=(0.0, 1.0), fontsize=6.5,
              handlelength=1.4, columnspacing=0.9, handletextpad=0.4)
    st.panel_caption_below(ax, "(b) Accuracy–consistency\ntrade-off", y=ROW1_CAPTION_Y)


# ---------------------------------------------------------------------------
# (c) DC-PSR vs backbone: paired effect. Two stacked areas sharing one panel:
#   ax_top -- paired moving-block-bootstrap forest plot, Delta (pp), positive = favors DC-PSR.
#   ax_bot -- Smooth reduction, a SEPARATE unit (relative %, point estimate only) -- deliberately
#             not sharing ax_top's pp x-axis (mixing pp and a relative-% metric on one numeric
#             scale would misrepresent both).
# Every number plotted here comes from derived/B11_B12_paired_bootstrap_effects.csv (paired
# moving-block bootstrap, load_data.py::paired_moving_block_bootstrap) -- never independently
# subtracted from two separately-bootstrapped CIs.
# ---------------------------------------------------------------------------
FOREST_METRIC_ORDER = ["Acc", "MacroF1", "M_F1", "M_Rec"]
FOREST_METRIC_LABELS = {"Acc": "Acc", "MacroF1": "Macro-F1", "M_F1": "M-F1", "M_Rec": "M-Rec"}
NEUTRAL_EFFECT_COLOR = "#5B7A96"  # muted blue-gray -- small pp gaps must not read as "alarming"


def panel_c(ax_top, ax_bot, main_df, paired_df):
    pd_idx = paired_df.set_index("metric")
    n_m = len(FOREST_METRIC_ORDER)
    y0 = np.arange(n_m)[::-1]
    effects = np.array([pd_idx.loc[m, "effect"] for m in FOREST_METRIC_ORDER])
    ci_lo = np.array([pd_idx.loc[m, "CI_low"] for m in FOREST_METRIC_ORDER])
    ci_hi = np.array([pd_idx.loc[m, "CI_high"] for m in FOREST_METRIC_ORDER])
    xerr_lo = effects - ci_lo
    xerr_hi = ci_hi - effects

    ax_top.axvline(0.0, color="#B9BEC3", linewidth=1.1, zorder=1)
    ax_top.errorbar(effects, y0, xerr=[xerr_lo, xerr_hi], fmt="o", color=NEUTRAL_EFFECT_COLOR,
                     ecolor=NEUTRAL_EFFECT_COLOR, elinewidth=1.8, capsize=3.2, capthick=1.6,
                     markersize=5.6, zorder=4)
    # Value labels sit ABOVE each dot (not inline with the whisker) so they never overlap the CI
    # line, the x=0 reference line, or the vertical gridlines.
    m_rec_i = FOREST_METRIC_ORDER.index("M_Rec")
    for i, (xi, yi) in enumerate(zip(effects, y0)):
        label = "identical" if i == m_rec_i else f"{xi:+.2f}"
        style = "italic" if i == m_rec_i else "normal"
        ax_top.text(xi, yi + 0.30, label, ha="center", va="bottom", fontsize=6.0,
                    color="#555555" if i == m_rec_i else "#333333", style=style)

    ax_top.set_yticks(y0)
    ax_top.set_yticklabels([FOREST_METRIC_LABELS[m] for m in FOREST_METRIC_ORDER], fontsize=7.2)
    ax_top.set_ylim(y0.min() - 0.55, y0.max() + 0.55)
    lo_pad = min(ci_lo.min(), effects.min()) - 0.55
    hi_pad = max(ci_hi.max(), effects.max()) + 0.85
    ax_top.set_xlim(lo_pad, hi_pad)
    ax_top.set_xlabel(r"$\Delta$ (pp), DC$-$PSR $-$ backbone   (favors DC-PSR $\rightarrow$)", fontsize=6.8)
    st.style_axis(ax_top, add_arrows=False, grid_axis="x")
    ax_top.spines["bottom"].set_visible(True)
    ax_top.spines["bottom"].set_color(st.AXIS_COLOR)
    ax_top.spines["bottom"].set_linewidth(0.9)
    ax_top.spines["left"].set_visible(True)
    ax_top.spines["left"].set_color(st.AXIS_COLOR)
    ax_top.spines["left"].set_linewidth(0.9)
    ax_top.tick_params(axis="x", labelsize=6.4)

    # --- Smooth: separate area, separate unit (relative % reduction, point estimate only) ---
    # No separate legend here -- panel (b) immediately to the left already establishes the
    # diamond=Multi-task TCN-GRU / star=DC-PSR convention in the same colors; this panel just
    # labels each point directly instead of repeating a legend.
    smooth_row = pd_idx.loc["Smooth"]
    b11_s, b12_s = smooth_row["B11_value"], smooth_row["B12_value"]
    rel_pct = smooth_row["effect"]
    ax_bot.set_xlim(0, b11_s * 1.30)
    ax_bot.set_ylim(-1.35, 1.35)
    ax_bot.plot([b12_s, b11_s], [0, 0], color="#B9BEC3", linewidth=2.4, zorder=2,
                solid_capstyle="round")
    ax_bot.scatter([b11_s], [0], marker="D", s=48, color=st.METHOD_COLORS["Multi-task TCN-GRU"],
                   edgecolor="white", linewidth=0.6, zorder=5)
    ax_bot.scatter([b12_s], [0], marker="*", s=95, color=st.METHOD_COLORS["DC-PSR"],
                   edgecolor="white", linewidth=0.6, zorder=5)
    # b11_s (diamond) and b12_s (star) are close together in x (~15% of the axis span), so
    # center-anchored labels above/below each point collide -- instead each label is anchored AT
    # its own point and grows OUTWARD, away from the other point.
    ax_bot.text(b11_s, -0.40, "Multi-task\nTCN-GRU", ha="left", va="top", fontsize=5.4,
               color=st.METHOD_COLORS["Multi-task TCN-GRU"])
    ax_bot.text(b12_s, -0.40, "DC-PSR", ha="right", va="top", fontsize=5.4,
               color=st.METHOD_COLORS["DC-PSR"])
    ax_bot.annotate(f"-{rel_pct:.1f}%", xy=((b11_s + b12_s) / 2, 0.40),
                    ha="center", va="bottom", fontsize=7.2, fontweight="bold", color=st.METHOD_COLORS["DC-PSR"])
    ax_bot.set_yticks([])
    for spine in ["top", "right", "left"]:
        ax_bot.spines[spine].set_visible(False)
    ax_bot.spines["bottom"].set_color(st.AXIS_COLOR)
    ax_bot.spines["bottom"].set_linewidth(0.9)
    ax_bot.tick_params(axis="y", left=False)
    ax_bot.tick_params(axis="x", labelsize=6.2, direction="in", length=3.0)
    ax_bot.set_xlabel("Smooth (↓ better)", fontsize=6.8, labelpad=1.5)


# ---------------------------------------------------------------------------
# (d) Confusion matrices, 4 representative methods
# ---------------------------------------------------------------------------
def panel_d_row(axes, rep_methods):
    labels = ["E", "M", "L"]
    im = None
    for ax, m in zip(axes, rep_methods):
        mid = METHOD_ID_MAP[m]
        counts = np.loadtxt(os.path.join(DERIVED_DIR, f"confusion_counts_{mid}.csv"), delimiter=",")
        row_norm = np.loadtxt(os.path.join(DERIVED_DIR, f"confusion_rownorm_{mid}.csv"), delimiter=",")
        im = ax.imshow(row_norm, cmap=st.CONFUSION_CMAP, vmin=0, vmax=1)
        for i in range(3):
            for j in range(3):
                val = row_norm[i, j]
                cnt = int(counts[i, j])
                color = "white" if val >= 0.55 else "#222222"
                ax.text(j, i, f"{val:.2f}\n({cnt})", ha="center", va="center",
                        fontsize=6.0, color=color)
        ax.set_xticks(range(3)); ax.set_xticklabels(labels, fontsize=6.8)
        ax.set_yticks(range(3)); ax.set_yticklabels(labels, fontsize=6.8)
        for spine in ax.spines.values():
            spine.set_color("#333333")
        st.panel_caption_below(ax, m, y=-0.30, fontsize=7.2, fontweight="normal")
    return im


# ---------------------------------------------------------------------------
# (e) Middle-stage & consistency diagnostics triptych (原 Fig.10 framework), 4 representative methods
# ---------------------------------------------------------------------------
def panel_e_recognition(ax, rep_df):
    methods = st.REPRESENTATIVE_METHODS
    sub = rep_df.set_index("Method").loc[methods].reset_index()
    x = np.arange(len(methods)); w = 0.26
    st.add_highlight_for_last_group(ax, x_center=x[-1], half_width=0.5)
    st.hatched_bar(ax, x - w, sub["M_Pre"].values, w, "#D55E00", st.HATCHES["h1"], label="M-Pre")
    st.hatched_bar(ax, x, sub["M_Rec"].values, w, "#0072B2", st.HATCHES["h2"], label="M-Rec")
    st.hatched_bar(ax, x + w, sub["M_F1"].values, w, "#009E73", st.HATCHES["h3"], label="M-F1")
    ax.set_xticks(x); ax.set_xticklabels(methods, rotation=20, ha="right", fontsize=6.6)
    ax.set_ylim(0, 1.18); ax.set_ylabel("Middle-stage score")
    st.style_axis(ax, add_arrows=True)
    # Legend tucked INSIDE the axes (upper area) rather than floating above it -- reduces the
    # vertical room this row needs and keeps all three e-panels' plot areas the same height.
    ax.legend(loc="upper center", ncol=3, fontsize=5.8, bbox_to_anchor=(0.5, 1.0),
              handlelength=1.0, columnspacing=0.6, handletextpad=0.35,
              framealpha=0.9, facecolor="white", edgecolor="none")
    st.panel_caption_below(ax, "(e1) Middle-stage\nrecognition", y=-0.46)


def panel_e_misclass(ax, rep_df):
    methods = st.REPRESENTATIVE_METHODS
    sub = rep_df.set_index("Method").loc[methods].reset_index()
    x = np.arange(len(methods)); w = 0.32
    st.add_highlight_for_last_group(ax, x_center=x[-1], half_width=0.5)
    st.hatched_bar(ax, x - w / 2, sub["M_to_E"].values, w, "#CC79A7", st.HATCHES["h1"], label="M→E")
    st.hatched_bar(ax, x + w / 2, sub["M_to_L"].values, w, "#E69F00", st.HATCHES["h2"], label="M→L")
    ax.set_xticks(x); ax.set_xticklabels(methods, rotation=20, ha="right", fontsize=6.6)
    ax.set_ylabel("Misclassification rate")
    ax.set_ylim(0, sub[["M_to_E", "M_to_L"]].values.max() * 1.35)
    st.style_axis(ax, add_arrows=True)
    ax.legend(loc="upper center", ncol=2, fontsize=5.8, bbox_to_anchor=(0.5, 1.0),
              handlelength=1.0, columnspacing=0.6, handletextpad=0.35,
              framealpha=0.9, facecolor="white", edgecolor="none")
    st.panel_caption_below(ax, "(e2) Middle-stage\nmisclassification direction", y=-0.46)


def panel_e_consistency(ax, main_df):
    methods = st.REPRESENTATIVE_METHODS
    sub = main_df.set_index("Method").loc[methods].reset_index()
    x = np.arange(len(methods)); w = 0.36
    st.add_highlight_for_last_group(ax, x_center=x[-1], half_width=0.5)
    st.hatched_bar(ax, x - w / 2, sub["Rev"].values, w, "#56B4E9", st.HATCHES["h1"], label="Rev")
    st.hatched_bar(ax, x + w / 2, sub["Jump"].values, w, "#8C564B", st.HATCHES["h2"], label="Jump")
    ax.set_xticks(x); ax.set_xticklabels(methods, rotation=20, ha="right", fontsize=6.6)
    ax.set_ylabel("Transition count")
    ax.set_ylim(0, max(1.0, sub[["Rev", "Jump"]].values.max() * 1.55))
    st.style_axis(ax, add_arrows=True, show_x_arrow=False)

    # Right (Smooth) axis visually lightened -- thinner spine, muted gray-blue instead of pure
    # black, smaller marker -- so it reads as a secondary reference line, not a competing axis.
    SMOOTH_COLOR = "#5B6670"
    ax2 = ax.twinx()
    ax2.plot(x, sub["Smooth"].values, color=SMOOTH_COLOR, marker="o", linewidth=1.1,
              markersize=3.0, label="Smooth")
    ax2.set_ylim(0, sub["Smooth"].values.max() * 1.42)  # headroom so the peak clears the legend
    ax2.set_ylabel("Smoothness (↓ better)", color=SMOOTH_COLOR, fontsize=7.6)
    ax2.spines["top"].set_visible(False)
    ax2.spines["left"].set_visible(False)
    ax2.spines["right"].set_color(SMOOTH_COLOR)
    ax2.spines["right"].set_linewidth(0.6)
    ax2.tick_params(axis="y", labelsize=6.4, colors=SMOOTH_COLOR, width=0.6)

    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper center", ncol=3, fontsize=5.8,
              bbox_to_anchor=(0.5, 1.0), handlelength=1.0, columnspacing=0.6, handletextpad=0.35,
              framealpha=0.9, facecolor="white", edgecolor="none")
    st.panel_caption_below(ax, "(e3) Transition stability\nand smoothness", y=-0.46)


def render_previews():
    main_df, ac_df, ci_df, rep_df, paired_df = load_all()

    fig, ax = plt.subplots(figsize=(3.4, 2.6)); panel_a(ax, main_df)
    fig.savefig(os.path.join(PREVIEW_DIR, "panel_a_preview.png"), dpi=200, bbox_inches="tight"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(3.0, 2.6)); panel_b(ax, ac_df)
    fig.savefig(os.path.join(PREVIEW_DIR, "panel_b_preview.png"), dpi=200, bbox_inches="tight"); plt.close(fig)

    fig = plt.figure(figsize=(3.2, 3.2))
    gs_c = fig.add_gridspec(2, 1, height_ratios=[0.66, 0.34], hspace=0.55, top=0.95, bottom=0.20)
    ax_top = fig.add_subplot(gs_c[0]); ax_bot = fig.add_subplot(gs_c[1])
    panel_c(ax_top, ax_bot, main_df, paired_df)
    fig.savefig(os.path.join(PREVIEW_DIR, "panel_c_preview.png"), dpi=200, bbox_inches="tight"); plt.close(fig)

    fig, axes = plt.subplots(1, 4, figsize=(7.0, 2.1))
    im = panel_d_row(axes, st.REPRESENTATIVE_METHODS)
    cax = fig.add_axes([0.93, 0.15, 0.012, 0.65])
    fig.colorbar(im, cax=cax).ax.tick_params(labelsize=6.5)
    fig.subplots_adjust(left=0.04, right=0.91, wspace=0.35, bottom=0.28)
    fig.savefig(os.path.join(PREVIEW_DIR, "panel_d_preview.png"), dpi=200, bbox_inches="tight"); plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.5))
    panel_e_recognition(axes[0], rep_df)
    panel_e_misclass(axes[1], rep_df)
    panel_e_consistency(axes[2], main_df)
    fig.subplots_adjust(wspace=0.62, bottom=0.34, top=0.82)
    fig.savefig(os.path.join(PREVIEW_DIR, "panel_e_preview.png"), dpi=200, bbox_inches="tight"); plt.close(fig)

    print("Wrote panel previews to", PREVIEW_DIR)


if __name__ == "__main__":
    render_previews()
