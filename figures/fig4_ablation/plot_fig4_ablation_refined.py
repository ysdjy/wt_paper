"""Refined, publication-ready rendering of the audited Fig. 4 ablation grid.

Data provenance is frozen. Panels (a) and (c) use AUTHORITATIVE_A1_A6.csv,
with the audited M-Precision completion from ABLATION_RECOMPUTED.csv. Panels
(b) and (d) use the inference-only lifecycle exports validated by
plot_fig4_ablation_v2.load_and_validate_data(). No fitting or training occurs.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import plot_fig4_ablation_v2 as base


OUT_DIR = Path(__file__).resolve().parent
OUTPUT_BASE = OUT_DIR / "fig4_ablation_refined"
NOTES_PATH = OUT_DIR / "FIG4_REFINEMENT_NOTES.md"
MANIFEST_PATH = OUT_DIR / "data_manifest.json"

METHODS = base.METHODS
METHOD_COLORS = base.METHOD_COLORS
METHOD_MARKERS = base.METHOD_MARKERS
COLORS = base.COLORS


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def apply_style() -> None:
    """Apply one restrained typographic and line-weight system to all panels."""
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "font.size": 7.0,
            "axes.labelsize": 7.15,
            "xtick.labelsize": 6.45,
            "ytick.labelsize": 6.25,
            "legend.fontsize": 5.75,
            "axes.linewidth": 0.72,
            "axes.edgecolor": COLORS["slate"],
            "axes.spines.top": False,
            "axes.spines.right": False,
            "xtick.major.width": 0.60,
            "ytick.major.width": 0.60,
            "xtick.major.size": 2.6,
            "ytick.major.size": 2.6,
            "legend.frameon": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "pdf.fonttype": 42,
            "svg.fonttype": "none",
        }
    )


def highlight_a5_a6(ax: mpl.axes.Axes) -> None:
    """Subordinate A5/A6 background bands to the data marks."""
    ax.axvspan(3.52, 4.48, color=COLORS["a5_bg"], alpha=0.58, zorder=-5)
    ax.axvspan(4.52, 5.48, color=COLORS["a6_bg"], alpha=0.58, zorder=-5)
    ax.axvline(3.5, color=COLORS["grey"], linewidth=0.52, linestyle=(0, (2, 2)), zorder=-3)


def below_title(ax: mpl.axes.Axes, label: str, title: str) -> None:
    ax.text(
        0.5,
        -0.195,
        rf"$\bf{{({label})}}$ {title}",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=7.35,
        color=COLORS["text"],
    )


def combined_legend(ax: mpl.axes.Axes, right: mpl.axes.Axes) -> None:
    left_handles, left_labels = ax.get_legend_handles_labels()
    right_handles, right_labels = right.get_legend_handles_labels()
    ax.legend(
        left_handles + right_handles,
        left_labels + right_labels,
        loc="upper left",
        ncol=4,
        handlelength=1.40,
        columnspacing=0.66,
        handletextpad=0.34,
        borderaxespad=0.12,
    )


def annotate_series_points(
    ax: mpl.axes.Axes,
    x: np.ndarray,
    values: pd.Series | np.ndarray,
    color: str,
    offsets: list[int],
    decimals: int,
    bold_indices: set[int] | None = None,
) -> None:
    bold_indices = bold_indices or set()
    for index, (x_value, value) in enumerate(zip(x, np.asarray(values, dtype=float))):
        ax.annotate(
            f"{value:.{decimals}f}",
            xy=(x_value, value),
            xytext=(0, offsets[index]),
            textcoords="offset points",
            ha="center",
            va="bottom" if offsets[index] >= 0 else "top",
            fontsize=4.55 if index not in bold_indices else 4.85,
            fontweight="bold" if index in bold_indices else "normal",
            color=color,
            bbox=dict(facecolor="white", edgecolor="none", alpha=0.72, pad=0.14),
            zorder=9,
            annotation_clip=True,
        )


def draw_panel_a(ax: mpl.axes.Axes, summary: pd.DataFrame) -> None:
    x = np.arange(6, dtype=float)
    highlight_a5_a6(ax)
    width = 0.215
    baseline = 0.96
    for index, (metric, color) in enumerate(
        zip(["Acc", "Macro-F1", "M-F1"], [COLORS["navy"], COLORS["teal"], COLORS["cyan"]])
    ):
        bars = ax.bar(
            x + (index - 1) * width,
            summary[metric] - baseline,
            bottom=baseline,
            width=width * 0.90,
            color=color,
            edgecolor="white",
            linewidth=0.42,
            label=metric,
            zorder=2,
        )
        for method_index, method in [(4, "A5"), (5, "A6")]:
            bars[method_index].set_edgecolor(METHOD_COLORS[method])
            bars[method_index].set_linewidth(0.86)
    ax.set_ylim(0.96, 1.002)
    ax.set_yticks([0.96, 0.97, 0.98, 0.99, 1.00])
    ax.set_ylabel("Score (higher is better)")
    ax.set_xticks(x, METHODS)
    ax.set_xlim(-0.45, 5.45)
    base.style_axis(ax)

    right = ax.twinx()
    right.plot(
        x,
        summary["Smooth"],
        color=COLORS["gold"],
        marker="o",
        markersize=4.0,
        markerfacecolor="white",
        markeredgewidth=1.0,
        linewidth=1.42,
        label="Smooth ↓",
        zorder=5,
    )
    right.set_ylim(0.0110, 0.0257)
    right.set_yticks([0.012, 0.016, 0.020, 0.024])
    right.set_ylabel("Smooth (lower is better)")
    base.style_twin_axis(right, COLORS["gold"])
    annotate_series_points(
        right,
        x,
        summary["Smooth"],
        COLORS["gold"],
        offsets=[-8, 7, -8, 7, 7, -8],
        decimals=4,
        bold_indices={4, 5},
    )
    combined_legend(ax, right)
    right.annotate(
        "A5: strongest smoothing",
        xy=(4, summary.loc["A5", "Smooth"]),
        xytext=(3.48, 0.01215),
        ha="right",
        va="bottom",
        fontsize=5.25,
        color=METHOD_COLORS["A5"],
        fontweight="bold",
        arrowprops=dict(arrowstyle="-|>", color=METHOD_COLORS["A5"], lw=0.62, mutation_scale=6.5),
    )
    ax.annotate(
        "A6: accuracy restored",
        xy=(5 - width, summary.loc["A6", "Acc"]),
        xytext=(4.12, 0.9966),
        ha="left",
        va="top",
        fontsize=5.25,
        color=METHOD_COLORS["A6"],
        fontweight="bold",
        arrowprops=dict(arrowstyle="-|>", color=METHOD_COLORS["A6"], lw=0.62, mutation_scale=6.5),
    )
    below_title(ax, "a", "Overall predictive performance across A1–A6")


def vertical_method_legend(ax: mpl.axes.Axes, *, location: str) -> None:
    legend = ax.legend(
        loc=location,
        ncol=1,
        handlelength=1.48,
        handletextpad=0.42,
        labelspacing=0.34,
        borderaxespad=0.28,
        frameon=True,
        fancybox=False,
        framealpha=0.90,
        facecolor="white",
        edgecolor=COLORS["grid"],
    )
    legend.get_frame().set_linewidth(0.42)


def draw_panel_b(ax: mpl.axes.Axes, local: pd.DataFrame) -> None:
    for method in METHODS:
        frame = local[local["ID"].eq(method)].sort_values("run_id")
        x = frame["relative_tool_life"].to_numpy(float)
        raw = frame["local_variation_l1"].to_numpy(float)
        smooth = frame["local_variation_l1_smoothed"].to_numpy(float)
        color = METHOD_COLORS[method]
        ax.plot(x, raw, color=color, linewidth=0.45, alpha=0.12, zorder=1)
        ax.plot(
            x,
            smooth,
            color=color,
            linewidth=1.52 if method in {"A5", "A6"} else 1.05,
            marker=METHOD_MARKERS[method],
            markevery=52,
            markersize=2.7 if method in {"A5", "A6"} else 2.2,
            markerfacecolor="white",
            markeredgewidth=0.65,
            label=method,
            zorder=4 if method in {"A5", "A6"} else 3,
        )
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 0.70)
    ax.set_xticks(np.linspace(0, 1, 6))
    ax.set_yticks(np.arange(0, 0.7, 0.1))
    ax.set_xlabel("Relative tool life")
    ax.set_ylabel(r"Local probability variation  $\Delta_t$ (L1)")
    base.style_axis(ax)
    vertical_method_legend(ax, location="upper right")
    ax.text(
        0.46,
        0.965,
        "thin = raw   ·   dark = centered 11-run mean",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=5.05,
        color=COLORS["slate"],
        bbox=dict(facecolor="white", edgecolor=COLORS["grid"], linewidth=0.38, alpha=0.92, pad=1.25),
        zorder=10,
    )
    below_title(ax, "b", "Lifecycle-wise probability variation")


def draw_panel_c(ax: mpl.axes.Axes, summary: pd.DataFrame) -> None:
    x = np.arange(6, dtype=float)
    highlight_a5_a6(ax)
    width = 0.28
    baseline = 0.94
    for offset, metric, label, color in [
        (-width / 2, "M-Precision", "M-Pre", COLORS["teal"]),
        (width / 2, "M-Recall", "M-Rec", COLORS["blue"]),
    ]:
        bars = ax.bar(
            x + offset,
            summary[metric] - baseline,
            bottom=baseline,
            width=width * 0.90,
            color=color,
            edgecolor="white",
            linewidth=0.42,
            label=label,
            zorder=2,
        )
        for method_index, method in [(4, "A5"), (5, "A6")]:
            bars[method_index].set_edgecolor(METHOD_COLORS[method])
            bars[method_index].set_linewidth(0.85)
    ax.set_ylim(0.94, 1.005)
    ax.set_yticks([0.94, 0.96, 0.98, 1.00])
    ax.set_ylabel("Middle-stage score (higher is better)")
    ax.set_xticks(x, METHODS)
    ax.set_xlim(-0.45, 5.45)
    base.style_axis(ax)

    right = ax.twinx()
    for metric, label, color, marker in [
        ("M→E", "M→E ↓", COLORS["rust"], "D"),
        ("M→L", "M→L ↓", COLORS["slate"], "v"),
    ]:
        right.plot(
            x,
            summary[metric],
            color=color,
            marker=marker,
            markersize=3.7,
            markerfacecolor="white",
            markeredgewidth=0.92,
            linewidth=1.22,
            label=label,
            zorder=5,
        )
    right.set_ylim(-0.003, 0.0455)
    right.set_yticks([0.00, 0.01, 0.02, 0.03, 0.04])
    right.set_ylabel("Transition error rate (lower is better)")
    base.style_twin_axis(right, COLORS["rust"])
    annotate_series_points(
        right,
        x,
        summary["M→E"],
        COLORS["rust"],
        offsets=[7, -8, 7, -8, 7, -8],
        decimals=3,
        bold_indices={4, 5},
    )
    annotate_series_points(
        right,
        x,
        summary["M→L"],
        COLORS["slate"],
        offsets=[6, 6, 6, 6, 6, 6],
        decimals=3,
    )
    combined_legend(ax, right)
    ax.annotate(
        "A6 restores M-Rec",
        xy=(5 + width / 2, summary.loc["A6", "M-Recall"]),
        xytext=(4.00, 0.987),
        fontsize=5.25,
        color=METHOD_COLORS["A6"],
        fontweight="bold",
        arrowprops=dict(arrowstyle="-|>", color=METHOD_COLORS["A6"], lw=0.62, mutation_scale=6.5),
    )
    below_title(ax, "c", "Middle-stage and transition consistency")


def draw_panel_d(ax: mpl.axes.Axes, cumulative: pd.DataFrame) -> None:
    endpoints: dict[str, float] = {}
    for method in METHODS:
        frame = cumulative[cumulative["ID"].eq(method)].sort_values("run_id")
        x = frame["relative_tool_life"].to_numpy(float)
        y = frame["cumulative_variation_l1"].to_numpy(float)
        endpoints[method] = float(y[-1])
        ax.plot(
            x,
            y,
            color=METHOD_COLORS[method],
            linewidth=1.62 if method in {"A5", "A6"} else 1.08,
            marker=METHOD_MARKERS[method],
            markevery=52,
            markersize=2.8 if method in {"A5", "A6"} else 2.15,
            markerfacecolor="white",
            markeredgewidth=0.65,
            label=method,
            zorder=4 if method in {"A5", "A6"} else 3,
        )
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 7.85)
    ax.set_xticks(np.linspace(0, 1, 6))
    ax.set_yticks(np.arange(0, 8, 1))
    ax.set_xlabel("Relative tool life")
    ax.set_ylabel(r"Cumulative probability variation  $C_t$ (L1)")
    base.style_axis(ax)
    vertical_method_legend(ax, location="upper left")

    ax.text(
        0.33,
        0.965,
        r"terminal $C_t$/303 = Smooth",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=5.05,
        color=COLORS["slate"],
        bbox=dict(facecolor="white", edgecolor=COLORS["grid"], linewidth=0.38, alpha=0.92, pad=1.2),
        zorder=10,
    )
    ax.annotate(
        f"A5: lowest total variation ({endpoints['A5']:.2f})",
        xy=(0.88, endpoints["A5"]),
        xytext=(0.58, 2.85),
        fontsize=5.25,
        color=METHOD_COLORS["A5"],
        fontweight="bold",
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.84, pad=0.35),
        arrowprops=dict(arrowstyle="-|>", color=METHOD_COLORS["A5"], lw=0.62, mutation_scale=6.5),
        zorder=9,
    )
    ax.text(
        0.985,
        0.965,
        f"A6: balanced endpoint = {endpoints['A6']:.2f}",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=5.20,
        color=METHOD_COLORS["A6"],
        fontweight="bold",
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.88, pad=0.45),
        zorder=10,
    )
    below_title(ax, "d", "Trajectory stability diagnostics")


def make_figure(summary: pd.DataFrame, local: pd.DataFrame, cumulative: pd.DataFrame) -> plt.Figure:
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.75))
    draw_panel_a(axes[0, 0], summary)
    draw_panel_b(axes[0, 1], local)
    draw_panel_c(axes[1, 0], summary)
    draw_panel_d(axes[1, 1], cumulative)
    fig.subplots_adjust(left=0.085, right=0.925, top=0.978, bottom=0.105, wspace=0.37, hspace=0.56)
    return fig


def update_manifest(outputs: list[Path]) -> None:
    with MANIFEST_PATH.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    manifest["fig4_refined"] = {
        "audit_result": manifest.get("fig4_v2", {}).get("audit_result", "PASS_INFERENCE_ONLY"),
        "experiment_protocol_changed": False,
        "training_performed": False,
        "script": {"path": Path(__file__).name, "sha256": sha256(Path(__file__))},
        "refinement_notes": {"path": NOTES_PATH.name, "sha256": sha256(NOTES_PATH)},
        "panel_sources": {
            "a": [base.SUMMARY_SOURCE.name],
            "b": [base.LOCAL_SOURCE.name],
            "c": [base.SUMMARY_SOURCE.name, base.AUDIT_COMPLETION_SOURCE.name],
            "d": [base.CUMULATIVE_SOURCE.name],
        },
        "visual_changes_only": True,
        "point_value_labels": {"a_Smooth": "all A1-A6", "c_M_to_E": "all A1-A6", "c_M_to_L": "all A1-A6"},
        "right_panel_legends": "single-column vertical",
        "local_display_smoothing_window_runs": base.SMOOTHING_WINDOW,
        "outputs": {
            path.suffix.lstrip("."): {"path": path.name, "sha256": sha256(path), "bytes": path.stat().st_size}
            for path in outputs
        },
        "titles_below_panels": True,
        "backend": "Python/matplotlib",
        "png_dpi": 600,
        "svg_text_editable": True,
    }
    with MANIFEST_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def export_figure(fig: plt.Figure) -> list[Path]:
    outputs = [OUTPUT_BASE.with_suffix(suffix) for suffix in [".pdf", ".png", ".svg"]]
    metadata = {
        "Title": "Refined Fig. 4 A1-A6 ablation analysis",
        "Subject": "Visual refinement of audited PHM2010 D1 ablation results; no data or protocol changes",
        "Creator": "Matplotlib",
    }
    fig.savefig(outputs[0], metadata=metadata)
    fig.savefig(outputs[1], dpi=600)
    fig.savefig(outputs[2], metadata={"Title": metadata["Title"], "Description": metadata["Subject"]})
    plt.close(fig)
    update_manifest(outputs)
    return outputs


def main() -> list[Path]:
    apply_style()
    summary, trajectory, local, cumulative = base.load_and_validate_data()
    outputs = export_figure(make_figure(summary, local, cumulative))
    print("[Fig4 refined] protocol changed: False")
    print("[Fig4 refined] training performed: False")
    print(f"[Fig4 refined] trajectory rows validated: {len(trajectory)}")
    for output in outputs:
        print(f"[Fig4 refined output] {output.name} ({output.stat().st_size} bytes)")
    return outputs


if __name__ == "__main__":
    main()
