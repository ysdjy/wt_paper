"""Regrouped 2 x 2 Fig. 4 built from the audited formal A1-A6 results.

Primary data: AUTHORITATIVE_A1_A6.csv
Audit-only field completion: ABLATION_RECOMPUTED.csv (E-F1, L-F1, M-Precision)
Outputs: fig4_ablation_regrouped.{pdf,png,svg}
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Mandatory editable-text settings for journal SVG/PDF export.
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Liberation Sans"]
plt.rcParams["svg.fonttype"] = "none"


OUT_DIR = Path(__file__).resolve().parent
PRIMARY_SOURCE = OUT_DIR / "AUTHORITATIVE_A1_A6.csv"
AUDIT_SOURCE = OUT_DIR / "ABLATION_RECOMPUTED.csv"
OUTPUT_BASE = OUT_DIR / "fig4_ablation_regrouped"

METHODS = ["A1", "A2", "A3", "A4", "A5", "A6"]
PRIMARY_COLUMNS = [
    "ID",
    "Configuration",
    "Acc",
    "Macro-F1",
    "M-F1",
    "M-Rec",
    "M→E",
    "M→L",
    "Rev",
    "Jump",
    "Smooth",
]
AUDIT_COMPLETION_METRICS = ["E-F1", "L-F1", "M-Precision"]

# Chapter-wide cool palette, with one warm probability/transition accent.
COLORS = {
    "navy": "#193B5A",
    "blue": "#2F6688",
    "teal": "#287F8A",
    "cyan": "#69B7C1",
    "gold": "#D99227",
    "amber": "#C77C22",
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
            "font.size": 7.1,
            "axes.labelsize": 7.2,
            "xtick.labelsize": 6.6,
            "ytick.labelsize": 6.4,
            "legend.fontsize": 6.1,
            "axes.linewidth": 0.72,
            "axes.edgecolor": COLORS["slate"],
            "axes.spines.top": False,
            "axes.spines.right": False,
            "xtick.major.width": 0.60,
            "ytick.major.width": 0.60,
            "xtick.major.size": 2.7,
            "ytick.major.size": 2.7,
            "legend.frameon": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )


def load_audited_data() -> pd.DataFrame:
    """Load the authoritative table and validate three audit-completed fields."""
    primary = pd.read_csv(PRIMARY_SOURCE)
    missing = [column for column in PRIMARY_COLUMNS if column not in primary.columns]
    if missing:
        raise ValueError(f"Authoritative table is missing required columns: {missing}")
    if primary["ID"].tolist() != METHODS:
        raise ValueError(
            f"Expected A1-A6 in order, found {primary['ID'].astype(str).tolist()}"
        )
    if primary["ID"].duplicated().any():
        raise ValueError("Duplicate ablation IDs in authoritative table")

    numeric_primary = [column for column in PRIMARY_COLUMNS if column not in {"ID", "Configuration"}]
    primary[numeric_primary] = primary[numeric_primary].apply(pd.to_numeric, errors="raise")
    primary = primary.set_index("ID").loc[METHODS].copy()

    audit = pd.read_csv(AUDIT_SOURCE)
    audit_required = {"ID", "Metric", "Recomputed", "Difference", "Assessment"}
    if not audit_required.issubset(audit.columns):
        raise ValueError(f"Audit table lacks columns: {sorted(audit_required - set(audit.columns))}")
    selected = audit[audit["Metric"].isin(AUDIT_COMPLETION_METRICS)].copy()
    expected_pairs = len(METHODS) * len(AUDIT_COMPLETION_METRICS)
    if len(selected) != expected_pairs:
        raise ValueError(f"Expected {expected_pairs} audited completion rows, found {len(selected)}")
    if selected.duplicated(["ID", "Metric"]).any():
        raise ValueError("Duplicate ID/metric pairs in audited completion rows")
    if selected["ID"].drop_duplicates().tolist() != METHODS:
        raise ValueError("Audit completion rows are not ordered A1-A6")
    if pd.to_numeric(selected["Difference"], errors="raise").abs().max() > 1e-12:
        raise ValueError("Audit-completed recognition metrics differ from their stored values")

    completion = selected.pivot(index="ID", columns="Metric", values="Recomputed").loc[METHODS]
    completion = completion.apply(pd.to_numeric, errors="raise")
    for column in AUDIT_COMPLETION_METRICS:
        primary[column] = completion[column]
    primary["M-Precision"] = primary["M-Precision"].astype(float)
    primary["M-Recall"] = primary["M-Rec"].astype(float)

    macro_check = primary[["E-F1", "M-F1", "L-F1"]].mean(axis=1)
    if not np.allclose(macro_check, primary["Macro-F1"], atol=1e-12, rtol=0):
        raise ValueError("State-wise F1 values do not reproduce authoritative Macro-F1")
    middle_f1_check = (
        2
        * primary["M-Precision"]
        * primary["M-Recall"]
        / (primary["M-Precision"] + primary["M-Recall"])
    )
    if not np.allclose(middle_f1_check, primary["M-F1"], atol=1e-12, rtol=0):
        raise ValueError("Middle precision/recall do not reproduce authoritative M-F1")

    print(f"[Fig4 check] authoritative source: {PRIMARY_SOURCE.name}")
    print(f"[Fig4 check] authoritative SHA-256: {sha256(PRIMARY_SOURCE)}")
    print(f"[Fig4 check] available primary fields: {list(pd.read_csv(PRIMARY_SOURCE, nrows=0).columns)}")
    print(f"[Fig4 check] audited completion fields: {AUDIT_COMPLETION_METRICS}")
    print(f"[Fig4 check] ID order: {list(primary.index)}")
    print("[Fig4 check] state-F1 and middle-F1 identities: PASS")
    return primary


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
    ax.tick_params(axis="y", colors=color, width=0.60, length=2.7)
    ax.yaxis.label.set_color(color)


def highlight_a5_a6(ax: mpl.axes.Axes) -> None:
    ax.axvspan(3.52, 4.48, color=COLORS["a5_bg"], zorder=-5)
    ax.axvspan(4.52, 5.48, color=COLORS["a6_bg"], zorder=-5)
    ax.axvline(3.5, color=COLORS["grey"], linewidth=0.55, linestyle=(0, (2, 2)), zorder=-3)


def combine_legends(
    ax_left: mpl.axes.Axes,
    ax_right: mpl.axes.Axes,
    *,
    ncol: int,
    loc: str = "upper left",
) -> None:
    handles_left, labels_left = ax_left.get_legend_handles_labels()
    handles_right, labels_right = ax_right.get_legend_handles_labels()
    ax_left.legend(
        handles_left + handles_right,
        labels_left + labels_right,
        loc=loc,
        ncol=ncol,
        handlelength=1.5,
        columnspacing=0.8,
        handletextpad=0.45,
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
        fontsize=7.4,
        color=COLORS["text"],
    )


def make_figure(df: pd.DataFrame) -> plt.Figure:
    x = np.arange(len(METHODS), dtype=float)
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.75))
    ax_a, ax_b, ax_c, ax_d = axes.flat

    # (a) Overall predictive performance + probability smoothness.
    highlight_a5_a6(ax_a)
    bar_metrics = ["Acc", "Macro-F1", "M-F1"]
    bar_colors = [COLORS["navy"], COLORS["teal"], COLORS["cyan"]]
    width = 0.215
    baseline = 0.96
    for idx, (metric, color) in enumerate(zip(bar_metrics, bar_colors)):
        offset = (idx - 1) * width
        bars = ax_a.bar(
            x + offset,
            df[metric] - baseline,
            bottom=baseline,
            width=width * 0.90,
            color=color,
            edgecolor="white",
            linewidth=0.42,
            label=metric,
            zorder=2,
        )
        for method_idx in (4, 5):
            bars[method_idx].set_edgecolor(COLORS["amber"] if method_idx == 4 else COLORS["a6_edge"])
            bars[method_idx].set_linewidth(0.90)
    ax_a.set_ylim(0.96, 1.002)
    ax_a.set_yticks([0.96, 0.97, 0.98, 0.99, 1.00])
    ax_a.set_ylabel("Score (higher is better)")
    ax_a.set_xticks(x, METHODS)
    style_axis(ax_a)

    ax_a_r = ax_a.twinx()
    ax_a_r.plot(
        x,
        df["Smooth"],
        color=COLORS["gold"],
        marker="o",
        markersize=4.1,
        markerfacecolor="white",
        markeredgewidth=1.05,
        linewidth=1.45,
        label="Smooth ↓",
        zorder=5,
    )
    ax_a_r.set_ylim(0.0115, 0.0255)
    ax_a_r.set_yticks([0.012, 0.016, 0.020, 0.024])
    ax_a_r.set_ylabel("Smooth (lower is better)")
    style_twin_axis(ax_a_r, COLORS["gold"])
    combine_legends(ax_a, ax_a_r, ncol=4)
    ax_a_r.annotate(
        "A5: strongest\nsmoothing",
        xy=(4, df.loc["A5", "Smooth"]),
        xytext=(3.28, 0.0120),
        ha="right",
        va="bottom",
        fontsize=5.7,
        color=COLORS["amber"],
        fontweight="bold",
        arrowprops=dict(arrowstyle="-|>", color=COLORS["amber"], lw=0.72, mutation_scale=7),
    )
    ax_a.annotate(
        "A6: predictive\naccuracy restored",
        xy=(5 - width, df.loc["A6", "Acc"]),
        xytext=(4.20, 0.9968),
        ha="left",
        va="top",
        fontsize=5.7,
        color=COLORS["a6_edge"],
        fontweight="bold",
        arrowprops=dict(arrowstyle="-|>", color=COLORS["a6_edge"], lw=0.72, mutation_scale=7),
    )
    below_title(ax_a, "a", "Overall predictive performance across A1–A6")

    # (b) State-wise recognition profile.
    highlight_a5_a6(ax_b)
    state_specs = [
        ("E-F1", "E-F1", "#315A7D", "o"),
        ("M-F1", "M-F1", "#C88A24", "s"),
        ("L-F1", "L-F1", "#B65A3A", "^"),
    ]
    for metric, label, color, marker in state_specs:
        ax_b.plot(
            x,
            df[metric],
            color=color,
            marker=marker,
            markersize=4.0,
            markerfacecolor="white",
            markeredgewidth=1.0,
            linewidth=1.35,
            label=label,
            zorder=4,
        )
    ax_b.set_xlim(-0.35, 5.35)
    ax_b.set_ylim(0.968, 1.0025)
    ax_b.set_yticks([0.97, 0.98, 0.99, 1.00])
    ax_b.set_ylabel("State-wise F1 (higher is better)")
    ax_b.set_xticks(x, METHODS)
    style_axis(ax_b)
    ax_b.legend(loc="center left", bbox_to_anchor=(0.01, 0.13), ncol=3,
                handlelength=1.55, columnspacing=0.8, borderaxespad=0.15)
    ax_b.text(
        1.5,
        0.9776,
        "A1–A4: identical class decisions",
        ha="center",
        va="bottom",
        fontsize=5.55,
        color=COLORS["slate"],
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.78, pad=0.35),
    )
    annotation_offsets = {
        "E-F1": ((-19, -9), (4, -8)),
        "M-F1": ((-18, 5), (4, 5)),
        "L-F1": ((-18, 5), (4, 5)),
    }
    for metric, _, color, _ in state_specs:
        for method, offsets in zip(("A5", "A6"), annotation_offsets[metric]):
            ax_b.annotate(
                f"{df.loc[method, metric]:.3f}",
                xy=(METHODS.index(method), df.loc[method, metric]),
                xytext=offsets,
                textcoords="offset points",
                fontsize=5.1,
                color=color,
            )
    below_title(ax_b, "b", "State-wise recognition profile")

    # (c) Middle-stage precision/recall + transition errors.
    highlight_a5_a6(ax_c)
    c_width = 0.28
    c_baseline = 0.94
    for offset, metric, label, color in [
        (-c_width / 2, "M-Precision", "M-Pre", COLORS["teal"]),
        (c_width / 2, "M-Recall", "M-Rec", COLORS["blue"]),
    ]:
        bars = ax_c.bar(
            x + offset,
            df[metric] - c_baseline,
            bottom=c_baseline,
            width=c_width * 0.90,
            color=color,
            edgecolor="white",
            linewidth=0.42,
            label=label,
            zorder=2,
        )
        bars[4].set_edgecolor(COLORS["amber"])
        bars[4].set_linewidth(0.85)
        bars[5].set_edgecolor(COLORS["a6_edge"])
        bars[5].set_linewidth(0.85)
    ax_c.set_ylim(0.94, 1.005)
    ax_c.set_yticks([0.94, 0.96, 0.98, 1.00])
    ax_c.set_ylabel("Middle-stage score (higher is better)")
    ax_c.set_xticks(x, METHODS)
    style_axis(ax_c)

    ax_c_r = ax_c.twinx()
    for metric, label, color, marker in [
        ("M→E", "M→E ↓", COLORS["rust"], "D"),
        ("M→L", "M→L ↓", COLORS["slate"], "v"),
    ]:
        ax_c_r.plot(
            x,
            df[metric],
            color=color,
            marker=marker,
            markersize=3.8,
            markerfacecolor="white",
            markeredgewidth=0.95,
            linewidth=1.25,
            label=label,
            zorder=5,
        )
    ax_c_r.set_ylim(-0.002, 0.0445)
    ax_c_r.set_yticks([0.00, 0.01, 0.02, 0.03, 0.04])
    ax_c_r.set_ylabel("Transition error rate (lower is better)")
    style_twin_axis(ax_c_r, COLORS["rust"])
    combine_legends(ax_c, ax_c_r, ncol=4)
    ax_c.annotate(
        "A6 restores M-Rec",
        xy=(5 + c_width / 2, df.loc["A6", "M-Recall"]),
        xytext=(4.02, 0.987),
        fontsize=5.55,
        color=COLORS["a6_edge"],
        fontweight="bold",
        arrowprops=dict(arrowstyle="-|>", color=COLORS["a6_edge"], lw=0.68, mutation_scale=7),
    )
    below_title(ax_c, "c", "Middle-stage and transition consistency")

    # (d) Trajectory-level diagnostics; Rev and Jump are exactly zero throughout.
    highlight_a5_a6(ax_d)
    d_width = 0.28
    for offset, metric, color, hatch in [
        (-d_width / 2, "Rev", COLORS["slate"], "///"),
        (d_width / 2, "Jump", COLORS["rust"], "\\\\"),
    ]:
        ax_d.bar(
            x + offset,
            df[metric],
            width=d_width * 0.90,
            color="white",
            edgecolor=color,
            linewidth=0.80,
            hatch=hatch,
            label=metric,
            zorder=2,
        )
        ax_d.scatter(x + offset, np.zeros_like(x), marker="_", s=22, color=color, linewidths=0.95, zorder=4)
    ax_d.set_ylim(-0.03, 0.50)
    ax_d.set_yticks([0.0, 0.25, 0.50])
    ax_d.set_ylabel("Trajectory events (lower is better)")
    ax_d.set_xticks(x, METHODS)
    style_axis(ax_d)
    ax_d.text(
        0.03,
        0.91,
        "Rev = Jump = 0 for all A1–A6",
        transform=ax_d.transAxes,
        fontsize=5.65,
        color=COLORS["slate"],
        fontweight="bold",
    )

    ax_d_r = ax_d.twinx()
    ax_d_r.plot(
        x,
        df["Smooth"],
        color=COLORS["gold"],
        marker="o",
        markersize=4.2,
        markerfacecolor="white",
        markeredgewidth=1.0,
        linewidth=1.45,
        label="Smooth ↓",
        zorder=5,
    )
    ax_d_r.set_ylim(0.0115, 0.0255)
    ax_d_r.set_yticks([0.012, 0.016, 0.020, 0.024])
    ax_d_r.set_ylabel("Smooth (lower is better)")
    style_twin_axis(ax_d_r, COLORS["gold"])
    combine_legends(ax_d, ax_d_r, ncol=3)
    ax_d_r.annotate(
        "ordered output  →  final blend",
        xy=(5, df.loc["A6", "Smooth"]),
        xytext=(3.55, 0.0246),
        ha="left",
        va="top",
        fontsize=5.55,
        color=COLORS["a6_edge"],
        fontweight="bold",
        arrowprops=dict(arrowstyle="-|>", color=COLORS["a6_edge"], lw=0.70, mutation_scale=7),
    )
    ax_d.text(
        0.03,
        0.12,
        "Lower is better for Rev / Jump / Smooth",
        transform=ax_d.transAxes,
        fontsize=5.35,
        color=COLORS["slate"],
    )
    below_title(ax_d, "d", "Trajectory stability diagnostics")

    for ax in (ax_a, ax_b, ax_c, ax_d):
        ax.set_xlim(-0.45, 5.45)

    fig.subplots_adjust(left=0.085, right=0.925, top=0.978, bottom=0.105, wspace=0.38, hspace=0.56)
    return fig


def export_figure(fig: plt.Figure) -> list[Path]:
    metadata = {
        "Title": "Fig. 4 A1-A6 ablation: accuracy-consistency trade-off",
        "Subject": "Audited PHM2010 D1 ablation results from one frozen formal backbone",
        "Creator": "Matplotlib",
    }
    outputs = [
        OUTPUT_BASE.with_suffix(".pdf"),
        OUTPUT_BASE.with_suffix(".png"),
        OUTPUT_BASE.with_suffix(".svg"),
    ]
    fig.savefig(outputs[0], metadata=metadata)
    fig.savefig(outputs[1], dpi=600)
    fig.savefig(outputs[2], metadata={"Title": metadata["Title"], "Description": metadata["Subject"]})
    plt.close(fig)
    return outputs


def main() -> list[Path]:
    apply_style()
    df = load_audited_data()
    outputs = export_figure(make_figure(df))
    for output in outputs:
        print(f"[Fig4 output] {output.name} ({output.stat().st_size} bytes)")
    return outputs


if __name__ == "__main__":
    main()
