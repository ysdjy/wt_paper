"""Fig. 4 V2: audited summary anchors plus formal lifecycle trajectories."""

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

# Editable text in the vector exports.
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Liberation Sans"]
plt.rcParams["svg.fonttype"] = "none"


OUT_DIR = Path(__file__).resolve().parent
SUMMARY_SOURCE = OUT_DIR / "AUTHORITATIVE_A1_A6.csv"
AUDIT_COMPLETION_SOURCE = OUT_DIR / "ABLATION_RECOMPUTED.csv"
TRAJECTORY_SOURCE = OUT_DIR / "A1_A6_probability_trajectories.csv"
LOCAL_SOURCE = OUT_DIR / "A1_A6_lifecycle_variation.csv"
CUMULATIVE_SOURCE = OUT_DIR / "A1_A6_cumulative_variation.csv"
AUDIT_DOCUMENT = OUT_DIR / "FIG4_V2_DATA_AUDIT.md"
MANIFEST_PATH = OUT_DIR / "data_manifest.json"
OUTPUT_BASE = OUT_DIR / "fig4_ablation_v2"

METHODS = ["A1", "A2", "A3", "A4", "A5", "A6"]
SMOOTHING_WINDOW = 11
METHOD_COLORS = {
    "A1": "#8B949C",
    "A2": "#8AA9BA",
    "A3": "#5F89A5",
    "A4": "#315E7D",
    "A5": "#D6922E",
    "A6": "#0B6174",
}
METHOD_MARKERS = {"A1": "o", "A2": "s", "A3": "^", "A4": "D", "A5": "P", "A6": "X"}
COLORS = {
    "navy": "#193B5A",
    "blue": "#2F6688",
    "teal": "#287F8A",
    "cyan": "#69B7C1",
    "gold": "#D99227",
    "rust": "#B65A3A",
    "slate": "#697783",
    "grey": "#AEB7BE",
    "text": "#252B2F",
    "grid": "#E4E8EB",
    "a5_bg": "#FBF0DD",
    "a6_bg": "#E5F2F3",
    "a6_edge": "#0B6174",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def apply_style() -> None:
    mpl.rcParams.update(
        {
            "pdf.fonttype": 42,
            "font.size": 7.0,
            "axes.labelsize": 7.15,
            "xtick.labelsize": 6.45,
            "ytick.labelsize": 6.25,
            "legend.fontsize": 5.9,
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
        }
    )


def load_and_validate_data():
    summary = pd.read_csv(SUMMARY_SOURCE)
    required_summary = ["ID", "Acc", "Macro-F1", "M-F1", "M-Rec", "M→E", "M→L", "Smooth"]
    missing = [column for column in required_summary if column not in summary.columns]
    if missing:
        raise ValueError(f"Authoritative summary lacks columns: {missing}")
    if summary["ID"].tolist() != METHODS:
        raise ValueError("Authoritative summary order is not A1-A6")
    summary = summary.set_index("ID").loc[METHODS].copy()
    summary[required_summary[1:]] = summary[required_summary[1:]].apply(pd.to_numeric, errors="raise")

    audit = pd.read_csv(AUDIT_COMPLETION_SOURCE)
    m_precision = audit[audit["Metric"].eq("M-Precision")].copy()
    if len(m_precision) != 6 or pd.to_numeric(m_precision["Difference"], errors="raise").abs().max() > 1e-12:
        raise ValueError("Audited middle-stage precision completion failed")
    summary["M-Precision"] = (
        m_precision.set_index("ID").loc[METHODS, "Recomputed"].astype(float)
    )
    summary["M-Recall"] = summary["M-Rec"].astype(float)
    middle_f1 = 2 * summary["M-Precision"] * summary["M-Recall"] / (
        summary["M-Precision"] + summary["M-Recall"]
    )
    if not np.allclose(middle_f1, summary["M-F1"], atol=1e-12, rtol=0):
        raise ValueError("M-Precision/M-Recall do not reproduce authoritative M-F1")

    trajectory = pd.read_csv(TRAJECTORY_SOURCE)
    local = pd.read_csv(LOCAL_SOURCE)
    cumulative = pd.read_csv(CUMULATIVE_SOURCE)
    for name, frame in [("trajectory", trajectory), ("local", local), ("cumulative", cumulative)]:
        if len(frame) != 1824:
            raise ValueError(f"{name} table must contain 1824 rows")
        if sorted(frame["ID"].unique().tolist()) != METHODS:
            raise ValueError(f"{name} table does not contain A1-A6")
        counts = frame.groupby("ID").size().reindex(METHODS)
        if not (counts == 304).all():
            raise ValueError(f"{name} table does not contain 304 rows per method")

    if not (pd.to_numeric(local["smoothing_window_runs"]).drop_duplicates().tolist() == [SMOOTHING_WINDOW]):
        raise ValueError("Lifecycle table smoothing window is not 11 runs")
    for method in METHODS:
        local_method = local[local["ID"].eq(method)].sort_values("run_id")
        cumulative_method = cumulative[cumulative["ID"].eq(method)].sort_values("run_id")
        smooth = float(summary.loc[method, "Smooth"])
        local_mean = float(local_method["local_variation_l1"].mean())
        endpoint = float(cumulative_method["cumulative_variation_l1"].iloc[-1])
        if abs(local_mean - smooth) > 5e-10:
            raise ValueError(f"{method} local mean does not reproduce Smooth")
        if abs(endpoint / 303 - smooth) > 5e-10:
            raise ValueError(f"{method} cumulative endpoint does not reproduce Smooth")
    return summary, trajectory, local, cumulative


def style_axis(ax: mpl.axes.Axes, *, grid: bool = True) -> None:
    ax.spines["left"].set_color(COLORS["slate"])
    ax.spines["bottom"].set_color(COLORS["slate"])
    ax.tick_params(colors=COLORS["text"], labelcolor=COLORS["text"])
    if grid:
        ax.grid(axis="y", color=COLORS["grid"], linewidth=0.48, alpha=0.92)
        ax.set_axisbelow(True)


def style_twin_axis(ax: mpl.axes.Axes, color: str) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(True)
    ax.spines["right"].set_color(color)
    ax.spines["right"].set_linewidth(0.72)
    ax.tick_params(axis="y", colors=color, width=0.60, length=2.6)
    ax.yaxis.label.set_color(color)


def highlight_a5_a6(ax: mpl.axes.Axes) -> None:
    ax.axvspan(3.52, 4.48, color=COLORS["a5_bg"], zorder=-5)
    ax.axvspan(4.52, 5.48, color=COLORS["a6_bg"], zorder=-5)
    ax.axvline(3.5, color=COLORS["grey"], linewidth=0.55, linestyle=(0, (2, 2)), zorder=-3)


def combine_legends(ax_left: mpl.axes.Axes, ax_right: mpl.axes.Axes, ncol: int) -> None:
    handles_left, labels_left = ax_left.get_legend_handles_labels()
    handles_right, labels_right = ax_right.get_legend_handles_labels()
    ax_left.legend(
        handles_left + handles_right,
        labels_left + labels_right,
        loc="upper left",
        ncol=ncol,
        handlelength=1.45,
        columnspacing=0.72,
        handletextpad=0.38,
        borderaxespad=0.15,
    )


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


def draw_panel_a(ax: mpl.axes.Axes, summary: pd.DataFrame) -> None:
    x = np.arange(6, dtype=float)
    highlight_a5_a6(ax)
    width = 0.215
    baseline = 0.96
    for index, (metric, color) in enumerate(
        zip(["Acc", "Macro-F1", "M-F1"], [COLORS["navy"], COLORS["teal"], COLORS["cyan"]])
    ):
        offset = (index - 1) * width
        bars = ax.bar(
            x + offset,
            summary[metric] - baseline,
            bottom=baseline,
            width=width * 0.90,
            color=color,
            edgecolor="white",
            linewidth=0.42,
            label=metric,
            zorder=2,
        )
        bars[4].set_edgecolor(METHOD_COLORS["A5"])
        bars[4].set_linewidth(0.88)
        bars[5].set_edgecolor(METHOD_COLORS["A6"])
        bars[5].set_linewidth(0.88)
    ax.set_ylim(0.96, 1.002)
    ax.set_yticks([0.96, 0.97, 0.98, 0.99, 1.00])
    ax.set_ylabel("Score (higher is better)")
    ax.set_xticks(x, METHODS)
    ax.set_xlim(-0.45, 5.45)
    style_axis(ax)

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
    right.set_ylim(0.0115, 0.0255)
    right.set_yticks([0.012, 0.016, 0.020, 0.024])
    right.set_ylabel("Smooth (lower is better)")
    style_twin_axis(right, COLORS["gold"])
    combine_legends(ax, right, ncol=4)
    right.annotate(
        "A5: strongest\nsmoothing",
        xy=(4, summary.loc["A5", "Smooth"]),
        xytext=(3.25, 0.0120),
        ha="right",
        va="bottom",
        fontsize=5.55,
        color=METHOD_COLORS["A5"],
        fontweight="bold",
        arrowprops=dict(arrowstyle="-|>", color=METHOD_COLORS["A5"], lw=0.68, mutation_scale=7),
    )
    ax.annotate(
        "A6: accuracy\nrestored",
        xy=(5 - width, summary.loc["A6", "Acc"]),
        xytext=(4.22, 0.9968),
        ha="left",
        va="top",
        fontsize=5.55,
        color=METHOD_COLORS["A6"],
        fontweight="bold",
        arrowprops=dict(arrowstyle="-|>", color=METHOD_COLORS["A6"], lw=0.68, mutation_scale=7),
    )
    below_title(ax, "a", "Overall predictive performance across A1–A6")


def draw_panel_b(ax: mpl.axes.Axes, local: pd.DataFrame) -> None:
    for method in METHODS:
        frame = local[local["ID"].eq(method)].sort_values("run_id")
        x = frame["relative_tool_life"].to_numpy(float)
        raw = frame["local_variation_l1"].to_numpy(float)
        smoothed = frame["local_variation_l1_smoothed"].to_numpy(float)
        color = METHOD_COLORS[method]
        ax.plot(x, raw, color=color, linewidth=0.48, alpha=0.14, zorder=1)
        ax.plot(
            x,
            smoothed,
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
    ax.set_ylim(0, 0.66)
    ax.set_xticks(np.linspace(0, 1, 6))
    ax.set_yticks(np.arange(0, 0.7, 0.1))
    ax.set_xlabel("Relative tool life")
    ax.set_ylabel(r"Local probability variation  $\Delta_t$ (L1)")
    style_axis(ax)
    ax.legend(
        loc="upper left",
        ncol=3,
        handlelength=1.65,
        columnspacing=0.72,
        handletextpad=0.38,
        borderaxespad=0.20,
    )
    ax.text(
        0.02,
        0.035,
        "thin: raw  |  dark: centered 11-run mean",
        transform=ax.transAxes,
        fontsize=5.25,
        color=COLORS["slate"],
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.80, pad=0.35),
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
        bars[4].set_edgecolor(METHOD_COLORS["A5"])
        bars[4].set_linewidth(0.85)
        bars[5].set_edgecolor(METHOD_COLORS["A6"])
        bars[5].set_linewidth(0.85)
    ax.set_ylim(0.94, 1.005)
    ax.set_yticks([0.94, 0.96, 0.98, 1.00])
    ax.set_ylabel("Middle-stage score (higher is better)")
    ax.set_xticks(x, METHODS)
    ax.set_xlim(-0.45, 5.45)
    style_axis(ax)

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
    right.set_ylim(-0.002, 0.0445)
    right.set_yticks([0.00, 0.01, 0.02, 0.03, 0.04])
    right.set_ylabel("Transition error rate (lower is better)")
    style_twin_axis(right, COLORS["rust"])
    combine_legends(ax, right, ncol=4)
    ax.annotate(
        "A6 restores M-Rec",
        xy=(5 + width / 2, summary.loc["A6", "M-Recall"]),
        xytext=(4.02, 0.987),
        fontsize=5.45,
        color=METHOD_COLORS["A6"],
        fontweight="bold",
        arrowprops=dict(arrowstyle="-|>", color=METHOD_COLORS["A6"], lw=0.66, mutation_scale=7),
    )
    below_title(ax, "c", "Middle-stage and transition consistency")


def spread_endpoint_labels(endpoints: dict[str, float], minimum_gap: float = 0.22) -> dict[str, float]:
    ordered = sorted(endpoints.items(), key=lambda item: item[1])
    positions: dict[str, float] = {}
    previous = -np.inf
    for method, value in ordered:
        position = max(value, previous + minimum_gap)
        positions[method] = position
        previous = position
    return positions


def draw_panel_d(ax: mpl.axes.Axes, cumulative: pd.DataFrame) -> None:
    endpoints = {}
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
            zorder=4 if method in {"A5", "A6"} else 3,
        )
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 7.55)
    ax.set_xticks(np.linspace(0, 1, 6))
    ax.set_yticks(np.arange(0, 8, 1))
    ax.set_xlabel("Relative tool life")
    ax.set_ylabel(r"Cumulative probability variation  $C_t$ (L1)")
    style_axis(ax)

    label_positions = spread_endpoint_labels(endpoints)
    for method in METHODS:
        endpoint = endpoints[method]
        label_y = label_positions[method]
        color = METHOD_COLORS[method]
        ax.plot([1.0, 1.018], [endpoint, label_y], color=color, linewidth=0.60, clip_on=False)
        suffix = f"  {endpoint:.2f}" if method in {"A5", "A6"} else ""
        ax.text(
            1.024,
            label_y,
            f"{method}{suffix}",
            color=color,
            fontsize=5.55,
            fontweight="bold" if method in {"A5", "A6"} else "normal",
            ha="left",
            va="center",
            clip_on=False,
        )
    ax.text(
        0.02,
        0.92,
        r"terminal $C_t$/303 = Smooth",
        transform=ax.transAxes,
        fontsize=5.35,
        color=COLORS["slate"],
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.80, pad=0.35),
    )
    ax.annotate(
        "A5: lowest total variation",
        xy=(1.0, endpoints["A5"]),
        xytext=(0.57, 3.05),
        fontsize=5.45,
        color=METHOD_COLORS["A5"],
        fontweight="bold",
        arrowprops=dict(arrowstyle="-|>", color=METHOD_COLORS["A5"], lw=0.66, mutation_scale=7),
    )
    ax.annotate(
        "A6: final accuracy–consistency balance",
        xy=(0.82, cumulative[cumulative["ID"].eq("A6")].sort_values("run_id")["cumulative_variation_l1"].iloc[248]),
        xytext=(0.42, 6.68),
        fontsize=5.35,
        color=METHOD_COLORS["A6"],
        fontweight="bold",
        arrowprops=dict(arrowstyle="-|>", color=METHOD_COLORS["A6"], lw=0.66, mutation_scale=7),
    )
    below_title(ax, "d", "Cumulative trajectory variation")


def make_figure(summary: pd.DataFrame, local: pd.DataFrame, cumulative: pd.DataFrame) -> plt.Figure:
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.75))
    draw_panel_a(axes[0, 0], summary)
    draw_panel_b(axes[0, 1], local)
    draw_panel_c(axes[1, 0], summary)
    draw_panel_d(axes[1, 1], cumulative)
    fig.subplots_adjust(left=0.085, right=0.905, top=0.978, bottom=0.105, wspace=0.40, hspace=0.56)
    return fig


def update_manifest(outputs: list[Path]) -> None:
    with MANIFEST_PATH.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    v2 = manifest.setdefault("fig4_v2", {})
    v2["plot"] = {
        "script": {"path": Path(__file__).name, "sha256": sha256(Path(__file__))},
        "data_audit": {"path": AUDIT_DOCUMENT.name, "sha256": sha256(AUDIT_DOCUMENT)},
        "panel_sources": {
            "a": [SUMMARY_SOURCE.name],
            "b": [LOCAL_SOURCE.name],
            "c": [SUMMARY_SOURCE.name, AUDIT_COMPLETION_SOURCE.name],
            "d": [CUMULATIVE_SOURCE.name],
        },
        "outputs": {
            path.suffix.lstrip("."): {"path": path.name, "sha256": sha256(path), "bytes": path.stat().st_size}
            for path in outputs
        },
        "titles_below_panels": True,
        "total_title": False,
        "backend": "Python/matplotlib",
        "png_dpi": 600,
        "svg_text_editable": True,
    }
    with MANIFEST_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def export_figure(fig: plt.Figure) -> list[Path]:
    outputs = [
        OUTPUT_BASE.with_suffix(".pdf"),
        OUTPUT_BASE.with_suffix(".png"),
        OUTPUT_BASE.with_suffix(".svg"),
    ]
    metadata = {
        "Title": "Fig. 4 A1-A6 lifecycle probability variation",
        "Subject": "Inference-only visualization of audited PHM2010 D1 ablation trajectories",
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
    summary, trajectory, local, cumulative = load_and_validate_data()
    outputs = export_figure(make_figure(summary, local, cumulative))
    print("[Fig4 V2 plot] protocol changed: False")
    print("[Fig4 V2 plot] training performed: False")
    print(f"[Fig4 V2 plot] trajectory rows validated: {len(trajectory)}")
    for output in outputs:
        print(f"[Fig4 V2 output] {output.name} ({output.stat().st_size} bytes)")
    return outputs


if __name__ == "__main__":
    main()
