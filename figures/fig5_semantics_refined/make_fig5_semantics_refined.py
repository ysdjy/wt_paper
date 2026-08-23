"""Publication-ready Figure 5 built only from audited C6 sources.

Scientific content is frozen. This script changes visual hierarchy and layout only:
stage probability evolution, probability-simplex ordering, q agreement, the saved
hidden-representation PCA manifold, and physical-wear semantics.
"""

from __future__ import annotations

from datetime import datetime
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import numpy as np
import pandas as pd
from scipy.stats import spearmanr


# Editable vector text and embedded TrueType PDF fonts.
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Liberation Sans"]
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["pdf.fonttype"] = 42

SCRIPT_VERSION = "2.0.0"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = Path(__file__).resolve().parent
OUTPUT_STEM = OUT_DIR / "fig5_semantics_refined"

TRAJECTORY_SOURCE = Path(
    "补充材料/小论文/9_probability_wear_consistency_analysis/"
    "Data_5_4_A6_probability_wear_trajectory.csv"
)
REPRESENTATION_SOURCE = Path(
    "补充材料/小论文/10_第五章顶刊风格可视化/"
    "figures_representation_space/repr_hidden_hct.csv"
)
AUDIT_SOURCE = Path("nature_figures/FIGURE_DATA_AUDIT.md")
REFERENCE_SCRIPT = Path("nature_figures/scripts/fig5_semantics.py")

STAGES = ["early", "middle", "late"]
STAGE_LABELS = ["Early", "Middle", "Late"]
STAGE_COLORS = {
    "early": "#284F70",
    "middle": "#2C887F",
    "late": "#D98F28",
}
STAGE_ZONE_COLORS = {
    "early": "#DCE7EE",
    "middle": "#DCECE8",
    "late": "#F7E8CF",
}
STAGE_MARKERS = {"early": "o", "middle": "^", "late": "s"}
LIFE_CMAP = LinearSegmentedColormap.from_list(
    "degradation_life",
    [STAGE_COLORS["early"], STAGE_COLORS["middle"], "#F0D49A"],
)
DENSITY_CMAP = LinearSegmentedColormap.from_list(
    "run_density", ["#183C58", "#2E807D", "#E7C779"]
)

TEXT = "#252A2E"
MUTED = "#687278"
SPINE = "#515A5F"
GRID = "#E6EBED"

PANEL_TITLES = {
    "a": "Full lifecycle probability trajectory",
    "b": "Ordered trajectory in probability simplex",
    "c": "Continuous degradation-position agreement",
    "d": "Shared latent degradation manifold",
    "e": "Physical wear semantics",
}


def apply_style() -> None:
    """Global typography and line settings for a 183 mm journal figure."""
    mpl.rcParams.update(
        {
            "font.size": 7.0,
            "axes.labelsize": 7.2,
            "xtick.labelsize": 6.2,
            "ytick.labelsize": 6.2,
            "legend.fontsize": 5.9,
            "axes.linewidth": 0.70,
            "axes.edgecolor": SPINE,
            "axes.labelcolor": TEXT,
            "text.color": TEXT,
            "xtick.color": SPINE,
            "ytick.color": SPINE,
            "xtick.major.width": 0.55,
            "ytick.major.width": 0.55,
            "xtick.major.size": 2.5,
            "ytick.major.size": 2.5,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "legend.frameon": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )


def absolute(relative_path: Path) -> Path:
    path = PROJECT_ROOT / relative_path
    if not path.exists():
        raise FileNotFoundError(f"Required project file not found: {relative_path}")
    return path


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pca_svd(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Deterministic standardized SVD PCA matching the audited workflow."""
    x = matrix.astype(float)
    x -= x.mean(axis=0, keepdims=True)
    scale = x.std(axis=0, ddof=1, keepdims=True)
    scale[~np.isfinite(scale) | np.isclose(scale, 0)] = 1.0
    x /= scale
    u, singular, _ = np.linalg.svd(x, full_matrices=False)
    scores = u[:, :2] * singular[:2]
    explained = (singular[:2] ** 2) / np.sum(singular**2)
    return scores, explained


def ternary_xy(probability: np.ndarray) -> np.ndarray:
    """Early=(0,0), Middle=(0.5,sqrt(3)/2), Late=(1,0)."""
    p_middle = probability[:, 1]
    p_late = probability[:, 2]
    return np.column_stack([p_late + 0.5 * p_middle, np.sqrt(3) / 2 * p_middle])


def load_audited_data() -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    """Load and validate the two files designated by the figure audit."""
    trajectory = pd.read_csv(absolute(TRAJECTORY_SOURCE)).sort_values("run_id").reset_index(drop=True)
    required = {
        "run_id",
        "VB_true",
        "q_true",
        "q_pred",
        "true_stage",
        "pred_stage",
        "prob_early",
        "prob_middle",
        "prob_late",
    }
    missing = required.difference(trajectory.columns)
    if missing:
        raise ValueError(f"Trajectory source is missing columns: {sorted(missing)}")
    numeric = [
        "run_id",
        "VB_true",
        "q_true",
        "q_pred",
        "prob_early",
        "prob_middle",
        "prob_late",
    ]
    trajectory[numeric] = trajectory[numeric].apply(pd.to_numeric, errors="raise")
    if trajectory[numeric].isna().any().any():
        raise ValueError("Trajectory source contains missing numeric values")
    probability_sum = trajectory[["prob_early", "prob_middle", "prob_late"]].sum(axis=1)
    if not np.allclose(probability_sum, 1.0, atol=1e-5):
        raise ValueError("Stage probabilities do not sum to one")
    trajectory["true_stage"] = trajectory["true_stage"].str.lower()
    trajectory["pred_stage"] = trajectory["pred_stage"].str.lower()
    observed_order = list(dict.fromkeys(trajectory["true_stage"].tolist()))
    if observed_order != STAGES:
        raise ValueError(f"Unexpected lifecycle stage order: {observed_order}")
    run_span = trajectory["run_id"].max() - trajectory["run_id"].min()
    trajectory["relative_life"] = (
        trajectory["run_id"] - trajectory["run_id"].min()
    ) / run_span

    representation_all = pd.read_csv(absolute(REPRESENTATION_SOURCE))
    representation = representation_all[
        (representation_all["split"] == "test_C6")
        & (representation_all["condition"] == "C6")
    ].copy()
    representation["true_stage"] = representation["true_stage"].str.lower()
    hidden_columns = [column for column in representation.columns if column.startswith("h_")]
    if len(hidden_columns) != 64:
        raise ValueError(f"Expected 64 saved hidden features, found {len(hidden_columns)}")
    hidden = representation[hidden_columns].apply(pd.to_numeric, errors="raise").to_numpy(float)
    if hidden.shape[0] != len(trajectory):
        raise ValueError(
            f"Audited row mismatch: {len(trajectory)} lifecycle rows versus {hidden.shape[0]} representations"
        )
    scores, explained = pca_svd(hidden)
    representation["PC1"], representation["PC2"] = scores[:, 0], scores[:, 1]
    return trajectory, representation, explained


def stage_bands(trajectory: pd.DataFrame) -> list[tuple[str, float, float, float]]:
    """Return contiguous true-stage spans in relative-life coordinates."""
    labels = trajectory["true_stage"].to_numpy()
    x = trajectory["relative_life"].to_numpy(float)
    change_indices = np.flatnonzero(labels[1:] != labels[:-1])
    boundaries = [0.0]
    boundaries.extend(float(0.5 * (x[index] + x[index + 1])) for index in change_indices)
    boundaries.append(1.0)
    starts = [0] + [int(index + 1) for index in change_indices]
    bands = []
    for position, start in enumerate(starts):
        stage = str(labels[start])
        left, right = boundaries[position], boundaries[position + 1]
        bands.append((stage, left, right, 0.5 * (left + right)))
    return bands


def add_stage_background(ax: mpl.axes.Axes, bands: list[tuple[str, float, float, float]]) -> None:
    for stage, left, right, _ in bands:
        ax.axvspan(left, right, facecolor=STAGE_ZONE_COLORS[stage], alpha=0.38, lw=0, zorder=-3)
    for _, _, right, _ in bands[:-1]:
        ax.axvline(right, color="#AEB8BD", lw=0.55, ls=(0, (2.0, 2.2)), zorder=-1)


def quiet_grid(ax: mpl.axes.Axes) -> None:
    ax.grid(axis="y", color=GRID, linewidth=0.45, zorder=-2)
    ax.set_axisbelow(True)


def add_caption(ax: mpl.axes.Axes, letter: str) -> None:
    """Dedicated centered caption band under each panel."""
    ax.set_axis_off()
    ax.text(
        0.5,
        0.42,
        rf"$\bf{{({letter})}}$  {PANEL_TITLES[letter]}",
        ha="center",
        va="center",
        fontsize=6.45,
        color=TEXT,
        transform=ax.transAxes,
    )


def binned_medians(x: np.ndarray, y: np.ndarray, bins: int = 12) -> tuple[np.ndarray, np.ndarray]:
    edges = np.linspace(float(x.min()), float(x.max()), bins + 1)
    membership = np.clip(np.digitize(x, edges) - 1, 0, bins - 1)
    centers_x, centers_y = [], []
    for index in range(bins):
        mask = membership == index
        if np.any(mask):
            centers_x.append(float(np.median(x[mask])))
            centers_y.append(float(np.median(y[mask])))
    return np.asarray(centers_x), np.asarray(centers_y)


def manifold_centers(representation: pd.DataFrame, bins: int = 14) -> tuple[np.ndarray, np.ndarray]:
    """Median PCA center in equal q bins; display-only, not a fitted model."""
    q = representation["q_true"].to_numpy(float)
    edges = np.linspace(float(q.min()), float(q.max()), bins + 1)
    membership = np.clip(np.digitize(q, edges) - 1, 0, bins - 1)
    points, values = [], []
    for index in range(bins):
        subset = representation.loc[membership == index]
        if not subset.empty:
            points.append([float(subset["PC1"].median()), float(subset["PC2"].median())])
            values.append(float(subset["q_true"].median()))
    return np.asarray(points), np.asarray(values)


def add_path_arrows(
    ax: mpl.axes.Axes,
    points: np.ndarray,
    values: np.ndarray,
    fractions: tuple[float, ...],
    step: int = 2,
) -> None:
    """Add sparse arrows along an existing ordered path."""
    for fraction in fractions:
        start = min(int(fraction * (len(points) - 1)), len(points) - step - 1)
        end = start + step
        ax.annotate(
            "",
            xy=points[end],
            xytext=points[start],
            arrowprops=dict(
                arrowstyle="->",
                color=LIFE_CMAP(mpl.colors.Normalize(0, 1)(values[start])),
                lw=0.75,
                mutation_scale=4.8,
                shrinkA=1.5,
                shrinkB=1.5,
            ),
            zorder=5,
        )


def build_figure(
    trajectory: pd.DataFrame,
    representation: pd.DataFrame,
    explained: np.ndarray,
) -> tuple[mpl.figure.Figure, dict[str, object]]:
    q_true = trajectory["q_true"].to_numpy(float)
    q_hat = trajectory["q_pred"].to_numpy(float)
    r2 = float(1.0 - np.sum((q_true - q_hat) ** 2) / np.sum((q_true - q_true.mean()) ** 2))
    rho = float(spearmanr(q_true, q_hat).statistic)
    mae = float(np.mean(np.abs(q_true - q_hat)))
    agreement = float((trajectory["true_stage"] == trajectory["pred_stage"]).mean())
    bands = stage_bands(trajectory)

    fig = plt.figure(figsize=(7.20, 6.15))
    outer = fig.add_gridspec(
        2,
        1,
        height_ratios=[1.04, 0.91],
        left=0.070,
        right=0.970,
        top=0.975,
        bottom=0.045,
        hspace=0.10,
    )
    top = outer[0].subgridspec(
        2,
        3,
        height_ratios=[1.0, 0.155],
        width_ratios=[1.0, 1.20, 1.0],
        hspace=0.30,
        wspace=0.46,
    )
    bottom = outer[1].subgridspec(
        2,
        2,
        height_ratios=[1.0, 0.155],
        hspace=0.30,
        wspace=0.38,
    )

    # (a) Stage-aware probability evolution with audited true-stage zones.
    a_grid = top[0, 0].subgridspec(2, 1, height_ratios=[3.0, 0.95], hspace=0.08)
    ax_a = fig.add_subplot(a_grid[0, 0])
    ax_aq = fig.add_subplot(a_grid[1, 0], sharex=ax_a)
    caption_a = fig.add_subplot(top[1, 0])
    x_life = trajectory["relative_life"].to_numpy(float)
    add_stage_background(ax_a, bands)
    add_stage_background(ax_aq, bands)
    for column, label, stage in [
        ("prob_early", r"$p_E$", "early"),
        ("prob_middle", r"$p_M$", "middle"),
        ("prob_late", r"$p_L$", "late"),
    ]:
        ax_a.plot(
            x_life,
            trajectory[column],
            color=STAGE_COLORS[stage],
            label=label,
            lw=1.35,
            solid_capstyle="round",
        )
    for stage, _, _, center in bands:
        ax_a.text(
            center,
            0.965,
            f"{stage.title()} zone",
            transform=ax_a.get_xaxis_transform(),
            ha="center",
            va="top",
            fontsize=4.9,
            color=STAGE_COLORS[stage],
            alpha=0.82,
        )
    quiet_grid(ax_a)
    ax_a.set_ylabel("Probability")
    ax_a.set_ylim(-0.02, 1.02)
    ax_a.set_yticks([0.0, 0.5, 1.0])
    ax_a.tick_params(labelbottom=False)
    ax_a.legend(
        ncol=3,
        loc="upper center",
        bbox_to_anchor=(0.52, 1.03),
        handlelength=1.6,
        columnspacing=0.80,
        handletextpad=0.35,
        borderaxespad=0,
    )
    ax_aq.plot(x_life, q_hat, color="#333A3D", lw=1.05, solid_capstyle="round")
    ax_aq.fill_between(x_life, 0, q_hat, color="#9EA9AE", alpha=0.24, linewidth=0)
    ax_aq.set_ylim(-0.02, 1.02)
    ax_aq.set_yticks([0, 1])
    ax_aq.set_ylabel(r"$\hat q$", rotation=0, labelpad=7)
    ax_aq.set_xlabel("Relative life", labelpad=2)
    ax_aq.spines["top"].set_visible(False)
    add_caption(caption_a, "a")

    # (b) Hero panel: ordered simplex trajectory with sparse direction arrows.
    b_grid = top[0, 1].subgridspec(2, 1, height_ratios=[1.0, 0.085], hspace=0.02)
    ax_b = fig.add_subplot(b_grid[0, 0])
    cax_b = fig.add_subplot(b_grid[1, 0])
    caption_b = fig.add_subplot(top[1, 1])
    probability = trajectory[["prob_early", "prob_middle", "prob_late"]].to_numpy(float)
    simplex = ternary_xy(probability)
    triangle = np.array([[0, 0], [0.5, np.sqrt(3) / 2], [1, 0], [0, 0]])
    for fraction in [0.25, 0.50, 0.75]:
        ax_b.plot(
            [fraction, 0.5 + 0.5 * fraction],
            [0, np.sqrt(3) / 2 * (1 - fraction)],
            color=GRID,
            lw=0.43,
            zorder=0,
        )
        ax_b.plot(
            [1 - fraction, 0.5 * (1 - fraction)],
            [0, np.sqrt(3) / 2 * fraction],
            color=GRID,
            lw=0.43,
            zorder=0,
        )
        ax_b.plot(
            [0.5 * fraction, 1 - 0.5 * fraction],
            [np.sqrt(3) / 2 * fraction] * 2,
            color=GRID,
            lw=0.43,
            zorder=0,
        )
    ax_b.plot(triangle[:, 0], triangle[:, 1], color=SPINE, lw=0.85, zorder=1)
    segments = np.stack([simplex[:-1], simplex[1:]], axis=1)
    simplex_line = LineCollection(
        segments,
        cmap=LIFE_CMAP,
        norm=mpl.colors.Normalize(0, 1),
        linewidth=1.75,
        capstyle="round",
        joinstyle="round",
        zorder=2,
    )
    simplex_line.set_array(x_life[:-1])
    ax_b.add_collection(simplex_line)
    sample_indices = np.arange(0, len(simplex), 13)
    ax_b.scatter(
        simplex[sample_indices, 0],
        simplex[sample_indices, 1],
        c=x_life[sample_indices],
        cmap=LIFE_CMAP,
        vmin=0,
        vmax=1,
        s=11,
        edgecolor="white",
        linewidth=0.28,
        zorder=3,
    )
    add_path_arrows(ax_b, simplex, x_life, fractions=(0.20, 0.49, 0.76), step=5)
    ax_b.scatter(
        simplex[0, 0], simplex[0, 1], marker="o", s=38, facecolor="white",
        edgecolor=STAGE_COLORS["early"], linewidth=1.05, zorder=6
    )
    ax_b.scatter(
        simplex[-1, 0], simplex[-1, 1], marker="s", s=38, facecolor="#F2D7A0",
        edgecolor="#745421", linewidth=0.9, zorder=6
    )
    ax_b.annotate(
        "start", xy=simplex[0], xytext=(-4, 7), textcoords="offset points",
        ha="right", fontsize=5.3, color=MUTED
    )
    ax_b.annotate(
        "end", xy=simplex[-1], xytext=(5, 6), textcoords="offset points",
        ha="left", fontsize=5.3, color=MUTED
    )
    ax_b.text(-0.035, -0.025, "Early", ha="right", va="top", fontsize=6.2, fontweight="semibold")
    ax_b.text(1.035, -0.025, "Late", ha="left", va="top", fontsize=6.2, fontweight="semibold")
    ax_b.text(
        0.5, np.sqrt(3) / 2 + 0.025, "Middle",
        ha="center", va="bottom", fontsize=6.2, fontweight="semibold"
    )
    ax_b.set_xlim(-0.115, 1.115)
    ax_b.set_ylim(-0.095, np.sqrt(3) / 2 + 0.085)
    ax_b.set_aspect("equal")
    ax_b.set_axis_off()
    colorbar_b = fig.colorbar(simplex_line, cax=cax_b, orientation="horizontal")
    colorbar_b.set_ticks([0, 0.5, 1])
    colorbar_b.set_label("Relative life", fontsize=5.9, labelpad=1)
    colorbar_b.ax.tick_params(labelsize=5.4, width=0.5, length=2, pad=1)
    colorbar_b.outline.set_linewidth(0.55)
    colorbar_b.outline.set_edgecolor(SPINE)
    add_caption(caption_b, "b")

    # (c) Raw q agreement with identity reference and display-only binned medians.
    ax_c = fig.add_subplot(top[0, 2])
    caption_c = fig.add_subplot(top[1, 2])
    density = ax_c.hexbin(
        q_true,
        q_hat,
        gridsize=23,
        mincnt=1,
        bins="log",
        cmap=DENSITY_CMAP,
        linewidths=0.14,
        edgecolors="white",
    )
    low = float(min(q_true.min(), q_hat.min()))
    high = float(max(q_true.max(), q_hat.max()))
    ax_c.plot([low, high], [low, high], ls=(0, (3, 2)), color="#646C70", lw=0.85)
    median_x, median_y = binned_medians(q_true, q_hat, bins=12)
    ax_c.plot(median_x, median_y, color="white", lw=2.4, alpha=0.9, zorder=3)
    ax_c.plot(
        median_x,
        median_y,
        color=STAGE_COLORS["middle"],
        lw=1.0,
        marker="o",
        ms=2.2,
        markeredgecolor="white",
        markeredgewidth=0.35,
        zorder=4,
        label="Binned median",
    )
    margin = 0.035
    ax_c.set_xlim(low - margin, high + margin)
    ax_c.set_ylim(low - margin, high + margin)
    ax_c.set_xlabel(r"$q_{true}$", labelpad=2)
    ax_c.set_ylabel(r"$\hat q$")
    ax_c.set_aspect("equal", adjustable="box")
    quiet_grid(ax_c)
    ax_c.text(
        0.04,
        0.96,
        rf"$R^2$ = {r2:.3f}" + "\n" + rf"Spearman $\rho$ = {rho:.3f}" + "\n"
        + f"MAE = {mae:.3f}\n" + rf"$n$ = {len(trajectory)}",
        transform=ax_c.transAxes,
        ha="left",
        va="top",
        fontsize=5.55,
        linespacing=1.15,
        bbox=dict(
            boxstyle="round,pad=0.23",
            facecolor="white",
            edgecolor="#BDC5C9",
            linewidth=0.55,
            alpha=0.95,
        ),
    )
    ax_c.legend(loc="lower right", handlelength=1.4, borderaxespad=0.25, fontsize=5.1)
    cax_c = inset_axes(
        ax_c,
        width="4.0%",
        height="72%",
        loc="lower left",
        bbox_to_anchor=(1.045, 0.14, 1, 1),
        bbox_transform=ax_c.transAxes,
        borderpad=0,
    )
    colorbar_c = fig.colorbar(density, cax=cax_c)
    colorbar_c.set_label("Run density", fontsize=5.8, labelpad=2)
    colorbar_c.ax.tick_params(labelsize=5.3, width=0.5, length=2, pad=1)
    colorbar_c.outline.set_linewidth(0.55)
    add_caption(caption_c, "c")

    # (d) Saved 64D hidden representations with a q-binned median center path.
    ax_d = fig.add_subplot(bottom[0, 0])
    caption_d = fig.add_subplot(bottom[1, 0])
    q_norm = mpl.colors.Normalize(representation["q_true"].min(), representation["q_true"].max())
    center_points, center_q = manifold_centers(representation, bins=18)
    ax_d.plot(
        center_points[:, 0], center_points[:, 1],
        color="white", lw=1.8, alpha=0.80, zorder=1, solid_capstyle="round"
    )
    ax_d.plot(
        center_points[:, 0], center_points[:, 1],
        color=MUTED, lw=0.72, ls=(0, (2.2, 1.7)), alpha=0.68,
        zorder=2, solid_capstyle="round"
    )
    ax_d.scatter(
        center_points[:, 0], center_points[:, 1], c=center_q, cmap=LIFE_CMAP,
        norm=q_norm, s=9, edgecolor="white", linewidth=0.38, zorder=3
    )
    add_path_arrows(ax_d, center_points, center_q, fractions=(0.30, 0.68), step=1)
    for stage in STAGES:
        subset = representation[representation["true_stage"] == stage]
        ax_d.scatter(
            subset["PC1"],
            subset["PC2"],
            c=subset["q_true"],
            cmap=LIFE_CMAP,
            norm=q_norm,
            marker=STAGE_MARKERS[stage],
            s=16,
            alpha=0.72,
            edgecolor="white",
            linewidth=0.27,
            zorder=4,
        )
    ax_d.set_xlabel(f"PC1 ({100 * explained[0]:.1f}% var.)", labelpad=2)
    ax_d.set_ylabel(f"PC2 ({100 * explained[1]:.1f}% var.)")
    quiet_grid(ax_d)
    legend_handles = [
        Line2D(
            [0], [0], marker=STAGE_MARKERS[stage], linestyle="none", markersize=4.4,
            markerfacecolor=STAGE_COLORS[stage], markeredgecolor="white", markeredgewidth=0.4,
            label=label,
        )
        for stage, label in zip(STAGES, STAGE_LABELS)
    ]
    ax_d.legend(
        handles=legend_handles,
        ncol=3,
        loc="upper center",
        bbox_to_anchor=(0.52, 1.01),
        handletextpad=0.25,
        columnspacing=0.8,
        borderaxespad=0,
    )
    cax_d = inset_axes(
        ax_d,
        width="2.8%",
        height="70%",
        loc="lower left",
        bbox_to_anchor=(1.02, 0.15, 1, 1),
        bbox_transform=ax_d.transAxes,
        borderpad=0,
    )
    scalar = mpl.cm.ScalarMappable(norm=q_norm, cmap=LIFE_CMAP)
    colorbar_d = fig.colorbar(scalar, cax=cax_d)
    colorbar_d.ax.set_title(r"$q$", fontsize=6.0, pad=2)
    colorbar_d.ax.tick_params(labelsize=5.4, width=0.5, length=2, pad=1)
    colorbar_d.outline.set_linewidth(0.55)
    add_caption(caption_d, "d")

    # (e) Half-violin raincloud: distribution left, box center, all raw points right.
    ax_e = fig.add_subplot(bottom[0, 1])
    caption_e = fig.add_subplot(bottom[1, 1])
    groups = [
        trajectory.loc[trajectory["pred_stage"] == stage, "VB_true"].to_numpy(float)
        for stage in STAGES
    ]
    if any(len(group) == 0 for group in groups):
        raise ValueError("A predicted-stage wear group is empty")
    positions = np.array([1.0, 2.0, 3.0])
    raincloud = ax_e.violinplot(
        groups,
        positions=positions,
        widths=0.72,
        showmeans=False,
        showmedians=False,
        showextrema=False,
        bw_method=0.28,
    )
    for body, position, stage in zip(raincloud["bodies"], positions, STAGES):
        vertices = body.get_paths()[0].vertices
        vertices[:, 0] = np.minimum(vertices[:, 0], position)
        body.set_facecolor(STAGE_COLORS[stage])
        body.set_edgecolor(STAGE_COLORS[stage])
        body.set_linewidth(0.55)
        body.set_alpha(0.24)
    boxes = ax_e.boxplot(
        groups,
        positions=positions,
        widths=0.16,
        patch_artist=True,
        showfliers=False,
        medianprops=dict(color=TEXT, linewidth=1.05),
        whiskerprops=dict(color="#596166", linewidth=0.72),
        capprops=dict(color="#596166", linewidth=0.72),
    )
    for patch, stage in zip(boxes["boxes"], STAGES):
        patch.set_facecolor("white")
        patch.set_edgecolor(STAGE_COLORS[stage])
        patch.set_linewidth(0.9)
        patch.set_alpha(0.95)
    rng = np.random.default_rng(20260821)
    for position, stage, values in zip(positions, STAGES, groups):
        jitter = rng.uniform(0.045, 0.225, len(values))
        ax_e.scatter(
            position + jitter,
            values,
            s=6.7,
            color=STAGE_COLORS[stage],
            alpha=0.38,
            edgecolor="white",
            linewidth=0.16,
            zorder=3,
        )
    medians = [float(np.median(group)) for group in groups]
    ax_e.plot(
        positions,
        medians,
        color="#8A9397",
        lw=0.65,
        ls=(0, (2, 2)),
        marker="o",
        ms=2.8,
        markerfacecolor="white",
        markeredgecolor="#6C7478",
        markeredgewidth=0.55,
        zorder=1,
    )
    ax_e.set_xticks(positions, STAGE_LABELS)
    ax_e.set_xlabel("Predicted degradation state", labelpad=2)
    ax_e.set_ylabel("True flank wear, VB")
    ax_e.set_xlim(0.55, 3.45)
    quiet_grid(ax_e)
    add_caption(caption_e, "e")

    metrics: dict[str, object] = {
        "n": int(len(trajectory)),
        "R2": r2,
        "Spearman_rho": rho,
        "MAE": mae,
        "stage_agreement": agreement,
        "stage_boundaries_relative_life": [
            {"stage": stage, "left": left, "right": right}
            for stage, left, right, _ in bands
        ],
        "predicted_stage_counts": dict(zip(STAGE_LABELS, [int(len(group)) for group in groups])),
        "predicted_stage_median_VB": dict(zip(STAGE_LABELS, medians)),
        "PCA_explained_variance": explained.tolist(),
        "q_agreement_binned_median_points": int(len(median_x)),
        "PCA_center_path_points": int(len(center_points)),
    }
    return fig, metrics


def write_manifest(metrics: dict[str, object]) -> Path:
    trajectory_path = absolute(TRAJECTORY_SOURCE)
    representation_path = absolute(REPRESENTATION_SOURCE)
    audit_path = absolute(AUDIT_SOURCE)
    reference_path = absolute(REFERENCE_SCRIPT)
    manifest = {
        "figure": "Figure 5 — degradation-semantic consistency",
        "audit_status": "PASSED_AUTHORITATIVE_VISUAL_REFINEMENT_ONLY",
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "script": {
            "path": str(Path(__file__).resolve().relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "version": SCRIPT_VERSION,
            "backend": "Python/matplotlib",
        },
        "authority_basis": {
            "path": str(AUDIT_SOURCE).replace("\\", "/"),
            "sha256": file_sha256(audit_path),
            "reason": (
                "The project figure audit explicitly designates the full C6 trajectory for panels "
                "a,b,c,e and saved test_C6/C6 hidden representations for panel d."
            ),
        },
        "sources": {
            "lifecycle_trajectory": {
                "path": str(TRAJECTORY_SOURCE).replace("\\", "/"),
                "sha256": file_sha256(trajectory_path),
                "authoritative": True,
                "rows_used": int(metrics["n"]),
                "panels": ["a", "b", "c", "e"],
                "filter": "full C6 lifecycle; no row selection",
            },
            "hidden_representation": {
                "path": str(REPRESENTATION_SOURCE).replace("\\", "/"),
                "sha256": file_sha256(representation_path),
                "authoritative": True,
                "rows_used": int(metrics["n"]),
                "panels": ["d"],
                "filter": "split=test_C6 and condition=C6",
            },
        },
        "panel_map": {
            "a": {
                "source": "lifecycle_trajectory",
                "display": "raw stage probabilities and q_pred over min-max normalized run_id",
                "visual_derivation": "true_stage contiguous spans provide pale background zones",
            },
            "b": {
                "source": "lifecycle_trajectory",
                "display": "standard ternary barycentric mapping ordered by relative life",
                "visual_derivation": "arrows follow existing ordered trajectory; no interpolation model",
            },
            "c": {
                "source": "lifecycle_trajectory",
                "display": "log-count hexbin of all q_true/q_pred pairs plus y=x",
                "visual_derivation": "12 equal-width q_true bins summarized by medians",
            },
            "d": {
                "source": "hidden_representation",
                "display": "feature-wise standardization and deterministic two-component NumPy SVD PCA",
                "visual_derivation": "18 equal-width q_true bins summarized by median PCA centers",
            },
            "e": {
                "source": "lifecycle_trajectory",
                "display": "VB_true grouped by pred_stage as half-violin, boxplot, and every raw point",
                "visual_derivation": "deterministic jitter only; no observation removed",
            },
        },
        "reference_script": {
            "path": str(REFERENCE_SCRIPT).replace("\\", "/"),
            "sha256": file_sha256(reference_path),
            "role": "scientific logic and calculation reference",
        },
        "metrics": metrics,
        "integrity": {
            "model_retrained": False,
            "experiment_protocol_changed": False,
            "synthetic_data_used": False,
            "observations_removed_for_display": False,
            "statistics_redefined": False,
        },
    }
    path = OUT_DIR / "data_manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def export_figure(fig: mpl.figure.Figure) -> list[Path]:
    outputs = []
    for suffix in ["svg", "pdf", "png"]:
        target = OUTPUT_STEM.with_suffix(f".{suffix}")
        kwargs: dict[str, object] = {"bbox_inches": "tight", "pad_inches": 0.035}
        if suffix == "png":
            kwargs.update(
                dpi=600,
                metadata={
                    "Software": "Python/matplotlib",
                    "Description": "Audited refined Figure 5; 600 dpi review preview",
                },
            )
        fig.savefig(target, **kwargs)
        outputs.append(target)
    plt.close(fig)
    return outputs


def main() -> list[Path]:
    apply_style()
    trajectory, representation, explained = load_audited_data()
    figure, metrics = build_figure(trajectory, representation, explained)
    write_manifest(metrics)
    return export_figure(figure)


if __name__ == "__main__":
    for output in main():
        print(output.relative_to(PROJECT_ROOT))
