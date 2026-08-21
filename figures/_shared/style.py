"""Publication-wide matplotlib style for the Chapter 4 figure set."""

from __future__ import annotations

import matplotlib as mpl


FIG_WIDTH = 7.2  # 182.9 mm, full two-column width
BASE_FONT_SIZE = 7.2


def apply_publication_style() -> None:
    """Apply clean, editable, journal-width defaults."""
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans", "Liberation Sans", "sans-serif"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": BASE_FONT_SIZE,
            "axes.labelsize": 7.4,
            "axes.titlesize": 7.4,
            "xtick.labelsize": 6.5,
            "ytick.labelsize": 6.5,
            "legend.fontsize": 6.2,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": 0.72,
            "xtick.major.width": 0.6,
            "ytick.major.width": 0.6,
            "xtick.major.size": 2.5,
            "ytick.major.size": 2.5,
            "legend.frameon": False,
            "lines.linewidth": 1.15,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )
