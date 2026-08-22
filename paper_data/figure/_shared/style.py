"""
Shared plotting style for DC-PSR Chapter 4 figures (fig1-fig5).

Import and call `apply_style()` once at the top of each plot_figX.py.
Also exposes shared color constants so Early/Middle/Late and method colors
stay consistent across all 5 figures.
"""
import matplotlib as mpl
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Stage colors (fixed across the whole chapter; from DCPSR_Chapter4_CN_Detailed.docx:
# "三阶段采用统一配色：Early蓝、Middle青/金、Late橙红")
# ---------------------------------------------------------------------------
STAGE_COLORS = {
    "early": "#2E5FA3",   # blue
    "middle": "#C99A2E",  # teal/gold -> using gold for clearer separation from blue/red
    "late": "#B23A2E",    # orange-red
}
STAGE_ORDER = ["early", "middle", "late"]
STAGE_LABELS = {"early": "Early", "middle": "Middle", "late": "Late"}

# ---------------------------------------------------------------------------
# Method colors (9 formal methods; DC-PSR and Multi-task TCN-GRU get emphasis
# colors since they are the proposed method and its direct backbone).
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
    "RF": "#8C8C8C",
    "TCN-GRU": "#6FA8DC",
    "Multi-task TCN-GRU": "#3D6EA8",
    "HTT-Net (adapted)": "#9C6ADE",
    "Multi-source Attention": "#5CB88A",
    "MTF-AViTK": "#D4A017",
    "Dynamic GIN + TGP": "#E07B39",
    "DP2Net-adapted": "#B24C63",
    "DC-PSR": "#C1272D",  # proposed method: strong red, consistent everywhere
}

# Representative-method subset used repeatedly (Fig.1 confusion matrices etc.)
REPRESENTATIVE_METHODS = ["RF", "MTF-AViTK", "Multi-task TCN-GRU", "DC-PSR"]

# A1-A6 ablation colors: light grey (A1) -> DC-PSR red (A6), per docx
# "曲线色由A1浅灰->A6主题色"
ABLATION_IDS = ["A1", "A2", "A3", "A4", "A5", "A6"]
ABLATION_COLORS = {
    "A1": "#C9C9C9",
    "A2": "#ADB8C9",
    "A3": "#8FA0C4",
    "A4": "#6E82B8",
    "A5": "#8C4B4B",
    "A6": "#C1272D",
}

# Metric direction dictionary (00_metadata/metrics.csv, verified)
METRIC_DIRECTION = {
    "Acc": "higher",
    "Accuracy": "higher",
    "MacroF1": "higher",
    "Macro-F1": "higher",
    "E_F1": "higher",
    "E-F1": "higher",
    "M_F1": "higher",
    "M-F1": "higher",
    "L_F1": "higher",
    "L-F1": "higher",
    "M_Precision": "higher",
    "M-Pre": "higher",
    "M_Rec": "higher",
    "M-Rec": "higher",
    "M_to_E": "lower",
    "M→E": "lower",
    "M_to_L": "lower",
    "M→L": "lower",
    "Rev": "lower",
    "Jump": "lower",
    "Smooth": "lower",
}

DPI = 300


def apply_style():
    mpl.rcParams.update({
        "figure.dpi": 120,
        "savefig.dpi": DPI,
        "font.size": 9,
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "axes.linewidth": 0.8,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 7.5,
        "legend.frameon": False,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": False,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,   # editable text in PDF/Illustrator
        "ps.fonttype": 42,
    })


def save_all(fig, out_dir, basename):
    """Save fig as PNG + PDF + SVG under out_dir/basename.{png,pdf,svg}."""
    import os
    os.makedirs(out_dir, exist_ok=True)
    for ext in ("png", "pdf", "svg"):
        path = os.path.join(out_dir, f"{basename}.{ext}")
        fig.savefig(path, bbox_inches="tight")
    return {ext: os.path.join(out_dir, f"{basename}.{ext}") for ext in ("png", "pdf", "svg")}


def direction_unified(value, metric_name):
    """Return a 0-1-ish 'benefit' value where higher is always better, for heatmap coloring only.
    Caller must still display the raw value as text."""
    d = METRIC_DIRECTION.get(metric_name, "higher")
    return -value if d == "lower" else value
