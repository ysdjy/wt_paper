from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ET

import matplotlib

matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "nature_figures"
PLOT_DATA = OUT / "plot_data"

METHOD_ORDER = [
    "DC-PSR",
    "Multi-task TCN-GRU",
    "TCN-GRU",
    "RF",
    "HTT-Net",
    "Multi-source Attention",
    "MTF-AViTK",
    "Dynamic GIN + TGP",
    "DP2Net-adapted",
]

METHOD_COLORS = {
    "DC-PSR": "#D55E00",
    "Multi-task TCN-GRU": "#0072B2",
    "TCN-GRU": "#56B4E9",
    "RF": "#4D4D4D",
    "HTT-Net": "#CC79A7",
    "Multi-source Attention": "#E69F00",
    "MTF-AViTK": "#009E73",
    "Dynamic GIN + TGP": "#7A5195",
    "DP2Net-adapted": "#8C8C3A",
}

METHOD_MARKERS = {
    "DC-PSR": "o",
    "Multi-task TCN-GRU": "D",
    "TCN-GRU": "^",
    "RF": "s",
    "HTT-Net": "h",
    "Multi-source Attention": "p",
    "MTF-AViTK": "v",
    "Dynamic GIN + TGP": "X",
    "DP2Net-adapted": "*",
}

DISPLAY_RENAME = {
    "HTT-Net (adapted)": "HTT-Net",
}

CMAP_ABSOLUTE = LinearSegmentedColormap.from_list(
    "navy_teal_gold", ["#17324D", "#2A7F86", "#F3D9A3"]
)
CMAP_DELTA = LinearSegmentedColormap.from_list(
    "blue_white_vermillion", ["#4C78A8", "#F7F7F7", "#D55E00"]
)
CMAP_LIFE = LinearSegmentedColormap.from_list(
    "life", ["#17324D", "#2A7F86", "#F3D9A3"]
)


def apply_style() -> None:
    """Apply the shared full-width Nature-style visual system."""
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": 7.2,
            "axes.labelsize": 7.5,
            "axes.titlesize": 8.0,
            "axes.titleweight": "bold",
            "xtick.labelsize": 6.6,
            "ytick.labelsize": 6.6,
            "legend.fontsize": 6.4,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": 0.7,
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


def read_csv(relpath: str, **kwargs) -> pd.DataFrame:
    return pd.read_csv(ROOT / relpath, **kwargs)


def clean_method_names(frame: pd.DataFrame, column: str = "Method") -> pd.DataFrame:
    out = frame.copy()
    out[column] = out[column].replace(DISPLAY_RENAME)
    return out


def panel_label(ax, label: str, x: float = -0.10, y: float = 1.04) -> None:
    ax.text(
        x,
        y,
        label,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=8.5,
        fontweight="bold",
        clip_on=False,
    )


def save_figure(fig, out_dir: Path, stem: str) -> list[Path]:
    """Export editable SVG/PDF plus a 600-dpi PNG preview."""
    out_dir.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []
    for ext in ("svg", "pdf", "png"):
        path = out_dir / f"{stem}.{ext}"
        kwargs = {"bbox_inches": "tight", "pad_inches": 0.035}
        if ext == "png":
            kwargs["dpi"] = 600
            kwargs["metadata"] = {"Software": "Python/matplotlib", "Description": "600 dpi preview"}
        fig.savefig(path, **kwargs)
        saved.append(path)
    plt.close(fig)
    return saved


def write_plot_data(frame: pd.DataFrame, filename: str) -> Path:
    PLOT_DATA.mkdir(parents=True, exist_ok=True)
    path = PLOT_DATA / filename
    frame.to_csv(path, index=False, encoding="utf-8-sig")
    return path


def rank_desc(values: np.ndarray) -> np.ndarray:
    order = np.argsort(-np.asarray(values), kind="stable")
    ranks = np.empty(len(order), dtype=int)
    ranks[order] = np.arange(1, len(order) + 1)
    return ranks


def minmax(values: np.ndarray, higher_better: bool = True) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    lo, hi = np.nanmin(arr), np.nanmax(arr)
    if np.isclose(hi, lo):
        return np.full_like(arr, 0.5)
    score = (arr - lo) / (hi - lo)
    return score if higher_better else 1.0 - score


def heatmap(
    ax,
    matrix: np.ndarray,
    xlabels: list[str],
    ylabels: list[str],
    *,
    cmap,
    vmin: float,
    vmax: float,
    cbar_label: str,
    annotate: np.ndarray | None = None,
    annotate_fmt: str = "{}",
    show_ylabels: bool = True,
    outline_row: int | None = None,
    cbar_orientation: str = "horizontal",
):
    im = ax.imshow(matrix, cmap=cmap, vmin=vmin, vmax=vmax, aspect="auto", interpolation="nearest")
    ax.set_xticks(np.arange(len(xlabels)), labels=xlabels)
    ax.set_yticks(np.arange(len(ylabels)), labels=ylabels if show_ylabels else [""] * len(ylabels))
    ax.tick_params(which="both", length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    if annotate is not None:
        norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                val = matrix[i, j]
                rgba = cmap(norm(val))
                lum = 0.299 * rgba[0] + 0.587 * rgba[1] + 0.114 * rgba[2]
                color = "white" if lum < 0.48 else "#202020"
                ax.text(j, i, annotate_fmt.format(annotate[i, j]), ha="center", va="center", fontsize=5.8, color=color)
    if outline_row is not None:
        rect = mpl.patches.Rectangle(
            (-0.49, outline_row - 0.49),
            matrix.shape[1] - 0.02,
            0.98,
            fill=False,
            edgecolor=METHOD_COLORS["DC-PSR"],
            linewidth=1.1,
            clip_on=False,
        )
        ax.add_patch(rect)
    if cbar_orientation == "horizontal":
        cbar = ax.figure.colorbar(im, ax=ax, orientation="horizontal", fraction=0.08, pad=0.10, aspect=22)
    else:
        cbar = ax.figure.colorbar(im, ax=ax, orientation="vertical", fraction=0.05, pad=0.04)
    cbar.set_label(cbar_label, fontsize=6.2)
    cbar.ax.tick_params(labelsize=5.8, width=0.5, length=2)
    cbar.outline.set_linewidth(0.5)
    return im


def pca_svd(matrix: np.ndarray, n_components: int = 2) -> tuple[np.ndarray, np.ndarray]:
    """Deterministic PCA using NumPy SVD; no model fitting or label use."""
    x = np.asarray(matrix, dtype=float)
    x = x - x.mean(axis=0, keepdims=True)
    scale = x.std(axis=0, ddof=1, keepdims=True)
    scale[~np.isfinite(scale) | np.isclose(scale, 0)] = 1.0
    x = x / scale
    u, s, _ = np.linalg.svd(x, full_matrices=False)
    scores = u[:, :n_components] * s[:n_components]
    var = s**2
    explained = var[:n_components] / var.sum()
    return scores, explained


def verify_svg_text(path: Path) -> bool:
    root = ET.parse(path).getroot()
    return any(node.tag.endswith("text") for node in root.iter())

