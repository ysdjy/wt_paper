"""
Fig4-4 (消融实验 / probability-state formation) panel-first rendering.
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

ABLATION_IDS = st.ABLATION_IDS  # A1..A6
SUBSET = st.ABLATION_SUBSET     # A1, A4, A5, A6


def load_all():
    abs_df = pd.read_csv(os.path.join(DERIVED_DIR, "A1_A6_absolute.csv"), encoding="utf-8")
    traj_df = pd.read_csv(os.path.join(DERIVED_DIR, "trajectories_subset.csv"), encoding="utf-8")
    lv_df = pd.read_csv(os.path.join(DERIVED_DIR, "lifecycle_variation.csv"), encoding="utf-8")
    cv_df = pd.read_csv(os.path.join(DERIVED_DIR, "cumulative_variation.csv"), encoding="utf-8")
    f1_df = pd.read_csv(os.path.join(DERIVED_DIR, "stagewise_f1.csv"), encoding="utf-8")
    return abs_df, traj_df, lv_df, cv_df, f1_df


# ---------------------------------------------------------------------------
# (a) Hard-decision performance across A1-A6 (Acc, Macro-F1, M-Rec) -- natural y-axis, no
# exaggeration of the byte-identical A1-A4 region.
# ---------------------------------------------------------------------------
def panel_a(ax, abs_df):
    x = np.arange(6); w = 0.26
    st.add_highlight_for_last_group(ax, x_center=5, half_width=0.5)
    st.hatched_bar(ax, x - w, abs_df["Acc"].values, w, "#0072B2", st.HATCHES["h1"], label="Acc")
    st.hatched_bar(ax, x, abs_df["Macro-F1"].values, w, "#009E73", st.HATCHES["h2"], label="Macro-F1")
    st.hatched_bar(ax, x + w, abs_df["M-Rec"].values, w, "#D55E00", st.HATCHES["h3"], label="M-Rec")
    ax.set_xticks(x); ax.set_xticklabels(ABLATION_IDS, fontsize=7.4)
    # Natural range that still shows the real A5 dip -- not artificially zoomed to exaggerate it,
    # not compressed to hide it either. Bottom fixed a little below the true min.
    ymin = abs_df[["Acc", "Macro-F1", "M-Rec"]].values.min()
    ax.set_ylim(max(0, ymin - 0.06), 1.02)
    ax.set_ylabel("Score")
    st.style_axis(ax, add_arrows=True, show_x_arrow=False)

    # Secondary axis: Smooth (lower = better), restored per refinement request -- this is what
    # makes panel (a) alone show the full trade-off (A1-A4 flat classification / declining Smooth,
    # A5 = classification dip + best Smooth, A6 = classification recovery + still-good Smooth).
    ax2 = ax.twinx()
    smooth = abs_df["Smooth"].values
    ax2.plot(x, smooth, color="#222222", marker="o", linewidth=1.5, markersize=4.0,
             zorder=6, label="Smooth")
    for xi, yi in zip(x, smooth):
        ax2.annotate(f"{yi:.3f}", (xi, yi), fontsize=6.0, color="#222222",
                     xytext=(0, 6), textcoords="offset points", ha="center")
    ax2.set_ylim(0.0, smooth.max() * 1.35)
    ax2.set_ylabel("Smooth (↓ better)", labelpad=3)
    ax2.spines["top"].set_visible(False)
    ax2.spines["left"].set_visible(False)
    ax2.tick_params(axis="y", labelsize=6.8)

    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    # Legend moved INSIDE the plot (top empty area) instead of floating above the axes, per
    # explicit refinement request.
    ax.legend(h1 + h2, l1 + l2, loc="upper left", ncol=4, fontsize=6.0, bbox_to_anchor=(0.01, 0.995),
              handlelength=1.1, columnspacing=0.7, framealpha=0.88, facecolor="white", edgecolor="none")
    st.panel_caption_below(ax, "(a) Hard-decision performance & Smooth, A1→A6", y=-0.16)


# ---------------------------------------------------------------------------
# (b) State-wise recognition profile: E-F1/M-F1/L-F1 across A1-A6 -- replaces the sparse
# accuracy-smoothness scatter per refinement request. Complements panel (a) by showing WHICH
# stage drives the A5 dip / A6 recovery, rather than repeating the same Acc-vs-Smooth story.
# ---------------------------------------------------------------------------
def panel_b(ax, f1_df):
    x = np.arange(6)
    # E-F1/M-F1 sit only ~0.006 apart on A1-A4 -- same-direction labels collided during
    # panel-first review, so each series gets its own label offset direction/distance instead.
    series = [("E_F1", "E-F1", st.STAGE_COLORS["early"], "o", (0, -9), "top"),
              ("M_F1", "M-F1", st.STAGE_COLORS["middle"], "^", (0, 7), "bottom"),
              ("L_F1", "L-F1", st.STAGE_COLORS["late"], "s", (0, 7), "bottom")]
    for col, label, color, marker, off, va in series:
        y = f1_df[col].values
        ax.plot(x, y, color=color, marker=marker, markersize=5.0, linewidth=1.6, label=label, zorder=4)
        for xi, yi in zip(x, y):
            ax.annotate(f"{yi:.3f}", (xi, yi), fontsize=5.6, color=color,
                        xytext=off, textcoords="offset points", ha="center", va=va)
    ax.axvspan(3.5, 4.5, color=st.HIGHLIGHT, alpha=0.85, zorder=0)  # A5 highlighted (the dip)
    ax.set_xticks(x); ax.set_xticklabels(ABLATION_IDS, fontsize=7.4)
    ymin = f1_df[["E_F1", "M_F1", "L_F1"]].values.min()
    ax.set_ylim(max(0, ymin - 0.05), 1.03)
    ax.set_ylabel("Stage-wise F1")
    st.style_axis(ax, add_arrows=True)
    # Legend moved INSIDE the plot (top empty area), matching panel (a).
    ax.legend(loc="upper left", ncol=3, fontsize=6.0, bbox_to_anchor=(0.01, 0.995),
              handlelength=1.1, columnspacing=0.8, framealpha=0.88, facecolor="white", edgecolor="none")
    st.panel_caption_below(ax, "(b) State-wise recognition profile, A1→A6", y=-0.16)


# ---------------------------------------------------------------------------
# (c) Probability-state formation: A1, A4, A5, A6 small multiples, p_E/p_M/p_L over lifecycle
# ---------------------------------------------------------------------------
def _stage_background(ax, traj_sub):
    """Light background shading by TRUE stage along relative_tool_life, ported in spirit from
    代码/8.2图12.py::add_stage_background / add_true_stage_background."""
    life = traj_sub["relative_tool_life"].values
    stage = traj_sub["true_stage"].values
    start = 0
    cur = stage[0]
    for i in range(1, len(stage) + 1):
        if i == len(stage) or stage[i] != cur:
            ax.axvspan(life[start], life[i - 1] if i < len(stage) else life[-1],
                       color=st.STAGE_COLORS[cur], alpha=0.08, zorder=0, linewidth=0)
            if i < len(stage):
                start = i
                cur = stage[i]


def panel_c_config(ax, traj_df, aid, show_ylabel=True):
    sub = traj_df[traj_df["ID"] == aid].sort_values("relative_tool_life")
    _stage_background(ax, sub)
    x = sub["relative_tool_life"].values
    ax.plot(x, sub["p_E"].values, color=st.STAGE_COLORS["early"], linewidth=1.3, label="p_E")
    ax.plot(x, sub["p_M"].values, color=st.STAGE_COLORS["middle"], linewidth=1.3, label="p_M")
    ax.plot(x, sub["p_L"].values, color=st.STAGE_COLORS["late"], linewidth=1.3, label="p_L")
    ax.set_ylim(-0.03, 1.05)
    ax.set_xlim(0, 1)
    if show_ylabel:
        ax.set_ylabel("Stage probability")
    st.style_axis(ax, add_arrows=True, grid_axis="y")
    # No per-panel legend any more -- ONE shared legend for the whole (c) block is placed by
    # assemble.py, top-center, horizontal, per explicit refinement request.
    label = {"A1": "A1 (raw, instantaneous)", "A4": "A4 (mix, pre-ordering)",
             "A5": "A5 (strongest ordering)", "A6": "A6 (final balanced blend)"}[aid]
    # Sub-caption brought closer to its plot (was y=-0.30).
    st.panel_caption_below(ax, label, y=-0.13, fontsize=7.0)


def panel_c(axes, traj_df):
    for i, aid in enumerate(SUBSET):
        panel_c_config(axes[i], traj_df, aid, show_ylabel=(i == 0))


# ---------------------------------------------------------------------------
# (d) Probability-variation diagnostics: local + cumulative L1 variation, all A1-A6
# ---------------------------------------------------------------------------
def panel_d(axes, lv_df, cv_df):
    ax1, ax2 = axes
    # Line widths thinned to 3/4 of the previous values, per explicit refinement request.
    for i, aid in enumerate(ABLATION_IDS):
        color = st.ABLATION_COLORS[aid]
        sub = lv_df[lv_df["ID"] == aid].sort_values("relative_tool_life")
        ax1.plot(sub["relative_tool_life"], sub["local_variation_l1_smoothed"],
                 color=color, linewidth=1.125 if aid in ("A5", "A6") else 0.75,
                 alpha=1.0 if aid in ("A5", "A6", "A1") else 0.75, label=aid)
    for i, aid in enumerate(ABLATION_IDS):
        color = st.ABLATION_COLORS[aid]
        sub = cv_df[cv_df["ID"] == aid].sort_values("relative_tool_life")
        ax2.plot(sub["relative_tool_life"], sub["cumulative_variation_l1"],
                 color=color, linewidth=1.125 if aid in ("A5", "A6") else 0.75,
                 alpha=1.0 if aid in ("A5", "A6", "A1") else 0.75, label=aid)

    ax1.set_ylabel("Local variation (L1, smoothed)")
    ax1.set_xlabel("Relative tool life")
    st.style_axis(ax1, add_arrows=True)
    # No in-axes legend any more -- ONE shared legend for the whole (d) block (d1+d2) is placed by
    # assemble.py, top-center, per explicit refinement request.
    # Caption pulled further from the plot (was y=-0.26, collided with the x-axis label).
    st.panel_caption_below(ax1, "(d1) Local probability variation", y=-0.40)

    ax2.set_ylabel("Cumulative variation (L1)")
    ax2.set_xlabel("Relative tool life")
    st.style_axis(ax2, add_arrows=True)
    st.panel_caption_below(ax2, "(d2) Cumulative probability variation", y=-0.40)


# ---------------------------------------------------------------------------
# (e) Mechanism progression strip -- redesigned as a chevron/step-module band per refinement
# request (publication-grade, not plain circles). A1-A3 neutral/muted, A4 highlighted as the key
# fusion stage (taller module, bold outline), A5 visually distinct as the strongest-ordering stage
# (saturated accent + bold outline), A6 rendered as a rounded "final output" module rather than a
# chevron, to read visually as the pipeline's endpoint.
# ---------------------------------------------------------------------------
from matplotlib.patches import Polygon, FancyBboxPatch  # noqa: E402

STRIP_LABELS = {
    "A1": "Stage head\n(raw)", "A2": "+ fine-state\nhead", "A3": "+ q-prior",
    "A4": "+ weighted\nfusion", "A5": "+ ordered\nfilter", "A6": "Final\nblend",
}
STRIP_ROLE = {
    "A1": "input", "A2": "structure", "A3": "structure",
    "A4": "core fusion", "A5": "strongest ordering", "A6": "final output",
}


def _chevron(ax, x0, x1, y0, y1, tip, notch, color, edgecolor="white", lw=1.2, zorder=3, first=False):
    left = x0 if first else x0 + notch
    verts = [(x0, y0), (x1, y0), (x1 + tip, (y0 + y1) / 2), (x1, y1), (x0, y1), (left, (y0 + y1) / 2)]
    if first:
        verts = [(x0, y0), (x1, y0), (x1 + tip, (y0 + y1) / 2), (x1, y1), (x0, y1)]
    poly = Polygon(verts, closed=True, facecolor=color, edgecolor=edgecolor, linewidth=lw, zorder=zorder)
    ax.add_patch(poly)


def panel_e(ax):
    # x-extent: 6 modules x (step_w=0.92 + tip=0.16 + gap=0.03 + 0.02) starting at x=0.10, plus the
    # final module's own width -- verified by trace, not guessed, after panel-first review caught
    # A6's box being clipped by an xlim that was too tight.
    # y-extent tightened (was 0..1.05, leaving a large dead zone below the description labels down
    # to the old y=0 floor) -- refinement round, reclaim that whitespace instead of just pushing
    # the caption further away with a bigger negative offset.
    ax.set_xlim(0, 7.0); ax.set_ylim(0.06, 1.05)
    ax.axis("off")

    step_w = 0.92
    tip = 0.16
    notch = 0.16
    gap = 0.03
    # Modules flattened to 3/4 of their previous height, per explicit refinement request --
    # scaled around the same vertical center (0.64) so the whole strip doesn't shift position.
    # Vertical center lowered (was 0.64) so the modules sit closer to their own caption below and
    # farther from panel (d) above -- per explicit refinement request ("e图往下移，靠近e图标题").
    _center, _half = 0.48, (0.86 - 0.42) / 2 * 0.75
    y0, y1 = _center - _half, _center + _half  # base module vertical extent
    tall_extra = 0.055 * 0.75

    x = 0.10
    for i, aid in enumerate(ABLATION_IDS):
        color = st.ABLATION_COLORS[aid]
        emphasize_tall = aid in ("A4", "A5")
        yy0, yy1 = (y0 - tall_extra, y1 + tall_extra) if emphasize_tall else (y0, y1)
        edge_lw = 2.0 if aid in ("A4", "A5") else 1.0
        edgecolor = "#222222" if aid in ("A4", "A5") else "white"

        if aid == "A6":
            # Final module: rounded box, not a chevron -- reads as the pipeline's endpoint.
            box = FancyBboxPatch((x, y0 - tall_extra), step_w + tip, (y1 - y0) + 2 * tall_extra,
                                  boxstyle="round,pad=0.0,rounding_size=0.10",
                                  facecolor=color, edgecolor="#222222", linewidth=2.0, zorder=4)
            ax.add_patch(box)
            cx = x + (step_w + tip) / 2
        else:
            _chevron(ax, x, x + step_w, yy0, yy1, tip, notch, color,
                     edgecolor=edgecolor, lw=edge_lw, zorder=4, first=(i == 0))
            cx = x + step_w / 2 + (0 if i == 0 else notch / 2)

        ax.text(cx, (yy0 + yy1) / 2 if aid != "A6" else (y0 + y1) / 2, aid, ha="center", va="center",
                fontsize=8.0 if aid in ("A4", "A5", "A6") else 7.2, fontweight="bold",
                color="white" if aid != "A1" else "#333333", zorder=5)
        ax.text(cx, y0 - 0.10, STRIP_LABELS[aid], ha="center", va="top", fontsize=6.0,
                color=st.AXIS_COLOR, linespacing=1.25)
        # Role-label font enlarged (was 5.6), per explicit refinement request.
        ax.text(cx, y1 + 0.14, STRIP_ROLE[aid], ha="center", va="bottom", fontsize=7.0,
                fontstyle="italic", color="#8A8D8F" if aid not in ("A4", "A5", "A6") else color,
                fontweight="bold" if aid in ("A4", "A5", "A6") else "normal")
        x += step_w + tip + gap + 0.02

    # Caption offset shrunk from -0.62 to -0.30 now that ylim's dead zone below the description
    # labels is gone -- the axes bottom (data y=0.18) sits much closer to the labels already.
    st.panel_caption_below(ax, "(e) Ablation mechanism progression", y=-0.30, fontsize=7.4)


def render_previews():
    abs_df, traj_df, lv_df, cv_df, f1_df = load_all()

    fig, ax = plt.subplots(figsize=(3.6, 2.7)); panel_a(ax, abs_df)
    fig.savefig(os.path.join(PREVIEW_DIR, "panel_a_preview.png"), dpi=200, bbox_inches="tight"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(3.4, 2.7)); panel_b(ax, f1_df)
    fig.savefig(os.path.join(PREVIEW_DIR, "panel_b_preview.png"), dpi=200, bbox_inches="tight"); plt.close(fig)

    fig, axes = plt.subplots(1, 4, figsize=(8.6, 2.3), sharey=True)
    panel_c(axes, traj_df)
    fig.subplots_adjust(wspace=0.18, bottom=0.30, top=0.90)
    fig.savefig(os.path.join(PREVIEW_DIR, "panel_c_preview.png"), dpi=200, bbox_inches="tight"); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.6))
    panel_d(axes, lv_df, cv_df)
    fig.subplots_adjust(wspace=0.42, bottom=0.28, top=0.78)
    fig.savefig(os.path.join(PREVIEW_DIR, "panel_d_preview.png"), dpi=200, bbox_inches="tight"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.4, 1.85)); panel_e(ax)
    fig.savefig(os.path.join(PREVIEW_DIR, "panel_e_preview.png"), dpi=200, bbox_inches="tight"); plt.close(fig)

    print("Wrote panel previews to", PREVIEW_DIR)


if __name__ == "__main__":
    render_previews()
