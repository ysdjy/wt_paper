"""
Shared manuscript-native plotting style for paper_data/New_figure/Fig4_2..Fig4_5.

Design principle (per the round-2 task brief): the ORIGINAL manuscript's own plotting code
(代码/8.2图8~18.py) is the primary visual-style source this round, not the earlier
paper_data/figure/ v2-v5 AI-driven "dense-landscape" style. This module ports, verbatim where
possible, the exact reusable style functions found there:

- add_axis_arrows() / style_axis(): 代码/8.2图10.py -- open "arrow-tipped" axes, dashed
  y-gridlines only, in-facing ticks. This is the single most consistent signature across
  8.2图8/9/10/11/12/13/14.py and is adopted as this project's shared axis convention.
- add_highlight_for_last_group(): 代码/8.2图10.py -- shades the proposed-method's column/group.
- Hatched white-fill bars (facecolor="white", hatch="////"/"\\\\\\\\"/"....", colored edge):
  代码/8.2图10.py's bar convention, used instead of solid-fill bars throughout.

New in this module (not from 代码/, needed for this round's own explicit requirement):
- panel_caption_below(): every panel's "(a) description" caption sits BELOW the panel, centered
  (this project's global rule this round -- the original 代码/ scripts put titles ABOVE, which is
  deliberately overridden here; the plotting logic/visual body of each panel is otherwise kept
  faithful to 代码/).

Stage colors (Early/Middle/Late) are the exact hex values from 代码/8.2图17.py / 代码/8.2图18.py
(muted green / warm orange / muted red), per this round's explicit instruction to keep this
palette consistent across Fig4-4 and Fig4-5 rather than inventing a new "AI tech-blue" scheme.
"""
import os
import matplotlib as mpl
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Global rcParams -- Times New Roman + STIX mathtext, confirmed (not invented) as the
# manuscript's own convention by reading 代码/1.3.1可视化.py, 代码/7.3主实验.py, and every
# 代码/8.2图*.py script.
# ---------------------------------------------------------------------------
def apply_style():
    mpl.rcParams.update({
        "font.family": "Times New Roman",
        "mathtext.fontset": "stix",
        "axes.unicode_minus": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "font.size": 8.5,
        "axes.titlesize": 9.5,
        "axes.labelsize": 8.7,
        "xtick.labelsize": 7.6,
        "ytick.labelsize": 7.6,
        "legend.fontsize": 7.5,
        "legend.frameon": False,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "figure.dpi": 130,
    })


# ---------------------------------------------------------------------------
# Stage colors -- exact hex from 代码/8.2图17.py / 8.2图18.py, per explicit user instruction
# to keep this palette (not the previous round's #2F6FB3/#2E8B57/#E76F51 set).
# ---------------------------------------------------------------------------
STAGE_COLORS = {
    "early": "#1B9E77",   # deep teal green
    "middle": "#E6A01A",  # warm golden orange
    "late": "#C44E52",    # muted crimson red
}
STAGE_ORDER = ["early", "middle", "late"]
STAGE_LABELS = {"early": "Early", "middle": "Middle", "late": "Late"}
STAGE_MARKERS = {"early": "o", "middle": "^", "late": "s"}
CONDITION_MARKERS = {"C1": "o", "C4": "^", "C6": "s"}  # 代码/8.2图18.py convention

# q / uncertainty continuous colormaps -- ported from 代码/8.2图18.py (Q_CMAP / U_CMAP)
Q_CMAP = mpl.colors.LinearSegmentedColormap.from_list(
    "paper_q_vivid", ["#253494", "#2C7FB8", "#41B6C4", "#7FCDBB", "#FDE725"], N=256,
)
U_CMAP = mpl.colors.LinearSegmentedColormap.from_list(
    "paper_uncertainty_vivid", ["#3B0F70", "#8C2981", "#DE4968", "#F89540", "#FEE08B"], N=256,
)

# Confusion-matrix colormap -- exact ported from 代码/8.2图9.py::CMAP_ORIGINAL_LIKE (white -> light
# cyan -> light blue -> blue -> blue-purple -> deep red), used for every confusion matrix in this
# figure set for visual consistency with the manuscript's own Fig.9/Fig.11.
CONFUSION_CMAP = mpl.colors.LinearSegmentedColormap.from_list(
    "confusion_original_like",
    [(0.00, "#FFFFFF"), (0.12, "#E9F3F5"), (0.35, "#B7DCE5"),
     (0.60, "#4D79B8"), (0.78, "#6B4B7E"), (1.00, "#9B1B1B")],
)

# ---------------------------------------------------------------------------
# Method colors -- 9-method roster, muted/colorblind-conscious palette in the spirit of
# 代码/8.2图10.py's COLORS dict (not solid saturated "AI dashboard" hues).
# ---------------------------------------------------------------------------
METHOD_ORDER = [
    "RF", "TCN-GRU", "Multi-task TCN-GRU", "HTT-Net (adapted)",
    "Multi-source Attention", "MTF-AViTK", "Dynamic GIN + TGP", "DP2Net-adapted", "DC-PSR",
]
METHOD_COLORS = {
    "RF": "#8A8D8F",
    "TCN-GRU": "#7FA6C9",
    "Multi-task TCN-GRU": "#0072B2",
    "HTT-Net (adapted)": "#9B7FBD",
    "Multi-source Attention": "#56B4E9",
    "MTF-AViTK": "#D55E00",
    "Dynamic GIN + TGP": "#8C564B",
    "DP2Net-adapted": "#CC79A7",
    "DC-PSR": "#C44E52",
}
REPRESENTATIVE_METHODS = ["RF", "MTF-AViTK", "Multi-task TCN-GRU", "DC-PSR"]

ABLATION_IDS = ["A1", "A2", "A3", "A4", "A5", "A6"]
ABLATION_COLORS = {
    "A1": "#B7BDC2", "A2": "#93A6B8", "A3": "#6E93A8",
    "A4": "#0072B2", "A5": "#D55E00", "A6": "#009E73",
}
ABLATION_SUBSET = ["A1", "A4", "A5", "A6"]  # resolved decision, FIGURE_REBUILD_AUDIT.md

AXIS_COLOR = "#222222"
GRID_COLOR = "#D8D8D8"
HIGHLIGHT = "#F1E6E6"

METRIC_DIRECTION = {
    "Acc": "higher", "Macro-F1": "higher", "E-F1": "higher", "M-F1": "higher", "L-F1": "higher",
    "M-Pre": "higher", "M-Rec": "higher",
    "M→E": "lower", "M→L": "lower", "Rev": "lower", "Jump": "lower", "Smooth": "lower",
}


# ---------------------------------------------------------------------------
# Axis style -- ported verbatim (logic unchanged) from 代码/8.2图10.py
# ---------------------------------------------------------------------------
def add_axis_arrows(ax, x_pad=0.018, y_pad=0.020, show_x=True, show_y=True):
    arrow_kw = dict(arrowstyle="-|>", lw=1.1, color=AXIS_COLOR, shrinkA=0, shrinkB=0, mutation_scale=8)
    if show_x:
        ax.annotate("", xy=(1.0 + x_pad, 0.0), xytext=(0.0, 0.0),
                     xycoords="axes fraction", textcoords="axes fraction",
                     arrowprops=arrow_kw, clip_on=False, zorder=20)
    if show_y:
        ax.annotate("", xy=(0.0, 1.0 + y_pad), xytext=(0.0, 0.0),
                     xycoords="axes fraction", textcoords="axes fraction",
                     arrowprops=arrow_kw, clip_on=False, zorder=20)


def style_axis(ax, add_arrows=True, show_x_arrow=True, show_y_arrow=True, grid_axis="y"):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(not (add_arrows and show_y_arrow))
    ax.spines["bottom"].set_visible(not (add_arrows and show_x_arrow))
    if ax.spines["left"].get_visible():
        ax.spines["left"].set_color(AXIS_COLOR)
        ax.spines["left"].set_linewidth(0.9)
    if ax.spines["bottom"].get_visible():
        ax.spines["bottom"].set_color(AXIS_COLOR)
        ax.spines["bottom"].set_linewidth(0.9)
    if grid_axis:
        ax.grid(True, axis=grid_axis, linestyle="--", linewidth=0.55, alpha=0.5, color=GRID_COLOR)
    ax.set_axisbelow(True)
    ax.tick_params(axis="both", direction="in", width=0.8, length=3.2, colors=AXIS_COLOR)
    if add_arrows:
        add_axis_arrows(ax, show_x=show_x_arrow, show_y=show_y_arrow)


def add_highlight_for_last_group(ax, x_center, half_width=0.55, color=HIGHLIGHT, alpha=0.85):
    ax.axvspan(x_center - half_width, x_center + half_width, color=color, alpha=alpha, zorder=0)


HATCHES = {"h1": "////", "h2": "\\\\\\\\", "h3": "....", "h4": "xxxx"}


def hatched_bar(ax, x, values, width, color, hatch, label=None, zorder=3, linewidth=1.3):
    return ax.bar(x, values, width=width, facecolor="white", edgecolor=color,
                   linewidth=linewidth, hatch=hatch, label=label, zorder=zorder)


# ---------------------------------------------------------------------------
# Caption placement -- THIS ROUND'S rule: every panel caption sits BELOW the panel, centered,
# never above-left. No figure-level title anywhere (bare filename/README carries the Chinese
# figure name only).
# ---------------------------------------------------------------------------
def panel_caption_below(ax, text, y=-0.22, fontsize=9.0, fontweight="bold"):
    ax.text(0.5, y, text, transform=ax.transAxes, ha="center", va="top",
             fontsize=fontsize, fontweight=fontweight, color=AXIS_COLOR)


def caption_bottom_fig_frac(ax, y_offset, extra=0.028):
    """Figure-fraction y of the BOTTOM of a panel_caption_below() call at axes-fraction `y_offset`
    (negative), plus a small text-height margin. Use this (not a guessed constant) to size a block
    border so it clears every panel's own caption without eating into the next row -- computed from
    each axes' ACTUAL rendered position, per this project's standing rule against guessed offsets."""
    pos = ax.get_position()
    return pos.y0 + y_offset * pos.height - extra


# ---------------------------------------------------------------------------
# Refinement round (CIE-submission pass): outer canvas border + light block borders, per the
# explicit brief -- "参考当前实验设置图... 有明确整图外框; 大模块边界清楚". Both are drawn as the
# LAST step in each assemble.py, in figure-fraction coordinates, slightly inset from the true (0,1)
# edge so bbox_inches="tight" (used by save_all below) includes the full line weight without
# clipping it.
# ---------------------------------------------------------------------------
from matplotlib.patches import FancyBboxPatch as _FancyBboxPatch  # noqa: E402

OUTER_BORDER_COLOR = "#4A4A4A"
BLOCK_BORDER_COLOR = "#B9C2CC"
BLOCK_LABEL_COLOR = "#3A5068"


def add_outer_border(fig, inset=0.006, color=OUTER_BORDER_COLOR, lw=1.0, rounding=0.012):
    """Draws one rounded rectangle around the whole canvas. Call this LAST in assemble.py, after
    every panel/block has been drawn, so nothing overdraws it."""
    box = _FancyBboxPatch(
        (inset, inset), 1 - 2 * inset, 1 - 2 * inset,
        boxstyle=f"round,pad=0,rounding_size={rounding}",
        transform=fig.transFigure, facecolor="none", edgecolor=color, linewidth=lw,
        zorder=50, clip_on=False,
    )
    fig.add_artist(box)
    return box


def add_block_border(fig, bbox, label=None, color=BLOCK_BORDER_COLOR, lw=0.8, rounding=0.01,
                      label_color=BLOCK_LABEL_COLOR, label_fontsize=7.0, pad=0.010):
    """bbox = (x0, y0, x1, y1) in figure-fraction coordinates, spanning the panels that belong to
    one scientific block (e.g. all of Fig4-2's overall/Pareto/CI row). Draws a light rounded
    rectangle behind that region (zorder low, so it sits behind the panels already drawn on top)
    plus an optional small bold corner label. Compute bbox from the ACTUAL rendered positions of
    the block's own axes (ax.get_position()), never a guessed fraction -- the recurring lesson
    from every earlier caption-collision bug this project has hit."""
    x0, y0, x1, y1 = bbox
    x0, y0, x1, y1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
    box = _FancyBboxPatch(
        (x0, y0), x1 - x0, y1 - y0,
        boxstyle=f"round,pad=0,rounding_size={rounding}",
        transform=fig.transFigure, facecolor="none", edgecolor=color, linewidth=lw,
        zorder=0.5, clip_on=False,
    )
    fig.add_artist(box)
    if label:
        fig.text(x0 + 0.008, y1 - 0.006, label, transform=fig.transFigure, ha="left", va="top",
                  fontsize=label_fontsize, fontweight="bold", color=label_color, zorder=51)
    return box


DPI_EXPORT = 600
DPI_PREVIEW = 150


def save_all(fig, out_dir, basename, pdf=True, svg=True, png=True, pad_inches=0.04):
    os.makedirs(out_dir, exist_ok=True)
    paths = {}
    if pdf:
        p = os.path.join(out_dir, f"{basename}.pdf")
        fig.savefig(p, bbox_inches="tight", pad_inches=pad_inches)
        paths["pdf"] = p
    if svg:
        p = os.path.join(out_dir, f"{basename}.svg")
        fig.savefig(p, bbox_inches="tight", pad_inches=pad_inches)
        paths["svg"] = p
    if png:
        p = os.path.join(out_dir, f"{basename}_600dpi.png")
        fig.savefig(p, dpi=DPI_EXPORT, bbox_inches="tight", pad_inches=pad_inches)
        paths["png600"] = p
        p2 = os.path.join(out_dir, f"{basename}_preview.png")
        fig.savefig(p2, dpi=DPI_PREVIEW, bbox_inches="tight", pad_inches=pad_inches)
        paths["preview"] = p2
    return paths


FINAL_PDF_DIR_NAME = "final_pdf"


def save_fixed_name(fig, fixed_basename, new_figure_root, pad_inches=0.04):
    """Writes the submission-fixed-name PDF (+ 600dpi PNG) required by this round's brief, e.g.
    fig4_2_main_comparison.pdf -- into New_figure/final_pdf/, alongside (never replacing) each
    figure's own versioned outputs/ directory. `new_figure_root` is the paper_data/New_figure/
    path (each figure's assemble.py passes its own two-levels-up)."""
    out_dir = os.path.join(new_figure_root, FINAL_PDF_DIR_NAME)
    os.makedirs(out_dir, exist_ok=True)
    pdf_path = os.path.join(out_dir, f"{fixed_basename}.pdf")
    fig.savefig(pdf_path, bbox_inches="tight", pad_inches=pad_inches)
    png_path = os.path.join(out_dir, f"{fixed_basename}_600dpi.png")
    fig.savefig(png_path, dpi=DPI_EXPORT, bbox_inches="tight", pad_inches=pad_inches)
    return {"pdf": pdf_path, "png600": png_path}
