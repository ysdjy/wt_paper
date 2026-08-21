from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

from common import (
    CMAP_DELTA,
    METHOD_COLORS,
    OUT,
    ROOT,
    apply_style,
    heatmap,
    panel_label,
    read_csv,
    save_figure,
    write_plot_data,
)


D1_SOURCE = "final_statistical_evidence/results/D1_MAIN_BOOTSTRAP_CI.csv"
NASA_SOURCE = "补充材料/小论文/nasa_dcpsr_results_stageaware_opt/Table_NASA_original_split_mean_std.csv"
CROSS_MACHINE_SOURCE = "experiments_mendeley/04_overall_comparison/summary/overall_comparison_mean_std_by_task.csv"
FAILURE_SOURCE = "experiments_mendeley/07_semantic_consistency/probability_evolution/D2-M_seed42_predictions_test_B11B12.csv"

COLS = ["ΔAcc", "ΔM-F1", "Smooth\nbenefit", "Jump\nbenefit"]


def normalize_columns(values: np.ndarray) -> np.ndarray:
    out = np.zeros_like(values, dtype=float)
    for j in range(values.shape[1]):
        scale = np.nanmax(np.abs(values[:, j]))
        out[:, j] = values[:, j] / scale if scale > 0 else 0.0
    return out


def build_effect_tables():
    d1 = read_csv(D1_SOURCE).set_index("Method")
    phm_b = d1.loc["Multi-task TCN-GRU"]
    phm_d = d1.loc["DC-PSR"]
    phm = np.array([
        phm_d["Acc"] - phm_b["Acc"],
        phm_d["M_F1"] - phm_b["M_F1"],
        phm_b["Smooth"] - phm_d["Smooth"],
        phm_b["Jump"] - phm_d["Jump"],
    ], dtype=float)

    nasa = read_csv(NASA_SOURCE).set_index("Method")
    nasa_b, nasa_d = nasa.loc["B11"], nasa.loc["B12"]
    nasa_effect = np.array([
        nasa_d["Acc_mean"] - nasa_b["Acc_mean"],
        nasa_d["M-F1_mean"] - nasa_b["M-F1_mean"],
        nasa_b["Smooth_mean"] - nasa_d["Smooth_mean"],
        nasa_b["Jump_mean"] - nasa_d["Jump_mean"],
    ], dtype=float)

    cm = read_csv(CROSS_MACHINE_SOURCE)
    cm = cm[cm["Method"].isin(["B11", "B12"])].copy()
    cm["display_method"] = cm["Method"].map({"B11": "Multi-task TCN-GRU", "B12": "DC-PSR"})
    cm_idx = cm.set_index(["task", "Method"])
    task_rows = []
    for task in ["D1-M", "D2-M", "D3-M"]:
        b, d = cm_idx.loc[(task, "B11")], cm_idx.loc[(task, "B12")]
        task_rows.append(
            {
                "task": task,
                "ΔAcc": d["Acc_mean"] - b["Acc_mean"],
                "ΔM-F1": d["M_F1_mean"] - b["M_F1_mean"],
                "Smooth benefit": b["Smooth_mean"] - d["Smooth_mean"],
                "Jump benefit": b["Jump_mean"] - d["Jump_mean"],
            }
        )
    task_effect = pd.DataFrame(task_rows).set_index("task")
    cross_machine = task_effect.mean(axis=0).to_numpy(float)

    dataset_effect = pd.DataFrame(
        np.vstack([phm, nasa_effect, cross_machine]),
        index=["PHM2010", "NASA", "Cross-machine"],
        columns=["ΔAcc", "ΔM-F1", "Smooth benefit", "Jump benefit"],
    )
    return dataset_effect, task_effect


def make_figure():
    apply_style()
    dataset_effect, task_effect = build_effect_tables()
    dataset_norm = normalize_columns(dataset_effect.to_numpy(float))
    task_norm = normalize_columns(task_effect.to_numpy(float))

    dataset_export = dataset_effect.copy()
    for j, col in enumerate(dataset_effect.columns):
        dataset_export[f"normalized_{col}"] = dataset_norm[:, j]
    write_plot_data(dataset_export.reset_index(names="dataset"), "fig3_dataset_effects_vs_backbone.csv")
    task_export = task_effect.copy()
    for j, col in enumerate(task_effect.columns):
        task_export[f"normalized_{col}"] = task_norm[:, j]
    write_plot_data(task_export.reset_index(), "fig3_cross_machine_task_deltas.csv")

    failure = read_csv(FAILURE_SOURCE)
    stages = ["early", "middle", "late"]
    true_frac = failure["stage_true"].value_counts(normalize=True).reindex(stages, fill_value=0.0)
    pred_frac = failure["stage_pred_final_name"].value_counts(normalize=True).reindex(stages, fill_value=0.0)
    failure_export = pd.DataFrame({"stage": [s.title() for s in stages], "true_fraction": true_frac.values,
                                   "predicted_fraction": pred_frac.values})
    write_plot_data(failure_export, "fig3_D2M_seed42_failure_distribution.csv")

    fig = plt.figure(figsize=(7.2, 4.65))
    gs = fig.add_gridspec(2, 3, height_ratios=[0.78, 2.15], width_ratios=[1.12, 1.12, 0.82],
                          hspace=0.42, wspace=0.50)
    ax_a = fig.add_subplot(gs[0, :])
    ax_b = fig.add_subplot(gs[1, 0])
    ax_c = fig.add_subplot(gs[1, 1])
    ax_d = fig.add_subplot(gs[1, 2])

    # a | validation ladder
    ax_a.set_xlim(0, 3)
    ax_a.set_ylim(0, 1)
    ax_a.axis("off")
    boxes = [
        (0.08, "PHM2010", "Cross-condition", "3 operating conditions", "#EAF1F5"),
        (1.08, "NASA milling", "Heterogeneous cross-case", "16 cases", "#E7F2EF"),
        (2.08, "Cross-machine milling", "Machine + sensing shift", "3 machines", "#F6E8DF"),
    ]
    for x, name, role, count, color in boxes:
        patch = mpl.patches.FancyBboxPatch((x, 0.16), 0.80, 0.64,
                                           boxstyle="round,pad=0.018,rounding_size=0.025",
                                           facecolor=color, edgecolor="#6E7377", linewidth=0.7)
        ax_a.add_patch(patch)
        ax_a.text(x + 0.40, 0.62, name, ha="center", va="center", fontsize=8.0, fontweight="bold")
        ax_a.text(x + 0.40, 0.43, role, ha="center", va="center", fontsize=6.6, color="#42484D")
        ax_a.text(x + 0.40, 0.27, count, ha="center", va="center", fontsize=6.2, color="#5C6368")
    for x in [0.91, 1.91]:
        ax_a.annotate("", xy=(x + 0.13, 0.48), xytext=(x, 0.48),
                      arrowprops=dict(arrowstyle="-|>", color="#7A7A7A", lw=1.0))
    ax_a.text(1.50, 0.91, "Progressive domain shift", ha="center", va="center",
              fontsize=6.5, color="#666666")
    panel_label(ax_a, "a", x=-0.02, y=0.86)

    # b | aggregate directional effects
    raw_b = dataset_effect.to_numpy(float)
    ann_b = np.empty(raw_b.shape, dtype=object)
    for i in range(raw_b.shape[0]):
        for j in range(raw_b.shape[1]):
            ann_b[i, j] = f"{raw_b[i, j]:+.3f}" if j < 3 else f"{raw_b[i, j]:+.2f}"
    heatmap(ax_b, dataset_norm, COLS, dataset_effect.index.tolist(), cmap=CMAP_DELTA,
            vmin=-1, vmax=1, cbar_label="Normalized directional improvement vs. backbone",
            annotate=ann_b, annotate_fmt="{}", cbar_orientation="horizontal")
    ax_b.set_title("Backbone-controlled effects", loc="left", pad=6)
    panel_label(ax_b, "b", x=-0.23)

    # c | cross-machine task-level effects
    raw_c = task_effect.to_numpy(float)
    ann_c = np.empty(raw_c.shape, dtype=object)
    for i in range(raw_c.shape[0]):
        for j in range(raw_c.shape[1]):
            ann_c[i, j] = f"{raw_c[i, j]:+.3f}" if j < 3 else f"{raw_c[i, j]:+.1f}"
    heatmap(ax_c, task_norm, COLS, task_effect.index.tolist(), cmap=CMAP_DELTA,
            vmin=-1, vmax=1, cbar_label="Column-normalized directional effect",
            annotate=ann_c, annotate_fmt="{}", cbar_orientation="horizontal")
    ax_c.set_title("Cross-machine task deltas", loc="left", pad=6)
    panel_label(ax_c, "c", x=-0.19)

    # d | D2-M middle-collapse boundary
    y = np.arange(3)[::-1]
    for yi, t, p in zip(y, true_frac.values, pred_frac.values):
        ax_d.plot([t, p], [yi, yi], color="#B0B0B0", lw=1.2, zorder=1)
        ax_d.scatter(t, yi, s=22, facecolor="white", edgecolor="#4D4D4D", linewidth=0.8,
                     label="True" if yi == y[0] else None, zorder=3)
        ax_d.scatter(p, yi, s=27, color=METHOD_COLORS["DC-PSR"], edgecolor="white", linewidth=0.4,
                     label="Predicted" if yi == y[0] else None, zorder=4)
    ax_d.set_yticks(y, labels=[s.title() for s in stages])
    ax_d.set_xlim(-0.03, 1.0)
    ax_d.set_xlabel("Fraction of runs")
    ax_d.set_title("D2-M failure boundary", loc="left", pad=6)
    ax_d.legend(loc="lower right", fontsize=5.8, handletextpad=0.4)
    ax_d.grid(axis="x", color="#E8E8E8", lw=0.45)
    ax_d.text(0.03, -0.38, "M1+M3 → M2; seed 42", transform=ax_d.transAxes,
              fontsize=5.8, color="#5C5C5C")
    panel_label(ax_d, "d", x=-0.24)

    fig.subplots_adjust(left=0.105, right=0.985, top=0.965, bottom=0.16)
    return fig


def main():
    return save_figure(make_figure(), OUT / "fig3_cross_dataset", "fig3_cross_dataset")


if __name__ == "__main__":
    main()
