"""Fig. 3 — Cross-dataset / cross-benchmark perspective.

Inputs: final PHM D1 evidence, NASA original-split summaries, cross-machine five-seed
summaries, and the D2-M seed-42 prediction table.
Output: fig3_cross_dataset.{svg,pdf,png} and data_manifest.json
Run: python figures/fig3_cross_dataset/plot_fig3.py
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
from _shared.palette import BACKBONE, DC_PSR, NEGATIVE, NEAR_WHITE, POSITIVE
from _shared.style import FIG_WIDTH, apply_publication_style
from _shared.utils_export import export_figure
from _shared.utils_io import read_csv, sha256, write_manifest
from _shared.utils_layout import add_panel_caption, hide_axis_frame


D1_SOURCE = "final_statistical_evidence/results/D1_MAIN_BOOTSTRAP_CI.csv"
NASA_SOURCE = "补充材料/小论文/nasa_dcpsr_results_stageaware_opt/Table_NASA_original_split_mean_std.csv"
CROSS_MACHINE_SOURCE = "experiments_mendeley/04_overall_comparison/summary/overall_comparison_mean_std_by_task.csv"
FAILURE_SOURCE = "experiments_mendeley/07_semantic_consistency/probability_evolution/D2-M_seed42_predictions_test_B11B12.csv"
OUT_DIR = Path(__file__).resolve().parent
METRICS = ["ΔAcc", "ΔM-F1", "Smooth benefit", "Jump benefit"]
CMAP = LinearSegmentedColormap.from_list("signed", [NEGATIVE, NEAR_WHITE, POSITIVE])


def normalize_columns(values: np.ndarray) -> np.ndarray:
    out = np.zeros_like(values, dtype=float)
    for j in range(values.shape[1]):
        scale = np.max(np.abs(values[:, j]))
        out[:, j] = values[:, j] / scale if scale else 0
    return out


def build_effect_tables():
    d1 = read_csv(D1_SOURCE).set_index("Method")
    b, d = d1.loc["Multi-task TCN-GRU"], d1.loc["DC-PSR"]
    phm = [d["Acc"] - b["Acc"], d["M_F1"] - b["M_F1"], b["Smooth"] - d["Smooth"], b["Jump"] - d["Jump"]]

    nasa = read_csv(NASA_SOURCE).set_index("Method")
    b, d = nasa.loc["B11"], nasa.loc["B12"]
    nasa_effect = [d["Acc_mean"] - b["Acc_mean"], d["M-F1_mean"] - b["M-F1_mean"],
                   b["Smooth_mean"] - d["Smooth_mean"], b["Jump_mean"] - d["Jump_mean"]]

    cm = read_csv(CROSS_MACHINE_SOURCE)
    cm = cm[cm["Method"].isin(["B11", "B12"])].set_index(["task", "Method"])
    task_rows = []
    for task in ["D1-M", "D2-M", "D3-M"]:
        b, d = cm.loc[(task, "B11")], cm.loc[(task, "B12")]
        task_rows.append({"task": task, "ΔAcc": d["Acc_mean"] - b["Acc_mean"],
                          "ΔM-F1": d["M_F1_mean"] - b["M_F1_mean"],
                          "Smooth benefit": b["Smooth_mean"] - d["Smooth_mean"],
                          "Jump benefit": b["Jump_mean"] - d["Jump_mean"]})
    task_effect = pd.DataFrame(task_rows).set_index("task")
    dataset_effect = pd.DataFrame([phm, nasa_effect, task_effect.mean().to_list()],
                                  index=["PHM2010", "NASA", "Cross-machine"], columns=METRICS)
    return dataset_effect.astype(float), task_effect.astype(float)


def draw_signed_heatmap(fig, ax, raw: pd.DataFrame):
    norm = normalize_columns(raw.to_numpy(float))
    im = ax.imshow(norm, cmap=CMAP, vmin=-1, vmax=1, aspect="auto", interpolation="nearest")
    ax.set_xticks(range(len(METRICS)), labels=["ΔAcc", "ΔM-F1", "Smooth\nbenefit", "Jump\nbenefit"])
    ax.set_yticks(range(len(raw.index)), labels=raw.index)
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    for i in range(raw.shape[0]):
        for j in range(raw.shape[1]):
            value = raw.iloc[i, j]
            ax.text(j, i, f"{value:+.3f}" if j < 3 else f"{value:+.1f}",
                    ha="center", va="center", fontsize=5.4,
                    color="white" if abs(norm[i, j]) > 0.68 else "#252525")
    cbar = fig.colorbar(im, ax=ax, fraction=0.045, pad=0.025)
    cbar.set_label("Column-normalized effect", fontsize=6.0)
    cbar.ax.tick_params(labelsize=5.5, length=2)
    return cbar


def main() -> list[Path]:
    apply_publication_style()
    dataset_effect, task_effect = build_effect_tables()

    failure = read_csv(FAILURE_SOURCE)
    stages = ["early", "middle", "late"]
    true_frac = failure["stage_true"].str.lower().value_counts(normalize=True).reindex(stages, fill_value=0)
    pred_frac = failure["stage_pred_final_name"].str.lower().value_counts(normalize=True).reindex(stages, fill_value=0)

    fig = plt.figure(figsize=(FIG_WIDTH, 5.75))
    gs = fig.add_gridspec(2, 2, hspace=0.76, wspace=0.43)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    cgs = gs[1, 0].subgridspec(2, 2, hspace=0.56, wspace=0.42)
    axes_c = [fig.add_subplot(cgs[i, j]) for i in range(2) for j in range(2)]
    ax_d = fig.add_subplot(gs[1, 1])
    fig.subplots_adjust(left=0.10, right=0.98, top=0.97, bottom=0.11)

    # a — benchmark shift ladder.
    hide_axis_frame(ax_a)
    ax_a.set_xlim(0, 1)
    ax_a.set_ylim(0, 1)
    boxes = [
        (0.02, 0.69, "PHM2010", "cross-condition", "3 targets", "#E8EFF3"),
        (0.35, 0.69, "NASA", "cross-case", "N1–N4", "#E5F0ED"),
        (0.68, 0.69, "Cross-machine", "machine + sensor shift", "D1-M–D3-M", "#F4E6DC"),
    ]
    for x, y, name, role, count, face in boxes:
        patch = mpl.patches.FancyBboxPatch((x, y - 0.18), 0.29, 0.34,
                                           boxstyle="round,pad=0.012,rounding_size=0.018",
                                           facecolor=face, edgecolor="#6F7478", linewidth=0.7)
        ax_a.add_patch(patch)
        ax_a.text(x + 0.145, y + 0.07, name, ha="center", va="center", fontweight="bold", fontsize=7.0)
        ax_a.text(x + 0.145, y - 0.02, role, ha="center", va="center", fontsize=5.7, color="#4D555A")
        ax_a.text(x + 0.145, y - 0.10, count, ha="center", va="center", fontsize=5.5, color="#62686C")
    for x in [0.315, 0.645]:
        ax_a.annotate("", xy=(x + 0.03, 0.69), xytext=(x, 0.69),
                      arrowprops=dict(arrowstyle="-|>", color="#777777", lw=0.9))
    ax_a.text(0.50, 0.25, "Increasing domain and sensing shift", ha="center", fontsize=6.1, color="#555555")
    ax_a.annotate("", xy=(0.82, 0.36), xytext=(0.18, 0.36),
                  arrowprops=dict(arrowstyle="-|>", color="#999999", lw=1.0))

    # b — dataset-level backbone-controlled effects.
    cbar_b = draw_signed_heatmap(fig, ax_b, dataset_effect)

    # c — cross-machine task-specific directional profiles.
    normalized = normalize_columns(task_effect.to_numpy(float))
    colors = ["#5B7FA3", "#6C948D", "#D9A441"]
    for j, (ax, metric) in enumerate(zip(axes_c, METRICS)):
        vals = normalized[:, j]
        ax.axhline(0, color="#8D8D8D", lw=0.65)
        ax.bar(range(3), vals, color=[colors[i] if vals[i] >= 0 else "#7994B2" for i in range(3)], width=0.62)
        ax.set_xticks(range(3), labels=task_effect.index if j >= 2 else ["", "", ""])
        ax.set_ylim(-1.12, 1.12)
        ax.text(0.50, 0.96, metric, transform=ax.transAxes, ha="center", va="top", fontsize=5.8)
        ax.tick_params(labelsize=5.4)
        if j % 2:
            ax.set_yticklabels([])
        for i, raw in enumerate(task_effect[metric]):
            ax.text(i, vals[i] + (0.07 if vals[i] >= 0 else -0.07), f"{raw:+.2f}" if metric == "Jump benefit" else f"{raw:+.3f}",
                    ha="center", va="bottom" if vals[i] >= 0 else "top", fontsize=4.7)

    # d — interpretable failure boundary on the hardest target condition.
    y = np.arange(3)[::-1]
    for yi, truth, pred in zip(y, true_frac, pred_frac):
        ax_d.plot([truth, pred], [yi, yi], color="#B5B5B5", lw=1.3)
        ax_d.scatter(truth, yi, s=28, facecolor="white", edgecolor="#444444", linewidth=0.8,
                     label="True" if yi == 2 else None, zorder=3)
        ax_d.scatter(pred, yi, s=31, color=DC_PSR, edgecolor="white", linewidth=0.4,
                     label="Predicted" if yi == 2 else None, zorder=4)
    ax_d.set_yticks(y, labels=[stage.title() for stage in stages])
    ax_d.set_xlim(-0.02, 1.0)
    ax_d.set_xlabel("Fraction of runs")
    ax_d.grid(axis="x", color="#E8E8E8", lw=0.45)
    ax_d.legend(loc="lower right")
    ax_d.text(0.03, 0.06, "D2-M, seed 42, n = 2,751", transform=ax_d.transAxes, fontsize=5.7, color="#5D5D5D")

    add_panel_caption(fig, ax_a, "a", "Benchmark landscape and progressive domain shift", pad=0.040)
    add_panel_caption(fig, [ax_b, cbar_b.ax], "b", "Backbone-controlled cross-dataset effects", pad=0.030)
    add_panel_caption(fig, axes_c, "c", "DC-PSR relative gains across\ncross-machine tasks", pad=0.042)
    add_panel_caption(fig, ax_d, "d", "D2-M failure boundary:\npredicted middle-stage collapse", pad=0.042)

    sources = []
    for path, columns, aggregation in [
        (D1_SOURCE, ["Method", "Acc", "M_F1", "Smooth", "Jump"], "none; 304-run D1 common universe"),
        (NASA_SOURCE, ["Method", "Acc_mean", "M-F1_mean", "Smooth_mean", "Jump_mean"], "B11/B12 means across original N1–N4 cases"),
        (CROSS_MACHINE_SOURCE, ["task", "Method", "Acc_mean", "M_F1_mean", "Smooth_mean", "Jump_mean"], "B11/B12 five-seed summaries; panel b averages D1-M/D2-M/D3-M"),
        (FAILURE_SOURCE, ["stage_true", "stage_pred_final_name"], "class fractions over all 2,751 seed-42 D2-M test runs"),
    ]:
        sources.append({"path": path, "sha256": sha256(path), "columns": columns,
                        "aggregation": aggregation, "normalization": "signed effect columns normalized only for color/bar scale",
                        "bootstrap": "not newly computed"})
    write_manifest(OUT_DIR / "data_manifest.json", {
        "figure": "Fig.3 Cross-dataset Perspective", "audit_status": "passed",
        "sources": sources,
        "key_values": {"dataset_effects": dataset_effect.round(8).to_dict(orient="index"),
                       "cross_machine_task_effects": task_effect.round(8).to_dict(orient="index"),
                       "D2M_true_stage_fraction": true_frac.round(8).to_dict(),
                       "D2M_predicted_stage_fraction": pred_frac.round(8).to_dict()},
        "warnings": ["NASA uses original N1–N4 summary variability while the cross-machine source uses five-seed task summaries; no pooled significance claim is made.",
                     "Negative Accuracy deltas are retained without clipping or favorable-seed selection."],
    })
    return export_figure(fig, OUT_DIR / "fig3_cross_dataset")


if __name__ == "__main__":
    main()
