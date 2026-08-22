"""
Shared v3 (dense landscape, below-panel-caption) plotting style for DC-PSR Chapter 4 figures.

v3 fixes two structural problems in v2:
  1. v2's panel_caption() placed caption text via fig.text() at a *guessed* figure-fraction
     position read from ax.get_position() -- correct only if nothing about the layout changes
     between when the caption is placed and when the figure is saved. v3 instead nests every
     panel's plot area and its caption strip inside the SAME GridSpec cell via subgridspec(), so
     the caption is geometrically locked to its panel regardless of draw order, tight_layout, or
     bbox_inches="tight" cropping. There is no bbox-guessing left anywhere in this module.
  2. v2 used a figure-level bottom caption ("主比较" etc.) as a stand-in for a top title. v3 drops
     figure-level titling entirely -- the Chinese figure name lives only in the folder name, the
     README, and the output filename semantics, never rendered on the canvas.

Color constants, the metric-direction dictionary, and validation-relevant data helpers are
UNCHANGED from v2 (re-exported here, not redefined) so v1/v2/v3 all agree on what "DC-PSR red" or
"lower is better" mean. Only the layout/caption machinery is new.
"""
import os
import sys
import matplotlib as mpl
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
from style_v2 import (  # noqa: F401  (re-exported for plot_figX_v3.py convenience)
    STAGE_COLORS, STAGE_ORDER, STAGE_LABELS, STAGE_MARKERS, DEGRADATION_CMAP,
    METHOD_ORDER, METHOD_COLORS, REPRESENTATIVE_METHODS,
    ABLATION_IDS, ABLATION_COLORS, METRIC_DIRECTION,
    BENEFIT_CMAP, DIVERGING_CMAP, CJK_FONT, DPI,
)

# NOTE: v2's panel_letter / panel_caption / figure_caption are deliberately NOT imported here --
# v3 replaces them with panel_container() below. Do not reach for the v2 caption helpers in a
# plot_figX_v3.py script.


def apply_style():
    mpl.rcParams.update({
        "figure.dpi": 120,
        "savefig.dpi": DPI,
        "font.size": 9.3,
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "axes.titlesize": 9.3,
        "axes.labelsize": 9.0,
        "axes.linewidth": 0.8,
        "xtick.labelsize": 8.0,
        "ytick.labelsize": 8.0,
        "legend.fontsize": 7.6,
        "legend.frameon": False,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": "#E4E6E8",
        "grid.linewidth": 0.6,
        "axes.axisbelow": True,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })


def panel_container(fig, outer_spec, caption, caption_height=0.065, fontsize=9.3,
                     caption_color="#1A1A1A", hspace=0.015, letter_bold=True):
    """Split one GridSpec cell into a plot area (top, 1-caption_height) and a caption strip
    (bottom, caption_height), both anchored inside the SAME cell via subgridspec -- geometrically
    exact, no post-hoc position lookup.

    Returns `content_spec`, a SubplotSpec occupying the plot-area row. The caller adds one axes
    directly to it (fig.add_subplot(content_spec, ...)) for a single-axes panel, or further
    subdivides it with `content_spec.subgridspec(...)` for a multi-axes panel group (the caption
    then describes the whole group, centered under it).

    `caption` should already read like "(a) Overall predictive performance" -- letter and title
    together, since this is the only place either appears (no separate upper-left letter in v3).
    """
    inner = outer_spec.subgridspec(2, 1, height_ratios=[1 - caption_height, caption_height],
                                    hspace=hspace)
    content_spec = inner[0]
    cap_ax = fig.add_subplot(inner[1])
    cap_ax.axis("off")
    weight = "bold" if letter_bold else "normal"
    cap_ax.text(0.5, 0.58, caption, ha="center", va="center", fontsize=fontsize,
                color=caption_color, transform=cap_ax.transAxes, fontweight=weight)
    return content_spec, cap_ax


def sub_caption(fig, outer_spec, caption, caption_height=0.10, fontsize=8.0,
                 caption_color="#444444", hspace=0.05):
    """Lighter-weight caption for a SUB-panel inside an already-captioned group (e.g. each of the
    2x2 confusion matrices, which each want their own small method-name label below them, nested
    inside panel (b)'s own group caption). Same geometric-lock mechanism as panel_container()."""
    inner = outer_spec.subgridspec(2, 1, height_ratios=[1 - caption_height, caption_height],
                                    hspace=hspace)
    content_spec = inner[0]
    cap_ax = fig.add_subplot(inner[1])
    cap_ax.axis("off")
    cap_ax.text(0.5, 0.5, caption, ha="center", va="center", fontsize=fontsize,
                color=caption_color, transform=cap_ax.transAxes)
    return content_spec, cap_ax


def save_all(fig, out_dir, basename):
    os.makedirs(out_dir, exist_ok=True)
    paths = {}
    for ext in ("png", "pdf", "svg"):
        path = os.path.join(out_dir, f"{basename}.{ext}")
        fig.savefig(path, bbox_inches="tight")
        paths[ext] = path
    return paths
