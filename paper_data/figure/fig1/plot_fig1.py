"""
Fig.1 (paper Fig. 4-2): PHM2010 D1 core-task overall performance, representative confusion
patterns, and middle-stage/consistency diagnostics.

Inputs:
  - paper_data/07_figure_ready/fig1/D1_main_metrics.csv           9-method authoritative metrics + bootstrap CI
  - paper_data/07_figure_ready/fig1/accuracy_consistency_points.csv  Acc/Smooth pairs for Pareto panel
  - paper_data/07_figure_ready/fig1/B11_B12_controlled_comparison.csv  paired B11/B12 bootstrap CI
  - paper_data/07_figure_ready/fig2/taskwise_absolute.csv (Task==D1)  E_F1/L_F1/M_Precision (classwise completion)
  - paper_data/01_PHM2010/01_main_D1/predictions_common_universe/D1_<method>_304runs.csv (9 files)
      sample-level true_stage/pred_stage -> confusion matrices, recomputed from labels only.

Outputs: paper_data/figure/fig1/outputs/fig1_main.{png,pdf,svg}
Derived: paper_data/figure/fig1/derived/D1_heatmap_complete.csv
Logs:    paper_data/figure/fig1/logs/validation.txt

Run: python paper_data/figure/fig1/plot_fig1.py
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_shared"))
from style import apply_style, save_all, METHOD_ORDER, METHOD_COLORS, REPRESENTATIVE_METHODS, STAGE_ORDER, STAGE_COLORS  # noqa: E402
import data_utils as du  # noqa: E402

HERE = os.path.dirname(__file__)
OUT_DIR = os.path.join(HERE, "outputs")
DERIVED_DIR = os.path.join(HERE, "derived")
LOG_DIR = os.path.join(HERE, "logs")
os.makedirs(DERIVED_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

METHOD_ID_MAP = {
    "RF": "rf", "TCN-GRU": "tcn_gru", "Multi-task TCN-GRU": "multitask_tcn_gru",
    "DC-PSR": "dc_psr", "HTT-Net (adapted)": "htt_net",
    "Multi-source Attention": "multi_source_attention", "MTF-AViTK": "mtf_avitk",
    "Dynamic GIN + TGP": "dynamic_gin_tgp", "DP2Net-adapted": "dp2net_adapted",
}

HEATMAP_METRICS = [
    ("Acc", "higher", "Acc"), ("MacroF1", "higher", "Macro-F1"),
    ("E_F1", "higher", "E-F1"), ("M_F1", "higher", "M-F1"), ("L_F1", "higher", "L-F1"),
    ("M_Precision", "higher", "M-Pre"), ("M_Rec", "higher", "M-Rec"),
    ("M_to_E", "lower", "M→E"), ("M_to_L", "lower", "M→L"),
    ("Rev", "lower", "Rev"), ("Jump", "lower", "Jump"), ("Smooth", "lower", "Smooth"),
]


def load():
    d1 = du.read_csv("07_figure_ready", "fig1", "D1_main_metrics.csv")
    acc_cons = du.read_csv("07_figure_ready", "fig1", "accuracy_consistency_points.csv")
    ci_pair = du.read_csv("07_figure_ready", "fig1", "B11_B12_controlled_comparison.csv")
    taskwise = du.read_csv("07_figure_ready", "fig2", "taskwise_absolute.csv")
    tw_d1 = taskwise[taskwise["Task"] == "D1"][["Method", "E_F1", "L_F1", "M_Precision"]]
    return d1, acc_cons, ci_pair, tw_d1


def load_predictions(method_display):
    mid = METHOD_ID_MAP[method_display]
    df = du.read_csv("01_PHM2010", "01_main_D1", "predictions_common_universe", f"D1_{mid}_304runs.csv")
    return df


def build_heatmap_table(d1, tw_d1, log_lines):
    merged = d1.merge(tw_d1, on="Method", how="left")
    assert len(merged) == 9, f"expected 9 methods, got {len(merged)}"
    assert merged["E_F1"].notna().all() and merged["L_F1"].notna().all() and merged["M_Precision"].notna().all()
    merged["Method"] = pd.Categorical(merged["Method"], categories=METHOD_ORDER, ordered=True)
    merged = merged.sort_values("Method").reset_index(drop=True)
    log_lines.append(f"PASS: merged D1_main_metrics.csv with taskwise_absolute.csv(Task==D1) -> {len(merged)} rows (expected 9), classwise fields non-null.")
    merged.to_csv(os.path.join(DERIVED_DIR, "D1_heatmap_complete.csv"), index=False, encoding="utf-8")
    return merged


def validate_headline(merged, log_lines):
    mt = merged[merged["Method"] == "Multi-task TCN-GRU"].iloc[0]
    dc = merged[merged["Method"] == "DC-PSR"].iloc[0]
    checks = [
        ("Multi-task TCN-GRU Acc", mt["Acc"], 0.99013, 2e-4),
        ("Multi-task TCN-GRU MacroF1", mt["MacroF1"], 0.99023, 2e-4),
        ("Multi-task TCN-GRU M_F1", mt["M_F1"], 0.98824, 2e-4),
        ("Multi-task TCN-GRU M_Rec", mt["M_Rec"], 0.97674, 2e-4),
        ("Multi-task TCN-GRU Smooth", mt["Smooth"], 0.02359, 2e-4),
        ("DC-PSR Acc", dc["Acc"], 0.98684, 2e-4),
        ("DC-PSR MacroF1", dc["MacroF1"], 0.98710, 2e-4),
        ("DC-PSR M_F1", dc["M_F1"], 0.98438, 2e-4),
        ("DC-PSR M_Rec", dc["M_Rec"], 0.97674, 2e-4),
        ("DC-PSR Smooth", dc["Smooth"], 0.01876, 2e-4),
    ]
    for name, actual, expected, atol in checks:
        assert np.isclose(actual, expected, atol=atol), f"{name}: got {actual}, expected {expected}"
        log_lines.append(f"PASS: {name} = {actual:.5f} (expected ≈{expected})")


def panel_heatmap(ax, merged):
    n_methods = len(merged)
    n_metrics = len(HEATMAP_METRICS)
    grid = np.zeros((n_methods, n_metrics))
    raw = np.zeros((n_methods, n_metrics))
    for j, (col, direction, _) in enumerate(HEATMAP_METRICS):
        vals = merged[col].values.astype(float)
        raw[:, j] = vals
        vmin, vmax = vals.min(), vals.max()
        norm = np.ones_like(vals) * 0.5 if vmax - vmin < 1e-12 else (vals - vmin) / (vmax - vmin)
        if direction == "lower":
            norm = 1 - norm
        grid[:, j] = norm
    im = ax.imshow(grid, aspect="auto", cmap="RdYlGn", vmin=0, vmax=1)
    ax.set_yticks(np.arange(n_methods))
    ax.set_yticklabels(merged["Method"].tolist())
    ax.set_xticks(np.arange(n_metrics))
    ax.set_xticklabels([f"{lab}{'↑' if d=='higher' else '↓'}" for _, d, lab in HEATMAP_METRICS], rotation=0)
    for i in range(n_methods):
        for j in range(n_metrics):
            col = HEATMAP_METRICS[j][0]
            v = raw[i, j]
            txt = f"{int(v)}" if col in ("Rev", "Jump") else f"{v:.3f}"
            ax.text(j, i, txt, ha="center", va="center", fontsize=6.0,
                     color="black" if 0.25 < grid[i, j] < 0.85 else "white")
    for i, m in enumerate(merged["Method"]):
        if m == "DC-PSR":
            ax.get_yticklabels()[i].set_color(METHOD_COLORS["DC-PSR"])
            ax.get_yticklabels()[i].set_fontweight("bold")
        elif m == "Multi-task TCN-GRU":
            ax.get_yticklabels()[i].set_fontweight("bold")
    ax.set_title("(a) 9-method × metric performance landscape on PHM2010 D1 (color = within-column normalized benefit; numbers = raw values)",
                 loc="left", fontweight="bold")
    cbar = plt.colorbar(im, ax=ax, fraction=0.018, pad=0.008)
    cbar.set_label("within-column\nbenefit (1=best)", fontsize=6.5)
    cbar.ax.tick_params(labelsize=6)


def panel_pareto(ax, acc_cons):
    for _, r in acc_cons.iterrows():
        color = METHOD_COLORS.get(r["Method"], "#888888")
        emphasize = r["Method"] in ("DC-PSR", "Multi-task TCN-GRU")
        ax.scatter(r["Acc"] * 100, r["Smooth"], s=70 if emphasize else 40,
                   color=color, edgecolor="black" if emphasize else "none", linewidth=0.8,
                   zorder=3 if emphasize else 2, label=r["Method"])
        dx, dy = 0.3, 0.003
        if r["Method"] == "DC-PSR":
            dx, dy = -8.0, 0.006
        elif r["Method"] == "Multi-task TCN-GRU":
            dx, dy = -14.5, -0.010
        ax.annotate(r["Method"], (r["Acc"] * 100 + dx, r["Smooth"] + dy), fontsize=6.2, color=color)
    ax.set_xlabel("Accuracy % (higher better →)")
    ax.set_ylabel("Smooth (lower better ↑ = worse)")
    ax.invert_yaxis()
    ax.set_title("(b) Accuracy–consistency trade-off", loc="left", fontweight="bold")
    ax.annotate("better\n(high Acc,\nlow Smooth)", xy=(0.96, 0.06), xycoords="axes fraction",
                fontsize=6.5, ha="right", color="#3D6EA8")


def panel_ci_strip(ax, ci_pair, d1):
    reps = ["RF", "MTF-AViTK", "Multi-task TCN-GRU", "DC-PSR"]
    rows = []
    for m in reps:
        if m in ci_pair["Method"].values:
            rows.append(ci_pair[ci_pair["Method"] == m].iloc[0])
        else:
            rows.append(d1[d1["Method"] == m].iloc[0])
    metrics = [("Acc", "Acc_CI_low", "Acc_CI_high"), ("MacroF1", "MacroF1_CI_low", "MacroF1_CI_high"),
               ("M_F1", "M_F1_CI_low", "M_F1_CI_high")]
    y_positions = np.arange(len(reps))
    offsets = [-0.22, 0.0, 0.22]
    metric_colors = {"Acc": "#3D6EA8", "MacroF1": "#5CB88A", "M_F1": "#C1272D"}
    for (metric, lo_col, hi_col), off in zip(metrics, offsets):
        for yi, r in zip(y_positions, rows):
            lo, hi, mid = r[lo_col] * 100, r[hi_col] * 100, r[metric] * 100
            ax.plot([lo, hi], [yi + off, yi + off], color=metric_colors[metric], lw=2.2, solid_capstyle="round")
            ax.plot(mid, yi + off, "o", color=metric_colors[metric], ms=3.5, mec="black", mew=0.3)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(reps)
    ax.set_xlabel("% (95% moving-block bootstrap CI)")
    ax.set_title("(c) Bootstrap 95% CI, representative methods", loc="left", fontweight="bold")
    handles = [plt.Line2D([0], [0], color=c, lw=2.2, label=lab) for lab, c in
               [("Acc", metric_colors["Acc"]), ("Macro-F1", metric_colors["MacroF1"]), ("M-F1", metric_colors["M_F1"])]]
    ax.legend(handles=handles, loc="lower left", fontsize=6.5)


def panel_confusion(fig, gs_row, predictions_by_method, log_lines):
    axes = [fig.add_subplot(gs_row[i]) for i in range(4)]
    for ax, method in zip(axes, REPRESENTATIVE_METHODS):
        df = predictions_by_method[method]
        counts, row_norm = du.confusion_counts(df["true_stage"].values, df["pred_stage"].values, labels=STAGE_ORDER)
        assert counts.sum() == 304, f"{method}: expected 304 samples, got {counts.sum()}"
        im = ax.imshow(row_norm, cmap="Blues", vmin=0, vmax=1)
        for i in range(3):
            for j in range(3):
                color = "white" if row_norm[i, j] > 0.6 else "black"
                ax.text(j, i, f"{row_norm[i, j]:.3f}\n({counts[i, j]})", ha="center", va="center",
                         fontsize=6.0, color=color)
        ax.set_xticks(range(3)); ax.set_xticklabels(["E", "M", "L"], fontsize=7)
        ax.set_yticks(range(3)); ax.set_yticklabels(["E", "M", "L"], fontsize=7)
        title_color = METHOD_COLORS.get(method, "black")
        ax.set_title(method, fontsize=7.8, color=title_color, fontweight="bold")
        ax.set_xlabel("Predicted", fontsize=6.5)
    axes[0].set_ylabel("True", fontsize=6.5)
    log_lines.append("PASS: all 4 representative confusion matrices sum to 304 samples, row-normalized, labels fixed order [early, middle, late].")
    fig.text(0.065, axes[0].get_position().y1 + 0.012,
              "(d) Representative confusion matrices (row-normalized; cell = proportion, (n) = count)",
              fontsize=9, fontweight="bold")


def panel_middle_diagnostics(ax, merged):
    reps = ["RF", "MTF-AViTK", "Multi-task TCN-GRU", "DC-PSR"]
    sub = merged[merged["Method"].isin(reps)].copy()
    sub["Method"] = pd.Categorical(sub["Method"], categories=reps, ordered=True)
    sub = sub.sort_values("Method")
    metrics = [("M_Precision", "M-Pre", "higher"), ("M_Rec", "M-Rec", "higher"),
               ("M_to_E", "M→E", "lower"), ("M_to_L", "M→L", "lower"),
               ("Smooth", "Smooth", "lower")]
    x = np.arange(len(metrics))
    width = 0.2
    for i, m in enumerate(reps):
        r = sub[sub["Method"] == m].iloc[0]
        vals = [r[c] for c, _, _ in metrics]
        ax.bar(x + (i - 1.5) * width, vals, width=width, color=METHOD_COLORS[m], label=m)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{lab} {'↑' if d=='higher' else '↓'}" for _, lab, d in metrics])
    ax.set_ylabel("Value (see arrow for direction)")
    ax.set_title("(e) Middle-stage & trajectory-consistency diagnostics, representative methods", loc="left", fontweight="bold")
    ax.legend(loc="upper right", ncol=2, fontsize=6.3)


def main():
    apply_style()
    d1, acc_cons, ci_pair, tw_d1 = load()
    log_lines = []

    merged = build_heatmap_table(d1, tw_d1, log_lines)
    validate_headline(merged, log_lines)

    predictions_by_method = {m: load_predictions(m) for m in REPRESENTATIVE_METHODS}
    for m, df in predictions_by_method.items():
        assert len(df) == 304, f"{m}: expected 304 rows, got {len(df)}"
        assert set(df["true_stage"].unique()) <= set(STAGE_ORDER)
    log_lines.append("PASS: all 4 representative prediction files have 304 rows with valid stage labels.")

    fig = plt.figure(figsize=(13.5, 15.5))
    gs = GridSpec(4, 4, height_ratios=[1.35, 1.0, 1.05, 0.95], hspace=0.62, wspace=0.35, figure=fig)

    ax_heat = fig.add_subplot(gs[0, :])
    panel_heatmap(ax_heat, merged)

    ax_pareto = fig.add_subplot(gs[1, :2])
    panel_pareto(ax_pareto, acc_cons)
    ax_ci = fig.add_subplot(gs[1, 2:])
    panel_ci_strip(ax_ci, ci_pair, d1)

    gs_conf = gs[2, :]
    from matplotlib.gridspec import GridSpecFromSubplotSpec
    gs_conf4 = GridSpecFromSubplotSpec(1, 4, subplot_spec=gs_conf, wspace=0.35)
    panel_confusion(fig, gs_conf4, predictions_by_method, log_lines)

    ax_diag = fig.add_subplot(gs[3, :])
    panel_middle_diagnostics(ax_diag, merged)

    fig.suptitle("PHM2010 D1 core task: 9-method performance landscape, accuracy–consistency\n"
                 "trade-off, representative confusion patterns, and middle-stage diagnostics (n=304)",
                 fontsize=11, y=0.975)
    fig.subplots_adjust(top=0.93, bottom=0.03)

    paths = save_all(fig, OUT_DIR, "fig1_main")
    log_lines.append(f"Saved outputs: {paths}")

    with open(os.path.join(LOG_DIR, "validation.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
    print("\n".join(log_lines))
    print("Fig.1 done.")


if __name__ == "__main__":
    main()
