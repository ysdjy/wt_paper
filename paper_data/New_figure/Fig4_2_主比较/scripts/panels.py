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
    main_df["Method"] = pd.Categorical(main_df["Method"], st.METHOD_ORDER, ordered=True)
    main_df = main_df.sort_values("Method").reset_index(drop=True)
    return main_df, ac_df, ci_df, rep_df


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
# (c) Bootstrap 95% CI forest plot, representative methods, Acc / Macro-F1 / M-F1
# ---------------------------------------------------------------------------
def panel_c(ax, main_df):
    methods = st.REPRESENTATIVE_METHODS
    metrics = [("Acc", "#0072B2"), ("MacroF1", "#009E73"), ("M_F1", "#D55E00")]
    y0 = np.arange(len(methods))[::-1]
    offsets = [0.22, 0.0, -0.22]
    # Values plotted in percentage points (x100) -- same underlying CI data, display-only unit
    # change, per user refinement request.
    all_lo, all_hi = [], []
    for (metric, color), off in zip(metrics, offsets):
        sub = main_df[main_df["Method"].isin(methods)].copy()
        sub["Method"] = pd.Categorical(sub["Method"], methods, ordered=True)
        sub = sub.sort_values("Method")
        y = y0 + off
        val = sub[metric].values * 100
        lo = val - sub[f"{metric}_CI_low"].values * 100
        hi = sub[f"{metric}_CI_high"].values * 100 - val
        all_lo.append((sub[f"{metric}_CI_low"].values * 100).min())
        all_hi.append((sub[f"{metric}_CI_high"].values * 100).max())
        ax.errorbar(val, y, xerr=[lo, hi], fmt="o", color=color, ecolor=color,
                    elinewidth=1.8, capsize=3.0, capthick=1.6, markersize=5.4,
                    label={"Acc": "Acc", "MacroF1": "Macro-F1", "M_F1": "M-F1"}[metric])
    ax.set_yticks(y0)
    # "Multi-task TCN-GRU" wrapped to two lines -- the single longest label, was pushing this
    # panel's own left margin (and neighboring panel (b)'s space) wider than necessary.
    ytick_labels = [m.replace("Multi-task TCN-GRU", "Multi-task\nTCN-GRU") for m in methods]
    ax.set_yticklabels(ytick_labels, fontsize=7.0)
    ax.set_ylim(y0.min() - 0.55, y0.max() + 0.55)  # compress top/bottom margin, no empty rows
    # Shortened axis label -- the statistical meaning (moving-block bootstrap 95% CI) now lives in
    # the panel caption only, per explicit refinement-round instruction, not lost, just relocated.
    ax.set_xlabel("Score (%)")
    # Tighten to the actual data range (~91-100%) instead of the old 55-103% span, with a small
    # fixed margin -- found empirically to bracket every representative-method CI bound exactly.
    ax.set_xlim(min(all_lo) - 1.6, max(all_hi) + 1.2)
    st.style_axis(ax, add_arrows=True, grid_axis="x")
    ax.legend(loc="lower left", ncol=3, fontsize=6.5, bbox_to_anchor=(0.0, 1.0),
              handlelength=1.0, columnspacing=0.8)
    st.panel_caption_below(ax, "(c) Moving-block bootstrap 95% CIs", y=ROW1_CAPTION_Y)


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
    main_df, ac_df, ci_df, rep_df = load_all()

    fig, ax = plt.subplots(figsize=(3.4, 2.6)); panel_a(ax, main_df)
    fig.savefig(os.path.join(PREVIEW_DIR, "panel_a_preview.png"), dpi=200, bbox_inches="tight"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(3.0, 2.6)); panel_b(ax, ac_df)
    fig.savefig(os.path.join(PREVIEW_DIR, "panel_b_preview.png"), dpi=200, bbox_inches="tight"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(3.0, 2.6)); panel_c(ax, main_df)
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
