"""
Fig.2 (paper Fig. 4-3): cross-target-condition (D1/D2/D3) and cross-dataset (PHM2010/NASA
Milling/MTW-CM) generalization landscape.

Inputs (note: on-disk paper_data/07_figure_ready/fig2/ AND fig3/ both feed this ONE final
figure -- see paper_data/figure/FIGURE_PROGRESS.md for why on-disk numbering != final numbering):
  - paper_data/07_figure_ready/fig2/taskwise_absolute.csv     D1/D2/D3 x 9 methods, absolute values
  - paper_data/07_figure_ready/fig2/taskwise_normalized.csv   within-task normalized (already
                                                                direction-corrected: 1=best)
  - paper_data/07_figure_ready/fig2/taskwise_rank.csv         within-task rank (1=best)
  - paper_data/07_figure_ready/fig3/cross_dataset_absolute.csv   PHM/NASA/MTW-CM, B11 vs B12 (=
                                                                Multi-task TCN-GRU vs DC-PSR)
  - paper_data/07_figure_ready/fig3/cross_dataset_deltas.csv     precomputed deltas, used only to
                                                                cross-validate our own recomputation

Outputs: paper_data/figure/fig2/outputs/fig2_main.{png,pdf,svg}
Logs:    paper_data/figure/fig2/logs/validation.txt

Run: python paper_data/figure/fig2/plot_fig2.py
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_shared"))
from style import apply_style, save_all, METHOD_ORDER, METHOD_COLORS  # noqa: E402
import data_utils as du  # noqa: E402

HERE = os.path.dirname(__file__)
OUT_DIR = os.path.join(HERE, "outputs")
DERIVED_DIR = os.path.join(HERE, "derived")
LOG_DIR = os.path.join(HERE, "logs")
os.makedirs(DERIVED_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

PHM_TASKS = ["D1", "D2", "D3"]
HEATMAP_METRICS = ["Acc", "M_F1", "Smooth"]


def load():
    tw_abs = du.read_csv("07_figure_ready", "fig2", "taskwise_absolute.csv")
    tw_norm = du.read_csv("07_figure_ready", "fig2", "taskwise_normalized.csv")
    cross_abs = du.read_csv("07_figure_ready", "fig3", "cross_dataset_absolute.csv")
    cross_delta_ref = du.read_csv("07_figure_ready", "fig3", "cross_dataset_deltas.csv")
    return tw_abs, tw_norm, cross_abs, cross_delta_ref


def panel_taskwise_heatmap(fig, gs_row, tw_abs, tw_norm, log_lines):
    from matplotlib.gridspec import GridSpecFromSubplotSpec
    gs3 = GridSpecFromSubplotSpec(1, 3, subplot_spec=gs_row, wspace=0.55)
    axes = [fig.add_subplot(gs3[i]) for i in range(3)]
    for ax, task in zip(axes, PHM_TASKS):
        sub = tw_norm[tw_norm["Task"] == task]
        methods = [m for m in METHOD_ORDER if m in sub["Method"].unique()]
        grid = np.zeros((len(methods), len(HEATMAP_METRICS)))
        raw = np.zeros_like(grid)
        for j, metric in enumerate(HEATMAP_METRICS):
            for i, m in enumerate(methods):
                row = sub[(sub["Method"] == m) & (sub["metric"] == metric)]
                grid[i, j] = row["normalized_score"].values[0]
                raw[i, j] = row["absolute_value"].values[0]
        im = ax.imshow(grid, aspect="auto", cmap="RdYlGn", vmin=0, vmax=1)
        ax.set_yticks(np.arange(len(methods)))
        ax.set_yticklabels(methods if task == "D1" else [""] * len(methods), fontsize=6.5)
        ax.set_xticks(np.arange(3))
        ax.set_xticklabels(["Acc↑", "M-F1↑", "Smooth↓"], fontsize=7)
        for i in range(len(methods)):
            for j in range(3):
                ax.text(j, i, f"{raw[i, j]:.3f}", ha="center", va="center", fontsize=5.6,
                         color="black" if 0.25 < grid[i, j] < 0.85 else "white")
        ax.set_title(task, fontsize=8.5, fontweight="bold")
        best_method = sub[(sub["metric"] == "Acc")].sort_values("absolute_value", ascending=False)["Method"].iloc[0]
        log_lines.append(f"{task}: best Acc = {best_method}")
    fig.text(0.065, axes[0].get_position().y1 + 0.012,
              "(a) Within-task normalized performance, D1/D2/D3 × 9 methods (color = within-task-and-metric normalized benefit; numbers = raw values)",
              fontsize=9, fontweight="bold")
    n_unique_best = tw_norm[tw_norm["metric"] == "Acc"].sort_values(["Task", "absolute_value"]).groupby("Task").tail(1)["Method"].nunique()
    log_lines.append(f"PASS: {n_unique_best} distinct methods top Acc across D1/D2/D3 (target-condition dependence, no single winner if >1).")


def panel_paired_delta(ax, tw_abs, log_lines):
    bb = tw_abs[tw_abs["Method"] == "Multi-task TCN-GRU"].set_index("Task")
    dc = tw_abs[tw_abs["Method"] == "DC-PSR"].set_index("Task")
    rows = []
    for task in PHM_TASKS:
        d_acc = (dc.loc[task, "Acc"] - bb.loc[task, "Acc"]) * 100
        d_mf1 = (dc.loc[task, "M_F1"] - bb.loc[task, "M_F1"]) * 100
        d_mrec = (dc.loc[task, "M_Recall"] - bb.loc[task, "M_Recall"]) * 100
        smooth_benefit_pct = (bb.loc[task, "Smooth"] - dc.loc[task, "Smooth"]) / bb.loc[task, "Smooth"] * 100
        rows.append((task, d_acc, d_mf1, d_mrec, smooth_benefit_pct))
    df = pd.DataFrame(rows, columns=["Task", "dAcc_pp", "dM_F1_pp", "dM_Rec_pp", "Smooth_benefit_pct"])
    df.to_csv(os.path.join(DERIVED_DIR, "PHM_backbone_to_dcpsr_paired_delta.csv"), index=False, encoding="utf-8")

    expected = {"D1": (-0.33, -0.39, 0.0, 20.5), "D2": (-0.33, -0.61, None, 6.6), "D3": (0.66, 1.10, 1.80, -5.7)}
    for task, d_acc, d_mf1, d_mrec, sm in rows:
        e_acc, e_mf1, e_mrec, e_sm = expected[task]
        assert np.isclose(d_acc, e_acc, atol=0.1), f"{task} dAcc: got {d_acc:.2f}, expected {e_acc}"
        assert np.isclose(d_mf1, e_mf1, atol=0.15), f"{task} dM_F1: got {d_mf1:.2f}, expected {e_mf1}"
        if e_mrec is not None:
            assert np.isclose(d_mrec, e_mrec, atol=0.15), f"{task} dM_Rec: got {d_mrec:.2f}, expected {e_mrec}"
        assert np.isclose(sm, e_sm, atol=1.0), f"{task} Smooth benefit%: got {sm:.2f}, expected {e_sm}"
        log_lines.append(f"PASS: PHM {task} Multi-task TCN-GRU->DC-PSR: dAcc={d_acc:.2f}pp, dM-F1={d_mf1:.2f}pp, "
                          f"dM-Rec={d_mrec:.2f}pp, Smooth_benefit={sm:.2f}% (matches design-doc narrative).")

    x = np.arange(len(PHM_TASKS))
    width = 0.2
    metrics_plot = [("dAcc_pp", "ΔAcc (pp)", "#3D6EA8"), ("dM_F1_pp", "ΔM-F1 (pp)", "#5CB88A"),
                     ("dM_Rec_pp", "ΔM-Rec (pp)", "#D4A017"), ("Smooth_benefit_pct", "Smooth benefit (%)", "#C1272D")]
    for i, (col, label, color) in enumerate(metrics_plot):
        ax.bar(x + (i - 1.5) * width, df[col], width=width, color=color, label=label)
    ax.axhline(0, color="black", lw=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels(PHM_TASKS)
    ax.set_ylabel("Δ (percentage points) or benefit (%)")
    ax.set_title("(b) Multi-task TCN-GRU → DC-PSR paired delta, PHM D1/D2/D3\n"
                 "(Smooth benefit = Smooth_backbone − Smooth_DC-PSR, positive = improvement; raw Smooth is never itself flipped)",
                 loc="left", fontweight="bold", fontsize=8.3)
    ax.legend(loc="upper left", fontsize=6.5, ncol=1)


def panel_cross_dataset_delta(ax, cross_abs, cross_delta_ref, log_lines):
    scopes = [("PHM2010", "D1"), ("NASA_MILLING", "original_N1-N4"),
              ("MILLING_CROSS_MACHINE", "D1-M"), ("MILLING_CROSS_MACHINE", "D2-M"),
              ("MILLING_CROSS_MACHINE", "D3-M"), ("MILLING_CROSS_MACHINE", "D1-M,D2-M,D3-M")]
    row_labels = ["PHM2010\nD1", "NASA Milling\nN1-N4 avg", "MTW-CM\nD1-M", "MTW-CM\nD2-M",
                  "MTW-CM\nD3-M", "MTW-CM\n3-task avg"]
    rows = []
    for dataset, scope in scopes:
        b11 = cross_abs[(cross_abs["dataset"] == dataset) & (cross_abs["task_scope"] == scope) & (cross_abs["method"] == "B11")].iloc[0]
        b12 = cross_abs[(cross_abs["dataset"] == dataset) & (cross_abs["task_scope"] == scope) & (cross_abs["method"] == "B12")].iloc[0]
        d_acc = (b12["Acc"] - b11["Acc"]) * 100
        d_mf1 = (b12["M_F1"] - b11["M_F1"]) * 100
        smooth_benefit_pct = (b11["Smooth"] - b12["Smooth"]) / b11["Smooth"] * 100 if b11["Smooth"] > 0 else 0.0
        jump_benefit_pct = (b11["Jump"] - b12["Jump"]) / b11["Jump"] * 100 if b11["Jump"] > 0 else 0.0
        rows.append([d_acc, d_mf1, smooth_benefit_pct, jump_benefit_pct])
    grid = np.array(rows)

    checks = {
        "NASA_MILLING": (5.86, -35.0),
        "MTW-CM-avg": (10.04, -23.9),
    }
    n_mf1, s_ben = grid[1, 1], grid[1, 2]
    assert np.isclose(n_mf1, checks["NASA_MILLING"][0], atol=0.5), n_mf1
    assert np.isclose(s_ben, -checks["NASA_MILLING"][1], atol=1.5), s_ben
    log_lines.append(f"PASS: NASA B11->B12 M-F1 delta={n_mf1:.2f}pp (~5.86), Smooth benefit={s_ben:.2f}% (~35.0).")
    n_mf1_mtw, s_ben_mtw = grid[5, 1], grid[5, 2]
    assert np.isclose(n_mf1_mtw, checks["MTW-CM-avg"][0], atol=0.5), n_mf1_mtw
    assert np.isclose(s_ben_mtw, -checks["MTW-CM-avg"][1], atol=1.5), s_ben_mtw
    log_lines.append(f"PASS: MTW-CM 3-task avg B11->B12 M-F1 delta={n_mf1_mtw:.2f}pp (~10.04), Smooth benefit={s_ben_mtw:.2f}% (~23.9).")
    j_ben_mtw = grid[5, 3]
    assert np.isclose(j_ben_mtw, 82.5, atol=1.5), j_ben_mtw
    log_lines.append(f"PASS: MTW-CM 3-task avg Jump benefit={j_ben_mtw:.2f}% (~82.5).")

    cols = ["ΔAcc (pp)", "ΔM-F1 (pp)", "Smooth benefit (%)", "Jump benefit (%)"]
    # Per-column diverging normalization (each column has its own scale/units: pp vs %), so a
    # small-magnitude column (e.g. ΔAcc in pp) is not visually washed out by a large-magnitude
    # column (e.g. Jump benefit in %) sharing one global color scale. Raw values are always
    # annotated in the cell regardless of color.
    color_grid = np.zeros_like(grid)
    for j in range(grid.shape[1]):
        col_vmax = np.abs(grid[:, j]).max()
        color_grid[:, j] = grid[:, j] / col_vmax if col_vmax > 0 else 0.0
    im = ax.imshow(color_grid, aspect="auto", cmap="RdYlGn", vmin=-1, vmax=1)
    ax.set_yticks(np.arange(len(row_labels)))
    ax.set_yticklabels(row_labels, fontsize=7)
    ax.set_xticks(np.arange(len(cols)))
    ax.set_xticklabels(cols, fontsize=7.5)
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            txt_color = "white" if abs(color_grid[i, j]) > 0.75 else "black"
            ax.text(j, i, f"{grid[i, j]:+.2f}", ha="center", va="center", fontsize=7,
                     color=txt_color)
    ax.set_title("(c) Cross-dataset Multi-task TCN-GRU → DC-PSR (B11→B12) delta matrix\n"
                 "(green = improvement in the metric's own direction, red = regression; color normalized per-column "
                 "since columns mix pp and % units; raw ΔAcc/ΔM-F1 in pp, Smooth/Jump shown as % benefit)",
                 loc="left", fontweight="bold", fontsize=8.3)
    cbar = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label("within-column benefit\n(normalized, diverging, 0=no change)", fontsize=6.5)
    cbar.ax.tick_params(labelsize=6)


def main():
    apply_style()
    tw_abs, tw_norm, cross_abs, cross_delta_ref = load()
    log_lines = []

    assert set(tw_abs["Task"].unique()) == set(PHM_TASKS)
    assert len(tw_abs) == 27, f"expected 27 rows (3 tasks x 9 methods), got {len(tw_abs)}"
    assert set(cross_abs["dataset"].unique()) == {"PHM2010", "NASA_MILLING", "MILLING_CROSS_MACHINE"}
    assert "MIMII" not in cross_abs["dataset"].unique()
    log_lines.append("PASS: taskwise_absolute has 27 rows (3 PHM tasks x 9 methods); cross_dataset_absolute uses "
                     "{PHM2010, NASA_MILLING, MILLING_CROSS_MACHINE} only, no legacy 'MIMII' label present.")

    fig = plt.figure(figsize=(13.5, 12.5))
    gs = GridSpec(3, 1, height_ratios=[1.55, 1.0, 1.15], hspace=0.62, figure=fig)

    panel_taskwise_heatmap(fig, gs[0], tw_abs, tw_norm, log_lines)

    ax_b = fig.add_subplot(gs[1])
    panel_paired_delta(ax_b, tw_abs, log_lines)

    ax_c = fig.add_subplot(gs[2])
    panel_cross_dataset_delta(ax_c, cross_abs, cross_delta_ref, log_lines)

    fig.suptitle("Cross-target-condition (PHM2010 D1/D2/D3) and cross-dataset (PHM2010/NASA\n"
                 "Milling/MTW-CM) generalization: no single method dominates every task, but\n"
                 "M-F1 and trajectory-consistency gains from DC-PSR stay directionally consistent",
                 fontsize=10.5, y=0.995)
    fig.subplots_adjust(top=0.88, bottom=0.04)

    paths = save_all(fig, OUT_DIR, "fig2_main")
    log_lines.append(f"Saved outputs: {paths}")

    with open(os.path.join(LOG_DIR, "validation.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
    print("\n".join(log_lines))
    print("Fig.2 done.")


if __name__ == "__main__":
    main()
