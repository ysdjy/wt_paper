"""
Shared v2 (reference-style) plotting style for DC-PSR Chapter 4 figures.

This is a SEPARATE module from style.py (v1) so that v1's plot_figX.py scripts remain byte-for-
byte reproducible and untouched. v2 scripts (plot_figX_v2.py) import from here instead.

Palette and layout conventions are drawn from paper_data/figure/figX/reference/*.png (style only
-- see each reference/SOURCE.md for what was and was not learned from them):
  - muted navy / teal / gold sequential palette for Early/Middle/Late (ordered, cool->warm)
  - DC-PSR = vermillion accent, Multi-task TCN-GRU = blue accent (matches fig1 reference mockup)
  - no top figure-level suptitle; a figure-level caption is centered at the BOTTOM instead
  - each panel keeps a small bold letter "(a)" in its own top-left corner, but its descriptive
    title moves to a centered caption BELOW the panel (not above)
"""
import os
import matplotlib as mpl
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Stage colors: ordered, cool (early) -> warm (late), matching the reference mockups'
# navy -> teal -> gold degradation-position colormap and violin/scatter coloring.
# ---------------------------------------------------------------------------
STAGE_COLORS = {
    "early": "#1B3A5C",   # dark navy
    "middle": "#2A8C7A",  # teal
    "late": "#D9A441",    # warm gold/amber
}
STAGE_ORDER = ["early", "middle", "late"]
STAGE_LABELS = {"early": "Early", "middle": "Middle", "late": "Late"}
STAGE_MARKERS = {"early": "o", "middle": "^", "late": "s"}

# Continuous "relative life / q" colormap consistent with the navy->teal->gold stage colors
DEGRADATION_CMAP = mpl.colors.LinearSegmentedColormap.from_list(
    "degradation_navy_teal_gold",
    [STAGE_COLORS["early"], STAGE_COLORS["middle"], STAGE_COLORS["late"]],
)

# Sequential "benefit" colormap for heatmaps (0=worst, 1=best), built from the same navy/teal/gold
# family so every heatmap in every figure reads as part of one coherent palette instead of a
# generic rainbow RdYlGn scale. Pale warm cream = worst, dark navy = best.
BENEFIT_CMAP = mpl.colors.LinearSegmentedColormap.from_list(
    "benefit_cream_gold_teal_navy",
    ["#F7ECD8", "#D9A441", "#2A8C7A", "#1B3A5C"],
)
# Diverging variant (for delta/effect matrices centered at 0): terracotta (regression) <-> cream
# (no change) <-> teal (improvement).
DIVERGING_CMAP = mpl.colors.LinearSegmentedColormap.from_list(
    "diverging_terracotta_cream_teal",
    ["#B0555E", "#E8CBB0", "#F7ECD8", "#B7DCD2", "#2A8C7A"],
)

# ---------------------------------------------------------------------------
# Method colors -- muted, DC-PSR and Multi-task TCN-GRU get the two accent colors used in the
# fig1 reference mockup (vermillion circle for DC-PSR, blue diamond for its backbone).
# ---------------------------------------------------------------------------
METHOD_ORDER = [
    "RF",
    "TCN-GRU",
    "Multi-task TCN-GRU",
    "HTT-Net (adapted)",
    "Multi-source Attention",
    "MTF-AViTK",
    "Dynamic GIN + TGP",
    "DP2Net-adapted",
    "DC-PSR",
]

METHOD_COLORS = {
    "RF": "#8A8D8F",
    "TCN-GRU": "#7FB2C9",
    "Multi-task TCN-GRU": "#2E6FA3",
    "HTT-Net (adapted)": "#9B7FBD",
    "Multi-source Attention": "#5FA88C",
    "MTF-AViTK": "#D9A441",
    "Dynamic GIN + TGP": "#C97B3D",
    "DP2Net-adapted": "#B0555E",
    "DC-PSR": "#D9541F",  # vermillion accent, consistent everywhere
}

REPRESENTATIVE_METHODS = ["RF", "MTF-AViTK", "Multi-task TCN-GRU", "DC-PSR"]

# A1-A6 ablation colors: light grey (A1, "raw") -> teal (A6, "final balanced"), with A5
# ("strongest ordered filter") called out in gold/amber, matching the MATLAB fig3 reference.
ABLATION_IDS = ["A1", "A2", "A3", "A4", "A5", "A6"]
ABLATION_COLORS = {
    "A1": "#B7BDC2",
    "A2": "#93A6B8",
    "A3": "#6E93A8",
    "A4": "#3E7C99",
    "A5": "#D9A441",
    "A6": "#2A8C7A",
}

METRIC_DIRECTION = {
    "Acc": "higher", "Accuracy": "higher", "MacroF1": "higher", "Macro-F1": "higher",
    "E_F1": "higher", "E-F1": "higher", "M_F1": "higher", "M-F1": "higher",
    "L_F1": "higher", "L-F1": "higher", "M_Precision": "higher", "M-Pre": "higher",
    "M_Rec": "higher", "M-Rec": "higher",
    "M_to_E": "lower", "M→E": "lower", "M_to_L": "lower", "M→L": "lower",
    "Rev": "lower", "Jump": "lower", "Smooth": "lower",
}

DPI = 300


def apply_style():
    mpl.rcParams.update({
        "figure.dpi": 120,
        "savefig.dpi": DPI,
        "font.size": 9.5,
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "axes.titlesize": 9.5,
        "axes.labelsize": 9.5,
        "axes.linewidth": 0.8,
        "xtick.labelsize": 8.3,
        "ytick.labelsize": 8.3,
        "legend.fontsize": 7.8,
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


def panel_letter(ax, letter, loc="upper left", fontsize=10.5, pad=0.02):
    """Small bold panel letter e.g. '(a)' inside the panel's own corner (2D or 3D axes)."""
    positions = {
        "upper left": (pad, 1 - pad, "left", "top"),
        "upper right": (1 - pad, 1 - pad, "right", "top"),
    }
    x, y, ha, va = positions.get(loc, positions["upper left"])
    if hasattr(ax, "text2D"):
        ax.text2D(x, y, letter, transform=ax.transAxes, fontsize=fontsize, fontweight="bold",
                   ha=ha, va=va)
    else:
        ax.text(x, y, letter, transform=ax.transAxes, fontsize=fontsize, fontweight="bold",
                 ha=ha, va=va)


def panel_caption(fig, ax, text, pad=0.045, fontsize=8.8):
    """Descriptive panel caption CENTERED BELOW the panel (not above), per the v2 layout
    requirement. Must be called after the figure layout (subplots_adjust / GridSpec) is final,
    since it reads the axis's figure-relative bounding box."""
    fig.canvas.draw()
    pos = ax.get_position()
    x_center = (pos.x0 + pos.x1) / 2
    y = pos.y0 - pad
    fig.text(x_center, y, text, ha="center", va="top", fontsize=fontsize, wrap=True)


CJK_FONT = "Microsoft YaHei"  # Arial/DejaVu Sans (the rcParams default) have no CJK glyphs


def figure_caption(fig, text, y=0.012, fontsize=13, subtitle=None, subtitle_fontsize=9.5):
    """Figure-level name, centered at the very bottom of the whole canvas -- replaces the
    old top suptitle entirely (v2 requirement: no top-level big title). `text` may contain CJK
    characters (explicitly set to a CJK-capable font since the figure's default sans-serif stack
    does not carry Chinese glyphs); `subtitle`, if given, is a smaller English line placed just
    above it for readers relying on the English caption."""
    y0 = y
    if subtitle:
        fig.text(0.5, y0 + fontsize / 720, subtitle, ha="center", va="bottom",
                  fontsize=subtitle_fontsize, color="#444444")
        y0 = y0 + fontsize / 720 + subtitle_fontsize / 620
    fig.text(0.5, y0, text, ha="center", va="bottom", fontsize=fontsize, fontweight="bold",
              fontfamily=CJK_FONT)


def save_all(fig, out_dir, basename):
    os.makedirs(out_dir, exist_ok=True)
    paths = {}
    for ext in ("png", "pdf", "svg"):
        path = os.path.join(out_dir, f"{basename}.{ext}")
        fig.savefig(path, bbox_inches="tight")
        paths[ext] = path
    return paths
