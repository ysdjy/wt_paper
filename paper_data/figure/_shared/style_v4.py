"""
Shared v4 (publication-grade, true-physical-size) plotting style for DC-PSR Chapter 4 figures.

v4 keeps v3's caption mechanism (panel_container / sub_caption -- geometrically locked via nested
GridSpec, already validated correct across all 5 figures in round 3) UNCHANGED, re-exported here
rather than reimplemented. What's new in v4:
  - a Times New Roman + STIX-math typography stack, matching the ORIGINAL paper's own plotting
    code (代码/*.py all set exactly this rcParams combination -- confirmed by reading it, not a
    new stylistic choice this round)
  - a new, higher-impact color palette (exact hex values specified in the round-4 task brief)
  - true-physical-size figure creation: MM_TO_IN() + master (width_mm, height_mm) per figure, so
    every figure is authored at its actual print size from the start, never a big screen canvas
    shrunk down later (which would make text too small to read)
  - save_all() now emits four artifacts: figX_v4.pdf, figX_v4.svg, figX_v4_600dpi.png (all at
    master physical size), and figX_v4_paper_preview.png (a comfortably-large raster of the SAME
    master size, meant for on-screen "does this actually read at 178mm" review)
"""
import os
import sys
import matplotlib as mpl
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
from style_v3 import panel_container, sub_caption  # noqa: F401  (unchanged caption mechanism)
from style_v2 import METRIC_DIRECTION  # noqa: F401  (unchanged direction dictionary)

# ---------------------------------------------------------------------------
# Physical size helpers
# ---------------------------------------------------------------------------
MM_PER_IN = 25.4


def mm_to_in(mm):
    return mm / MM_PER_IN


MASTER_SIZE_MM = {
    "fig1": (178, 120),
    "fig2": (178, 125),
    "fig3": (178, 130),
    "fig4": (178, 128),
    "fig5": (178, 132),
}


def master_figsize_in(fig_key):
    w_mm, h_mm = MASTER_SIZE_MM[fig_key]
    return (mm_to_in(w_mm), mm_to_in(h_mm))


# ---------------------------------------------------------------------------
# Stage colors -- exact hex values from the round-4 brief. Must be identical across fig3/4/5.
# ---------------------------------------------------------------------------
STAGE_COLORS = {
    "early": "#2F6FB3",
    "middle": "#2E8B57",
    "late": "#E76F51",
}
STAGE_ORDER = ["early", "middle", "late"]
STAGE_LABELS = {"early": "Early", "middle": "Middle", "late": "Late"}
STAGE_MARKERS = {"early": "o", "middle": "^", "late": "s"}

DEGRADATION_CMAP = mpl.colors.LinearSegmentedColormap.from_list(
    "degradation_v4", [STAGE_COLORS["early"], STAGE_COLORS["middle"], STAGE_COLORS["late"]],
)

# ---------------------------------------------------------------------------
# Method colors
# ---------------------------------------------------------------------------
METHOD_ORDER = [
    "RF", "TCN-GRU", "Multi-task TCN-GRU", "HTT-Net (adapted)",
    "Multi-source Attention", "MTF-AViTK", "Dynamic GIN + TGP", "DP2Net-adapted", "DC-PSR",
]
METHOD_COLORS = {
    "RF": "#8A8D8F",
    "TCN-GRU": "#7FA6C9",
    "Multi-task TCN-GRU": "#2F6FB3",
    "HTT-Net (adapted)": "#9B7FBD",
    "Multi-source Attention": "#6FAE8C",
    "MTF-AViTK": "#D39B23",
    "Dynamic GIN + TGP": "#B9793D",
    "DP2Net-adapted": "#A15A63",
    "DC-PSR": "#C73635",
}
REPRESENTATIVE_METHODS = ["RF", "MTF-AViTK", "Multi-task TCN-GRU", "DC-PSR"]
REPRESENTATIVE_METHODS_5 = ["RF", "TCN-GRU", "MTF-AViTK", "Multi-task TCN-GRU", "DC-PSR"]

ABLATION_IDS = ["A1", "A2", "A3", "A4", "A5", "A6"]
ABLATION_COLORS = {
    "A1": "#B7BDC2", "A2": "#93A6B8", "A3": "#6E93A8",
    "A4": "#3E7C99", "A5": "#D39B23", "A6": "#2E8B57",
}

# Sequential "benefit" colormap: terracotta (worst) -> cream -> light cyan -> deep blue (best)
BENEFIT_CMAP = mpl.colors.LinearSegmentedColormap.from_list(
    "benefit_v4", ["#C85445", "#F2CF86", "#85C7C1", "#24588F"],
)
# Diverging "delta" colormap: regression <-> neutral <-> improvement
DIVERGING_CMAP = mpl.colors.LinearSegmentedColormap.from_list(
    "diverging_v4", ["#B85250", "#F5F1E8", "#25847E"],
)
# Sequential Blues for confusion matrices specifically (distinct from BENEFIT_CMAP, matching the
# brief's explicit "真正的 sequential Blues, 不要继续使用 benefit heatmap colormap")
CONFUSION_CMAP = "Blues"

DPI_EXPORT = 600
DPI_PREVIEW = 200  # paper-preview raster: large enough to zoom, small enough to stay a manageable file


def apply_style():
    mpl.rcParams.update({
        "figure.dpi": 150,
        "savefig.dpi": DPI_EXPORT,
        "font.family": "Times New Roman",
        "mathtext.fontset": "stix",
        "axes.unicode_minus": False,
        "font.size": 8.5,
        "axes.titlesize": 8.5,
        "axes.labelsize": 8.7,
        "axes.linewidth": 0.75,
        "xtick.labelsize": 7.6,
        "ytick.labelsize": 7.6,
        "xtick.major.width": 0.7,
        "ytick.major.width": 0.7,
        "xtick.major.size": 2.4,
        "ytick.major.size": 2.4,
        "legend.fontsize": 7.5,
        "legend.frameon": False,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": "#D8DADC",
        "grid.linewidth": 0.4,
        "grid.alpha": 0.28,
        "axes.axisbelow": True,
        "lines.linewidth": 1.6,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    })


LW_MAIN = 1.7      # main data curve
LW_AUX = 1.0        # auxiliary/secondary curve
LW_SPINE = 0.75     # axis spine


def save_all(fig, out_dir, basename):
    """Export pdf/svg/600dpi-png/paper-preview-png, all at the figure's own physical size
    (figsize is set by the caller via master_figsize_in()); this function does not rescale."""
    os.makedirs(out_dir, exist_ok=True)
    paths = {}
    for ext, dpi in (("pdf", None), ("svg", None)):
        path = os.path.join(out_dir, f"{basename}.{ext}")
        fig.savefig(path, bbox_inches="tight")
        paths[ext] = path
    png600 = os.path.join(out_dir, f"{basename}_600dpi.png")
    fig.savefig(png600, dpi=DPI_EXPORT, bbox_inches="tight")
    paths["600dpi_png"] = png600
    preview = os.path.join(out_dir, f"{basename}_paper_preview.png")
    fig.savefig(preview, dpi=DPI_PREVIEW, bbox_inches="tight")
    paths["paper_preview_png"] = preview
    return paths
