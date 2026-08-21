from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from common import (
    CMAP_ABSOLUTE,
    METHOD_ORDER,
    OUT,
    apply_style,
    clean_method_names,
    heatmap,
    minmax,
    panel_label,
    rank_desc,
    read_csv,
    save_figure,
    write_plot_data,
)


SOURCE = "final_statistical_evidence/results/TRANSFER_TASKS_D1_D2_D3.csv"
TASKS = ["D1", "D2", "D3"]


def metric_pack(df: pd.DataFrame, metric: str, higher_better: bool):
    raw = df.pivot(index="Method", columns="Task", values=metric).loc[METHOD_ORDER, TASKS]
    score = raw.copy()
    ranks = raw.copy()
    for task in TASKS:
        vals = raw[task].to_numpy(float)
        s = minmax(vals, higher_better=higher_better)
        score[task] = s
        ranks[task] = rank_desc(s)
    return raw, score, ranks.astype(int)


def make_figure():
    apply_style()
    df = clean_method_names(read_csv(SOURCE))
    for col in ["Acc", "M_F1", "Smooth"]:
        df[col] = pd.to_numeric(df[col])

    specs = [
        ("Acc", True, "Within-task normalized Acc", "Relative Accuracy"),
        ("M_F1", True, "Within-task normalized M-F1", "Relative M-F1"),
        ("Smooth", False, "Within-task normalized consistency\n(from Smooth)", "Relative consistency"),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(7.2, 4.25), gridspec_kw={"wspace": 0.28})
    export_parts = []
    for k, (metric, higher, cbar_label, title) in enumerate(specs):
        raw, score, ranks = metric_pack(df, metric, higher)
        long = raw.stack().rename("raw_value").reset_index()
        long["normalized_score"] = score.stack().to_numpy()
        long["rank"] = ranks.stack().to_numpy()
        long["metric"] = metric
        long["normalization"] = (
            "(x-min_task)/(max_task-min_task)" if higher
            else "(max_task-x)/(max_task-min_task)"
        )
        export_parts.append(long)
        annotations = np.vectorize(lambda x: f"#{int(x)}")(ranks.to_numpy())
        heatmap(
            axes[k],
            score.to_numpy(float),
            TASKS,
            METHOD_ORDER,
            cmap=CMAP_ABSOLUTE,
            vmin=0,
            vmax=1,
            cbar_label=cbar_label,
            annotate=annotations,
            annotate_fmt="{}",
            show_ylabels=(k == 0),
            outline_row=0,
        )
        axes[k].set_title(title, loc="left", pad=7)
        panel_label(axes[k], chr(ord("a") + k), x=-0.20 if k == 0 else -0.10)

    export = pd.concat(export_parts, ignore_index=True)
    write_plot_data(export, "fig2_taskwise_normalized_scores.csv")
    fig.text(0.5, 0.012,
             "Cell labels are within-task ranks; colors are relative scores, not absolute metric values.",
             ha="center", va="bottom", fontsize=6.2, color="#4D4D4D")
    fig.subplots_adjust(left=0.205, right=0.985, top=0.91, bottom=0.20)
    return fig


def main():
    return save_figure(make_figure(), OUT / "fig2_cross_condition", "fig2_cross_condition")


if __name__ == "__main__":
    main()
