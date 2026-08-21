from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

from common import (
    CMAP_DELTA,
    METHOD_COLORS,
    OUT,
    apply_style,
    heatmap,
    panel_label,
    read_csv,
    save_figure,
    write_plot_data,
)


SOURCE = "paper_data/01_PHM2010/03_ablation/A1_A6_AUTHORITATIVE.csv"
METHODS = ["A1", "A2", "A3", "A4", "A5", "A6"]


def normalize_columns(values: np.ndarray) -> np.ndarray:
    out = np.zeros_like(values, dtype=float)
    for j in range(values.shape[1]):
        scale = np.max(np.abs(values[:, j]))
        out[:, j] = values[:, j] / scale if scale > 0 else 0.0
    return out


def make_figure():
    apply_style()
    df = read_csv(SOURCE).set_index("ID").loc[METHODS].copy()
    metric_map = {
        "Acc": "Acc",
        "Macro-F1": "Macro-F1",
        "M-F1": "M-F1",
        "M-Rec": "M-Rec",
    }
    ref = df.loc["A1"]
    delta = pd.DataFrame(index=METHODS)
    for label, col in metric_map.items():
        delta[label] = pd.to_numeric(df[col]) - float(ref[col])
    delta["Smooth benefit"] = float(ref["Smooth"]) - pd.to_numeric(df["Smooth"])
    norm = normalize_columns(delta.to_numpy(float))

    export = df.reset_index()[["ID", "Configuration", "Acc", "Macro-F1", "M-F1", "M-Rec", "Smooth"]].copy()
    for col in delta.columns:
        export[f"delta_{col}"] = delta[col].to_numpy(float)
    write_plot_data(export, "fig4_D1_ablation_A1_A6.csv")

    fig = plt.figure(figsize=(7.2, 4.55))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.30, 1.0], height_ratios=[1.0, 1.0],
                          hspace=0.52, wspace=0.42)
    ax_a = fig.add_subplot(gs[:, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 1])

    # a | delta heatmap versus raw-stage reference
    ann = np.vectorize(lambda x: f"{x:+.3f}")(delta.to_numpy(float))
    heatmap(ax_a, norm, ["Acc", "Macro-\nF1", "M-\nF1", "M-\nRec", "Smooth\nbenefit"], METHODS,
            cmap=CMAP_DELTA, vmin=-1, vmax=1,
            cbar_label="Column-normalized Δ relative to A1",
            annotate=ann, annotate_fmt="{}", outline_row=5, cbar_orientation="horizontal")
    ax_a.set_title("Component–metric effects relative to raw head", loc="left", pad=7)
    panel_label(ax_a, "a", x=-0.16)

    # b | evidence path; effects are always against A1 to avoid implying A2/A3 are nested.
    ax_b.set_xlim(-0.42, 5.42)
    ax_b.set_ylim(-0.58, 0.58)
    ax_b.axis("off")
    labels = ["Raw", "+Fine", "+Prior", "Mixture", "Ordered", "Final"]
    for i, (method, label) in enumerate(zip(METHODS, labels)):
        face = "#F0F0F0" if method != "A6" else "#F5DDD2"
        edge = "#8A8A8A" if method != "A6" else METHOD_COLORS["DC-PSR"]
        box = mpl.patches.FancyBboxPatch((i - 0.34, -0.31), 0.68, 0.62,
                                         boxstyle="round,pad=0.012,rounding_size=0.025",
                                         facecolor=face, edgecolor=edge, linewidth=0.85)
        ax_b.add_patch(box)
        ax_b.text(i, 0.16, label, ha="center", va="center", fontsize=5.4, fontweight="bold")
        if method == "A1":
            text = "reference"
        else:
            text = f"F1 {delta.loc[method, 'M-F1']:+.3f}\nS {delta.loc[method, 'Smooth benefit']:+.3f}"
        ax_b.text(i, -0.105, text, ha="center", va="center", fontsize=4.35, color="#4D4D4D")
        if i < 5:
            ax_b.annotate("", xy=(i + 0.62, 0), xytext=(i + 0.38, 0),
                          arrowprops=dict(arrowstyle="-|>", lw=0.70, color="#7A7A7A", mutation_scale=7))
    ax_b.set_title("Mechanism evidence path (effects vs A1)", loc="left", pad=5)
    panel_label(ax_b, "b", x=-0.12, y=1.02)

    # c | Pareto trajectory
    acc = pd.to_numeric(df["Acc"]).to_numpy(float)
    smooth = pd.to_numeric(df["Smooth"]).to_numpy(float)
    colors = [mpl.colors.to_rgba(METHOD_COLORS["DC-PSR"], 0.30 + 0.14 * i) for i in range(6)]
    for i in range(5):
        ax_c.annotate("", xy=(acc[i + 1], smooth[i + 1]), xytext=(acc[i], smooth[i]),
                      arrowprops=dict(arrowstyle="-|>", lw=0.8, color="#858585",
                                      shrinkA=4, shrinkB=4, mutation_scale=8))
    label_specs = {
        "A1": ("A1", (4, 7)),
        "A2": ("A2", (-14, -9)),
        "A3": ("A3", (-15, 7)),
        "A4": ("A4 hard disc.", (-52, 17)),
        "A5": ("A5 smoothing", (7, -4)),
        "A6": ("A6 balanced", (-44, 10)),
    }
    for i, method in enumerate(METHODS):
        ax_c.scatter(acc[i], smooth[i], s=28 if method != "A6" else 40,
                     color=colors[i], edgecolor="white", linewidth=0.45, zorder=4)
        text, offset = label_specs[method]
        color = METHOD_COLORS["DC-PSR"] if method == "A6" else "#303030"
        ax_c.annotate(text, (acc[i], smooth[i]), xytext=offset, textcoords="offset points",
                      fontsize=5.3, fontweight="bold" if method in {"A4", "A5", "A6"} else "normal",
                      color=color, arrowprops=dict(arrowstyle="-", lw=0.45, color="#707070"))
    ax_c.set_xlabel("Accuracy ↑")
    ax_c.set_ylabel("Smooth ↓")
    ax_c.set_xlim(acc.min() - 0.003, acc.max() + 0.003)
    ax_c.set_ylim(smooth.min() - 0.0025, smooth.max() + 0.003)
    ax_c.set_title("Ablation Pareto trajectory", loc="left", pad=5)
    panel_label(ax_c, "c", x=-0.18)

    fig.subplots_adjust(left=0.09, right=0.985, top=0.94, bottom=0.13)
    return fig


def main():
    return save_figure(make_figure(), OUT / "fig4_ablation", "fig4_ablation")


if __name__ == "__main__":
    main()
