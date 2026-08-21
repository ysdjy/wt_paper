"""Fig. 4 — Authoritative A1–A6 ablation study.

Input: 补充材料/小论文/3_main_experiment_fgds_psi/1_results/FINAL_ablation_outputs.csv
Output: fig4_ablation.{svg,pdf,png} and data_manifest.json
Run: python figures/fig4_ablation/plot_fig4.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _shared.palette import DC_PSR, NEGATIVE, NEAR_WHITE, POSITIVE
from _shared.style import FIG_WIDTH, apply_publication_style
from _shared.utils_export import export_figure
from _shared.utils_io import read_csv, sha256, write_manifest
from _shared.utils_layout import add_panel_caption, hide_axis_frame


SOURCE = "补充材料/小论文/3_main_experiment_fgds_psi/1_results/FINAL_ablation_outputs.csv"
METHODS = ["A1", "A2", "A3", "A4", "A5", "A6"]
OUT_DIR = Path(__file__).resolve().parent
CMAP = LinearSegmentedColormap.from_list("signed", [NEGATIVE, NEAR_WHITE, POSITIVE])


def normalize_columns(values: np.ndarray) -> np.ndarray:
    out = np.zeros_like(values, dtype=float)
    for j in range(values.shape[1]):
        scale = np.max(np.abs(values[:, j]))
        out[:, j] = values[:, j] / scale if scale else 0
    return out


def main() -> list[Path]:
    apply_publication_style()
    df = read_csv(SOURCE).set_index("Method").loc[METHODS].copy()
    numeric_columns = ["Acc", "Macro-F1", "M-F1", "M-Rec", "M→E", "M→L", "Rev", "Jump", "Smooth"]
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric)
    ref = df.loc["A1"]

    delta = pd.DataFrame(index=METHODS)
    for column in ["Acc", "Macro-F1", "M-F1", "M-Rec"]:
        delta[column] = df[column] - ref[column]
    delta["Smooth benefit"] = ref["Smooth"] - df["Smooth"]
    delta["M→E benefit"] = ref["M→E"] - df["M→E"]
    normalized = normalize_columns(delta.to_numpy(float))

    fig = plt.figure(figsize=(FIG_WIDTH, 5.8))
    gs = fig.add_gridspec(2, 2, hspace=0.76, wspace=0.43)
    ax_a = fig.add_subplot(gs[0, 0])
    bgs = gs[0, 1].subgridspec(1, 2, wspace=0.42)
    ax_b1, ax_b2 = fig.add_subplot(bgs[0, 0]), fig.add_subplot(bgs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])
    fig.subplots_adjust(left=0.10, right=0.985, top=0.98, bottom=0.11)

    # a — raw deltas with column-normalized color support.
    im = ax_a.imshow(normalized, cmap=CMAP, vmin=-1, vmax=1, aspect="auto", interpolation="nearest")
    ax_a.set_xticks(range(delta.shape[1]), labels=["Acc", "Macro-\nF1", "M-\nF1", "M-\nRec", "Smooth\nbenefit", "M→E\nbenefit"])
    ax_a.set_yticks(range(6), labels=METHODS)
    ax_a.tick_params(length=0)
    for spine in ax_a.spines.values():
        spine.set_visible(False)
    for i in range(6):
        for j in range(delta.shape[1]):
            value = delta.iloc[i, j]
            ax_a.text(j, i, f"{value:+.3f}", ha="center", va="center", fontsize=5.1,
                      color="white" if abs(normalized[i, j]) > 0.68 else "#252525")
    ax_a.add_patch(mpl.patches.Rectangle((-0.49, 4.51), delta.shape[1] - 0.02, 0.98,
                                         fill=False, edgecolor=DC_PSR, linewidth=1.2, clip_on=False))
    cbar_a = fig.colorbar(im, ax=ax_a, fraction=0.045, pad=0.025)
    cbar_a.set_label("Column-normalized direction", fontsize=6.0)
    cbar_a.ax.tick_params(labelsize=5.5, length=2)

    # b — two aligned views: classification delta and continuity delta.
    class_delta = delta[["Acc", "Macro-F1", "M-F1", "M-Rec"]].mean(axis=1)
    colors = [mpl.colors.to_rgba(DC_PSR, 0.25 + 0.13 * i) for i in range(6)]
    y = np.arange(6)
    ax_b1.axvline(0, color="#888888", lw=0.7)
    ax_b1.barh(y, class_delta, color=colors, height=0.62)
    ax_b1.set_yticks(y, labels=METHODS)
    ax_b1.invert_yaxis()
    ax_b1.set_xlabel("Mean class Δ")
    ax_b1.set_xlim(min(-0.016, class_delta.min() * 1.2), 0.002)
    for yi, value in zip(y, class_delta):
        ax_b1.text(value - 0.00025, yi, f"{value:+.3f}", ha="right", va="center", fontsize=5.0)

    width = 0.34
    ax_b2.axvline(0, color="#888888", lw=0.7)
    ax_b2.barh(y - width / 2, delta["Smooth benefit"], height=width, color=DC_PSR, label="Smooth")
    ax_b2.barh(y + width / 2, delta["M→E benefit"], height=width, color="#D9A441", label="M→E")
    ax_b2.set_yticks(y, labels=[""] * 6)
    ax_b2.invert_yaxis()
    ax_b2.set_xlabel("Continuity benefit")
    ax_b2.set_xlim(-0.018, 0.012)
    ax_b2.legend(loc="lower center", bbox_to_anchor=(0.5, 1.01), ncol=2, columnspacing=0.6)

    # c — progressive trade-off trajectory.
    acc, smooth = df["Acc"].to_numpy(float), df["Smooth"].to_numpy(float)
    for i in range(5):
        ax_c.annotate("", xy=(acc[i + 1], smooth[i + 1]), xytext=(acc[i], smooth[i]),
                      arrowprops=dict(arrowstyle="-|>", lw=0.8, color="#858585", shrinkA=4, shrinkB=4))
    offsets = {"A1": (4, 7), "A2": (-16, -9), "A3": (-18, 7), "A4": (-47, 15), "A5": (7, -3), "A6": (-40, 10)}
    labels = {"A1": "A1", "A2": "A2", "A3": "A3", "A4": "A4 fusion", "A5": "A5 ordered", "A6": "A6 final"}
    for i, method in enumerate(METHODS):
        ax_c.scatter(acc[i], smooth[i], s=42 if method == "A6" else 29, color=colors[i],
                     edgecolor="white", linewidth=0.45, zorder=4)
        ax_c.annotate(labels[method], (acc[i], smooth[i]), xytext=offsets[method], textcoords="offset points",
                      fontsize=5.5, color=DC_PSR if method == "A6" else "#303030",
                      fontweight="bold" if method in {"A5", "A6"} else "normal",
                      arrowprops=dict(arrowstyle="-", lw=0.45, color="#777777"))
    ax_c.set_xlabel("Accuracy ↑")
    ax_c.set_ylabel("Smooth ↓")
    ax_c.set_xlim(acc.min() - 0.003, acc.max() + 0.003)
    ax_c.set_ylim(smooth.min() - 0.0025, smooth.max() + 0.003)
    ax_c.grid(color="#ECECEC", lw=0.4)

    # d — evidence-backed component summary; no causal claim beyond observed deltas.
    hide_axis_frame(ax_d)
    ax_d.set_xlim(0, 1)
    ax_d.set_ylim(0, 1)
    rows = [
        ("A1", "Raw head", "reference"),
        ("A2", "Fine-state supervision", f"class +0.000; Smooth +{delta.loc['A2', 'Smooth benefit']:.3f}"),
        ("A3", "Ordered prior", f"class +0.000; Smooth +{delta.loc['A3', 'Smooth benefit']:.3f}"),
        ("A4", "Probability fusion", f"class +0.000; Smooth +{delta.loc['A4', 'Smooth benefit']:.3f}"),
        ("A5", "Ordered inference", f"class {class_delta['A5']:+.3f}; Smooth +{delta.loc['A5', 'Smooth benefit']:.3f}"),
        ("A6", "Final balance", f"class {class_delta['A6']:+.3f}; Smooth +{delta.loc['A6', 'Smooth benefit']:.3f}"),
    ]
    for i, (method, component, evidence) in enumerate(rows):
        y0 = 0.90 - i * 0.15
        face = "#E5F0F2" if method == "A6" else "#F2F3F4"
        edge = DC_PSR if method == "A6" else "#B5B8BA"
        ax_d.add_patch(mpl.patches.FancyBboxPatch((0.02, y0 - 0.055), 0.96, 0.105,
                                                  boxstyle="round,pad=0.008,rounding_size=0.012",
                                                  facecolor=face, edgecolor=edge, linewidth=0.7))
        ax_d.text(0.06, y0, method, ha="left", va="center", fontweight="bold", color=edge if method == "A6" else "#333333")
        ax_d.text(0.18, y0 + 0.018, component, ha="left", va="center", fontsize=5.8, fontweight="bold")
        ax_d.text(0.18, y0 - 0.025, evidence, ha="left", va="center", fontsize=5.2, color="#555555")

    add_panel_caption(fig, [ax_a, cbar_a.ax], "a", "Stepwise ablation delta matrix relative to A1", pad=0.030)
    add_panel_caption(fig, [ax_b1, ax_b2], "b", "Classification and continuity\ngain decomposition", pad=0.041)
    add_panel_caption(fig, ax_c, "c", "Progressive accuracy–smoothness\ntrajectory", pad=0.042)
    add_panel_caption(fig, ax_d, "d", "Observed component contributions", pad=0.042)

    key_values = {}
    for method in METHODS:
        key_values[method] = {column: float(df.loc[method, column]) for column in numeric_columns}
        key_values[method].update({f"delta_{column}": float(delta.loc[method, column]) for column in delta.columns})
    write_manifest(OUT_DIR / "data_manifest.json", {
        "figure": "Fig.4 Ablation Study", "audit_status": "passed with explicit warning",
        "sources": [{"path": SOURCE, "sha256": sha256(SOURCE), "table_or_rows": "A1–A6, Split=test_C6",
                     "columns": ["Method", "Output"] + numeric_columns,
                     "aggregation": "none; each row is the final 304-run C6 summary",
                     "normalization": "raw deltas are printed; only heatmap color and panel-b display scales are normalized",
                     "bootstrap": "not used"}],
        "key_values": key_values,
        "warnings": ["The authoritative final file confirms that A1–A4 have exactly identical Acc, Macro-F1, M-F1 and M-Rec values. This is retained as source evidence, not altered to match an expected narrative.",
                     "Rev, Jump and M→L are zero for all A1–A6 and are therefore documented in the manifest but omitted from the visual panels because they add no discrimination."],
    })
    return export_figure(fig, OUT_DIR / "fig4_ablation")


if __name__ == "__main__":
    main()
