"""Refined Figure 5: degradation-semantic consistency across five views.

The script uses the same C6 lifecycle and saved hidden-representation sources as
the existing Figure 5. It changes only visual layout and styling.

Run from the project root:
    C:\\Users\\banghai\\miniconda3\\python.exe \
        figures\\fig5_semantics_refined\\plot_fig5_semantics_refined.py
"""

from __future__ import annotations

import hashlib
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


# Mandatory publication/export settings: SVG text remains editable and PDF uses
# embedded TrueType fonts.
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Liberation Sans"]
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["pdf.fonttype"] = 42

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = Path(__file__).resolve().parent
OUTPUT_STEM = OUT_DIR / "fig5_semantics_refined"

TRAJ_SOURCE = Path(
    "补充材料/小论文/9_probability_wear_consistency_analysis/"
    "Data_5_4_A6_probability_wear_trajectory.csv"
)
REPR_SOURCE = Path(
    "补充材料/小论文/10_第五章顶刊风格可视化/"
    "figures_representation_space/repr_hidden_hct.csv"
)

STAGES = ["early", "middle", "late"]
STAGE_LABELS = ["Early", "Middle", "Late"]
STAGE_COLORS = {
    "early": "#284F70",   # restrained deep blue
    "middle": "#2C887F",  # muted teal
    "late": "#D5952F",    # warm amber
}
STAGE_MARKERS = {"early": "o", "middle": "^", "late": "s"}
TEXT = "#252A2E"
MUTED = "#69737A"
GRID = "#E8ECEE"
SPINE = "#4D555A"
LIFE_CMAP = LinearSegmentedColormap.from_list(
    "semantic_life", [STAGE_COLORS["early"], STAGE_COLORS["middle"], "#F1D7A1"]
)
DENSITY_CMAP = LinearSegmentedColormap.from_list(
    "semantic_density", ["#1D3E5A", "#287C7B", "#E9C77B"]
)


def apply_style() -> None:
    """Apply restrained journal-width styling."""
    mpl.rcParams.update(
        {
            "font.size": 7.0,
            "axes.labelsize": 7.2,
            "xtick.labelsize": 6.2,
            "ytick.labelsize": 6.2,
            "legend.fontsize": 6.0,
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
        raise FileNotFoundError(f"Required source data not found: {relative_path}")
    return path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pca_svd(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Match the existing deterministic standardized NumPy-SVD PCA."""
    x = matrix.astype(float)
    x -= x.mean(axis=0, keepdims=True)
    scale = x.std(axis=0, ddof=1, keepdims=True)
    scale[~np.isfinite(scale) | np.isclose(scale, 0)] = 1.0
    x /= scale
    u, s, _ = np.linalg.svd(x, full_matrices=False)
    scores = u[:, :2] * s[:2]
    explained = (s[:2] ** 2) / np.sum(s**2)
    return scores, explained


def ternary_xy(probabilities: np.ndarray) -> np.ndarray:
    """Map Early/Middle/Late probabilities to an equilateral simplex."""
    p_middle = probabilities[:, 1]
    p_late = probabilities[:, 2]
    return np.column_stack([p_late + 0.5 * p_middle, np.sqrt(3) / 2 * p_middle])


def quiet_y_grid(ax: mpl.axes.Axes) -> None:
    ax.grid(axis="y", color=GRID, linewidth=0.45, zorder=0)
    ax.set_axisbelow(True)


def make_caption(ax: mpl.axes.Axes, letter: str, title: str) -> None:
    """Create a dedicated, centered below-panel caption."""
    ax.set_axis_off()
    ax.text(
        0.5,
        0.42,
        rf"$\bf{{({letter})}}$  {title}",
        ha="center",
        va="center",
        fontsize=6.45,
        fontweight="normal",
        color=TEXT,
        transform=ax.transAxes,
    )


def validate_and_load() -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    traj = pd.read_csv(absolute(TRAJ_SOURCE)).sort_values("run_id").reset_index(drop=True)
    required_traj = {
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
    missing = required_traj.difference(traj.columns)
    if missing:
        raise ValueError(f"Lifecycle source is missing columns: {sorted(missing)}")
    numeric = [
        "run_id",
        "VB_true",
        "q_true",
        "q_pred",
        "prob_early",
        "prob_middle",
        "prob_late",
    ]
    traj[numeric] = traj[numeric].apply(pd.to_numeric, errors="raise")
    if traj[numeric].isna().any().any():
        raise ValueError("Lifecycle source contains missing numeric values")
    probability_sum = traj[["prob_early", "prob_middle", "prob_late"]].sum(axis=1)
    if not np.allclose(probability_sum, 1.0, atol=1e-5):
        raise ValueError("Stage probabilities do not sum to one within tolerance")
    traj["true_stage"] = traj["true_stage"].str.lower()
    traj["pred_stage"] = traj["pred_stage"].str.lower()
    life_denominator = traj["run_id"].max() - traj["run_id"].min()
    traj["relative_life"] = (traj["run_id"] - traj["run_id"].min()) / life_denominator

    repr_all = pd.read_csv(absolute(REPR_SOURCE))
    repr_test = repr_all[(repr_all["split"] == "test_C6") & (repr_all["condition"] == "C6")].copy()
    repr_test["true_stage"] = repr_test["true_stage"].str.lower()
    hidden_columns = [column for column in repr_test.columns if column.startswith("h_")]
    if len(hidden_columns) != 64:
        raise ValueError(f"Expected 64 hidden features, found {len(hidden_columns)}")
    hidden = repr_test[hidden_columns].apply(pd.to_numeric, errors="raise").to_numpy(float)
    if hidden.shape[0] != len(traj):
        raise ValueError(
            f"Lifecycle/representation row mismatch: {len(traj)} versus {hidden.shape[0]}"
        )
    scores, explained = pca_svd(hidden)
    repr_test["PC1"], repr_test["PC2"] = scores[:, 0], scores[:, 1]
    return traj, repr_test, explained


def add_vertical_stage_boundaries(ax: mpl.axes.Axes, traj: pd.DataFrame) -> None:
    stages = traj["true_stage"].to_numpy()
    x = traj["relative_life"].to_numpy(float)
    indices = np.flatnonzero(stages[1:] != stages[:-1])
    for idx in indices:
        boundary = 0.5 * (x[idx] + x[idx + 1])
        ax.axvline(boundary, color="#AEB7BC", lw=0.55, ls=(0, (2.0, 2.2)), zorder=0)


def build_figure(
    traj: pd.DataFrame, repr_test: pd.DataFrame, explained: np.ndarray
) -> tuple[mpl.figure.Figure, dict[str, float | list[float]]]:
    """Build a five-panel, publication-width composite."""
    q_true = traj["q_true"].to_numpy(float)
    q_hat = traj["q_pred"].to_numpy(float)
    r2 = float(1.0 - np.sum((q_true - q_hat) ** 2) / np.sum((q_true - q_true.mean()) ** 2))
    rho = float(spearmanr(q_true, q_hat).statistic)
    mae = float(np.mean(np.abs(q_true - q_hat)))
    stage_agreement = float((traj["true_stage"] == traj["pred_stage"]).mean())

    fig = plt.figure(figsize=(7.20, 6.20))  # 182.9 x 157.5 mm
    outer = fig.add_gridspec(
        2,
        1,
        height_ratios=[1.04, 0.90],
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
        width_ratios=[1.0, 1.14, 1.0],
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

    # (a) Full lifecycle probability trajectory and q-hat strip.
    a_grid = top[0, 0].subgridspec(2, 1, height_ratios=[3.0, 0.95], hspace=0.08)
    ax_a = fig.add_subplot(a_grid[0, 0])
    ax_aq = fig.add_subplot(a_grid[1, 0], sharex=ax_a)
    cap_a = fig.add_subplot(top[1, 0])
    x = traj["relative_life"].to_numpy(float)
    line_spec = [
        ("prob_early", r"$p_E$", STAGE_COLORS["early"]),
        ("prob_middle", r"$p_M$", STAGE_COLORS["middle"]),
        ("prob_late", r"$p_L$", STAGE_COLORS["late"]),
    ]
    for column, label, color in line_spec:
        ax_a.plot(x, traj[column], color=color, label=label, lw=1.35, solid_capstyle="round")
    add_vertical_stage_boundaries(ax_a, traj)
    add_vertical_stage_boundaries(ax_aq, traj)
    quiet_y_grid(ax_a)
    ax_a.set_ylabel("Probability")
    ax_a.set_ylim(-0.02, 1.02)
    ax_a.set_yticks([0.0, 0.5, 1.0])
    ax_a.tick_params(labelbottom=False)
    ax_a.legend(
        ncol=3,
        loc="upper center",
        bbox_to_anchor=(0.52, 1.02),
        handlelength=1.6,
        columnspacing=0.85,
        handletextpad=0.35,
        borderaxespad=0.0,
    )
    ax_aq.plot(x, q_hat, color="#343A3D", lw=1.05, solid_capstyle="round")
    ax_aq.fill_between(x, 0, q_hat, color="#B8C1C5", alpha=0.34, linewidth=0)
    ax_aq.set_ylim(-0.02, 1.02)
    ax_aq.set_yticks([0, 1])
    ax_aq.set_ylabel(r"$\hat q$", rotation=0, labelpad=7)
    ax_aq.set_xlabel("Relative life", labelpad=2.0)
    ax_aq.spines["top"].set_visible(False)
    ax_aq.spines["left"].set_color(SPINE)
    make_caption(cap_a, "a", "Full C6 lifecycle probability trajectory")

    # (b) Ordered ternary trajectory; slightly wider than neighboring panels.
    b_grid = top[0, 1].subgridspec(2, 1, height_ratios=[1.0, 0.085], hspace=0.02)
    ax_b = fig.add_subplot(b_grid[0, 0])
    cax_b = fig.add_subplot(b_grid[1, 0])
    cap_b = fig.add_subplot(top[1, 1])
    probability = traj[["prob_early", "prob_middle", "prob_late"]].to_numpy(float)
    xy = ternary_xy(probability)
    triangle = np.array([[0, 0], [0.5, np.sqrt(3) / 2], [1, 0], [0, 0]])
    for fraction in [0.25, 0.50, 0.75]:
        ax_b.plot(
            [fraction, 0.5 + 0.5 * fraction],
            [0, np.sqrt(3) / 2 * (1 - fraction)],
            color=GRID,
            lw=0.45,
            zorder=0,
        )
        ax_b.plot(
            [1 - fraction, 0.5 * (1 - fraction)],
            [0, np.sqrt(3) / 2 * fraction],
            color=GRID,
            lw=0.45,
            zorder=0,
        )
        ax_b.plot(
            [0.5 * fraction, 1 - 0.5 * fraction],
            [np.sqrt(3) / 2 * fraction] * 2,
            color=GRID,
            lw=0.45,
            zorder=0,
        )
    ax_b.plot(triangle[:, 0], triangle[:, 1], color=SPINE, lw=0.85, zorder=1)
    segments = np.stack([xy[:-1], xy[1:]], axis=1)
    trajectory = LineCollection(
        segments,
        cmap=LIFE_CMAP,
        norm=mpl.colors.Normalize(0, 1),
        linewidth=1.65,
        capstyle="round",
        joinstyle="round",
        zorder=2,
    )
    trajectory.set_array(x[:-1])
    ax_b.add_collection(trajectory)
    sample_idx = np.arange(0, len(xy), 13)
    ax_b.scatter(
        xy[sample_idx, 0],
        xy[sample_idx, 1],
        c=x[sample_idx],
        cmap=LIFE_CMAP,
        vmin=0,
        vmax=1,
        s=11,
        edgecolor="white",
        linewidth=0.28,
        zorder=3,
    )
    ax_b.scatter(
        xy[0, 0], xy[0, 1], marker="o", s=35, facecolor="white",
        edgecolor=STAGE_COLORS["early"], linewidth=1.0, zorder=4
    )
    ax_b.scatter(
        xy[-1, 0], xy[-1, 1], marker="s", s=35, facecolor="#F2D8A1",
        edgecolor="#725525", linewidth=0.9, zorder=4
    )
    ax_b.annotate(
        "start", xy=xy[0], xytext=(-4, 7), textcoords="offset points",
        ha="right", fontsize=5.4, color=MUTED
    )
    ax_b.annotate(
        "end", xy=xy[-1], xytext=(5, 6), textcoords="offset points",
        ha="left", fontsize=5.4, color=MUTED
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
    cb_b = fig.colorbar(trajectory, cax=cax_b, orientation="horizontal")
    cb_b.set_ticks([0, 0.5, 1])
    cb_b.set_label("Relative life", fontsize=5.9, labelpad=1.0)
    cb_b.ax.tick_params(labelsize=5.4, width=0.5, length=2, pad=1)
    cb_b.outline.set_linewidth(0.55)
    cb_b.outline.set_edgecolor(SPINE)
    make_caption(cap_b, "b", "Ordered trajectory in probability simplex")

    # (c) Continuous degradation-position agreement.
    ax_c = fig.add_subplot(top[0, 2])
    cap_c = fig.add_subplot(top[1, 2])
    hb = ax_c.hexbin(
        q_true,
        q_hat,
        gridsize=22,
        mincnt=1,
        bins="log",
        cmap=DENSITY_CMAP,
        linewidths=0.15,
        edgecolors="white",
    )
    low = float(min(q_true.min(), q_hat.min()))
    high = float(max(q_true.max(), q_hat.max()))
    margin = 0.035
    ax_c.plot([low, high], [low, high], ls=(0, (3, 2)), color="#62696D", lw=0.85, zorder=2)
    ax_c.set_xlim(low - margin, high + margin)
    ax_c.set_ylim(low - margin, high + margin)
    ax_c.set_xlabel(r"$q_{true}$", labelpad=2)
    ax_c.set_ylabel(r"$\hat q$")
    ax_c.set_aspect("equal", adjustable="box")
    quiet_y_grid(ax_c)
    ax_c.text(
        0.04,
        0.96,
        rf"$R^2$ = {r2:.3f}" + "\n" + rf"Spearman $\rho$ = {rho:.3f}" + "\n" +
        f"MAE = {mae:.3f}\n" + rf"$n$ = {len(traj)}",
        transform=ax_c.transAxes,
        ha="left",
        va="top",
        fontsize=5.65,
        linespacing=1.15,
        bbox=dict(
            boxstyle="round,pad=0.24",
            facecolor="white",
            edgecolor="#BDC5C9",
            linewidth=0.55,
            alpha=0.95,
        ),
    )
    cax_c = inset_axes(
        ax_c,
        width="4.0%",
        height="72%",
        loc="lower left",
        bbox_to_anchor=(1.045, 0.14, 1, 1),
        bbox_transform=ax_c.transAxes,
        borderpad=0,
    )
    cb_c = fig.colorbar(hb, cax=cax_c)
    cb_c.set_label("Run density", fontsize=5.8, labelpad=2)
    cb_c.ax.tick_params(labelsize=5.3, width=0.5, length=2, pad=1)
    cb_c.outline.set_linewidth(0.55)
    make_caption(cap_c, "c", "Continuous degradation-position agreement")

    # (d) Shared hidden-space manifold, same deterministic PCA as the original.
    ax_d = fig.add_subplot(bottom[0, 0])
    cap_d = fig.add_subplot(bottom[1, 0])
    q_norm = mpl.colors.Normalize(repr_test["q_true"].min(), repr_test["q_true"].max())
    for stage in STAGES:
        subset = repr_test[repr_test["true_stage"] == stage]
        ax_d.scatter(
            subset["PC1"],
            subset["PC2"],
            c=subset["q_true"],
            cmap=LIFE_CMAP,
            norm=q_norm,
            marker=STAGE_MARKERS[stage],
            s=17,
            alpha=0.82,
            edgecolor="white",
            linewidth=0.28,
            rasterized=False,
        )
    ax_d.set_xlabel(f"PC1 ({100 * explained[0]:.1f}% var.)", labelpad=2)
    ax_d.set_ylabel(f"PC2 ({100 * explained[1]:.1f}% var.)")
    quiet_y_grid(ax_d)
    legend_handles = [
        Line2D(
            [0], [0], marker=STAGE_MARKERS[stage], linestyle="none", markersize=4.5,
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
    cb_d = fig.colorbar(scalar, cax=cax_d)
    cb_d.ax.set_title(r"$q$", fontsize=6.0, pad=2)
    cb_d.ax.tick_params(labelsize=5.4, width=0.5, length=2, pad=1)
    cb_d.outline.set_linewidth(0.55)
    make_caption(cap_d, "d", "Shared latent degradation manifold")

    # (e) Physical-wear semantics: violin + boxplot + every raw observation.
    ax_e = fig.add_subplot(bottom[0, 1])
    cap_e = fig.add_subplot(bottom[1, 1])
    groups = [
        traj.loc[traj["pred_stage"] == stage, "VB_true"].to_numpy(float)
        for stage in STAGES
    ]
    if any(len(group) == 0 for group in groups):
        raise ValueError("At least one predicted-stage wear group is empty")
    violin = ax_e.violinplot(
        groups,
        positions=[1, 2, 3],
        widths=0.74,
        showmeans=False,
        showmedians=False,
        showextrema=False,
        bw_method=0.28,
    )
    for body, stage in zip(violin["bodies"], STAGES):
        body.set_facecolor(STAGE_COLORS[stage])
        body.set_edgecolor(STAGE_COLORS[stage])
        body.set_linewidth(0.55)
        body.set_alpha(0.24)
    boxes = ax_e.boxplot(
        groups,
        positions=[1, 2, 3],
        widths=0.23,
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
    for position, stage, values in zip([1, 2, 3], STAGES, groups):
        jitter = rng.uniform(-0.14, 0.14, len(values))
        ax_e.scatter(
            position + jitter,
            values,
            s=7.0,
            color=STAGE_COLORS[stage],
            alpha=0.38,
            edgecolor="white",
            linewidth=0.18,
            zorder=2,
        )
    ax_e.set_xticks([1, 2, 3], STAGE_LABELS)
    ax_e.set_xlabel("Predicted degradation state", labelpad=2)
    ax_e.set_ylabel("True flank wear, VB")
    ax_e.set_xlim(0.55, 3.45)
    quiet_y_grid(ax_e)
    make_caption(cap_e, "e", "Physical wear semantics")

    metrics: dict[str, float | list[float]] = {
        "n": float(len(traj)),
        "R2": r2,
        "Spearman_rho": rho,
        "MAE": mae,
        "stage_agreement": stage_agreement,
        "PCA_explained_variance": explained.tolist(),
        "predicted_stage_counts": [float(len(group)) for group in groups],
        "predicted_stage_median_VB": [float(np.median(group)) for group in groups],
    }
    return fig, metrics


def write_manifest(
    traj: pd.DataFrame,
    repr_test: pd.DataFrame,
    metrics: dict[str, float | list[float]],
) -> None:
    trajectory_path = absolute(TRAJ_SOURCE)
    representation_path = absolute(REPR_SOURCE)
    counts = [int(value) for value in metrics["predicted_stage_counts"]]  # type: ignore[index]
    medians = metrics["predicted_stage_median_VB"]  # type: ignore[assignment]
    explained = metrics["PCA_explained_variance"]  # type: ignore[assignment]
    content = f"""# Figure 5 refined — data manifest

## Source data

| Panel(s) | Project-relative source | Rows used | Variables / operation | SHA-256 |
|---|---|---:|---|---|
| (a), (b), (c), (e) | `{TRAJ_SOURCE.as_posix()}` | {len(traj)} | `run_id`, `VB_true`, `q_true`, `q_pred`, stage labels, and Early/Middle/Late probabilities | `{sha256(trajectory_path)}` |
| (d) | `{REPR_SOURCE.as_posix()}` | {len(repr_test)} (`split=test_C6`, `condition=C6`) | `h_00`–`h_63`, standardized feature-wise; two-component deterministic NumPy SVD PCA | `{sha256(representation_path)}` |

No synthetic observations, fitted smoothing, retraining, label-guided embedding, or manual point deletion are used.

## Recomputed audit values

- Lifecycle observations: **{int(metrics['n'])}**
- $R^2$: **{metrics['R2']:.12f}**
- Spearman $\\rho$: **{metrics['Spearman_rho']:.12f}**
- MAE: **{metrics['MAE']:.12f}**
- Stage agreement: **{100 * metrics['stage_agreement']:.4f}%**
- Predicted-stage counts (Early / Middle / Late): **{counts[0]} / {counts[1]} / {counts[2]}**
- Median true VB (Early / Middle / Late): **{medians[0]:.6f} / {medians[1]:.6f} / {medians[2]:.6f}**
- PCA explained variance (PC1 / PC2): **{100 * explained[0]:.4f}% / {100 * explained[1]:.4f}%**

## Display transformations

- Relative life is min–max normalized from `run_id` only for the horizontal lifecycle coordinate.
- Panel (b) applies the standard barycentric-to-Cartesian mapping to the three probabilities.
- Panel (c) uses logarithmic hex-bin counts for display; the statistics are calculated from all raw pairs.
- Panel (d) standardizes each saved hidden feature before deterministic SVD PCA, exactly as in the existing Figure 5 workflow.
- Panel (e) groups unmodified `VB_true` by `pred_stage` and displays every observation with deterministic jitter.
"""
    (OUT_DIR / "data_manifest.md").write_text(content, encoding="utf-8")


def export(fig: mpl.figure.Figure) -> list[Path]:
    outputs: list[Path] = []
    for suffix in ["svg", "pdf", "png"]:
        target = OUTPUT_STEM.with_suffix(f".{suffix}")
        kwargs: dict[str, object] = {"bbox_inches": "tight", "pad_inches": 0.035}
        if suffix == "png":
            kwargs.update(
                dpi=600,
                metadata={
                    "Software": "Python/matplotlib",
                    "Description": "Refined Figure 5; 600 dpi publication preview",
                },
            )
        fig.savefig(target, **kwargs)
        outputs.append(target)
    plt.close(fig)
    return outputs


def main() -> list[Path]:
    apply_style()
    traj, repr_test, explained = validate_and_load()
    fig, metrics = build_figure(traj, repr_test, explained)
    write_manifest(traj, repr_test, metrics)
    return export(fig)


if __name__ == "__main__":
    for output in main():
        print(output.relative_to(PROJECT_ROOT))
