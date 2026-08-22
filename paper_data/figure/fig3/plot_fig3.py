"""
Fig.3 (paper Fig. 4-4): A1-A6 ablation mechanism band.

Inputs (all under paper_data/07_figure_ready/fig4/ -- NOT paper_data/07_figure_ready/fig3/,
see paper_data/figure/FIGURE_PROGRESS.md for why the on-disk numbering does not match the
final figure numbering):
  - A1_A6_absolute.csv                 config-level authoritative metrics (sole permitted source)
  - A1_A6_probability_trajectories.csv run-level true_stage/pred_stage/probabilities, 6x304 rows
  - A1_A6_lifecycle_variation.csv      run-level local L1 probability variation, 6x304 rows
  - A1_A6_cumulative_variation.csv     run-level cumulative L1 probability variation, 6x304 rows
  - A1_A6_delta_vs_A1.csv              config-level deltas vs A1

Outputs: paper_data/figure/fig3/outputs/fig3_main.{png,pdf,svg}
Derived: paper_data/figure/fig3/derived/A1_A6_classwise_metrics.csv
Logs:    paper_data/figure/fig3/logs/validation.txt

Run: python paper_data/figure/fig3/plot_fig3.py
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_shared"))
from style import apply_style, save_all, ABLATION_IDS, ABLATION_COLORS, STAGE_ORDER, STAGE_COLORS  # noqa: E402
import data_utils as du  # noqa: E402

HERE = os.path.dirname(__file__)
OUT_DIR = os.path.join(HERE, "outputs")
DERIVED_DIR = os.path.join(HERE, "derived")
LOG_DIR = os.path.join(HERE, "logs")
os.makedirs(DERIVED_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

CONFIG_LABEL = {
    "Temperature-scaled raw stage head": "A1",
    "Raw plus fine-state stage probability": "A2",
    "Raw plus q-hat degradation-position prior": "A3",
    "Raw plus weighted fine/prior mixture": "A4",
    "Causal ordered filter applied to A4 mix": "A5",
    "Final blend of A4 mix and A5 ordered output": "A6",
}


def load():
    absolute = du.read_csv("07_figure_ready", "fig4", "A1_A6_absolute.csv")
    traj = du.read_csv("07_figure_ready", "fig4", "A1_A6_probability_trajectories.csv")
    local_var = du.read_csv("07_figure_ready", "fig4", "A1_A6_lifecycle_variation.csv")
    cum_var = du.read_csv("07_figure_ready", "fig4", "A1_A6_cumulative_variation.csv")
    delta = du.read_csv("07_figure_ready", "fig4", "A1_A6_delta_vs_A1.csv")
    return absolute, traj, local_var, cum_var, delta


def recompute_classwise(traj):
    """Recompute E-F1/M-F1/L-F1/M-Precision/M-Recall/Acc/Macro-F1 per config from run-level
    true_stage/pred_stage, independent of the pre-aggregated A1_A6_absolute.csv."""
    rows = []
    for config, sub in traj.groupby("Configuration", sort=False):
        pc = du.precision_recall_f1_per_class(sub["true_stage"].values, sub["pred_stage"].values)
        acc = du.accuracy(sub["true_stage"].values, sub["pred_stage"].values)
        mf1 = du.macro_f1(sub["true_stage"].values, sub["pred_stage"].values)
        rows.append({
            "Configuration": config,
            "ID": CONFIG_LABEL[config],
            "n": len(sub),
            "Acc_recomputed": acc,
            "MacroF1_recomputed": mf1,
            "E_F1": pc["early"]["f1"],
            "M_F1_recomputed": pc["middle"]["f1"],
            "L_F1": pc["late"]["f1"],
            "M_Precision": pc["middle"]["precision"],
            "M_Recall_recomputed": pc["middle"]["recall"],
        })
    out = pd.DataFrame(rows)
    out["ID"] = pd.Categorical(out["ID"], categories=ABLATION_IDS, ordered=True)
    out = out.sort_values("ID").reset_index(drop=True)
    return out


def validate(absolute, classwise, log_lines):
    absolute = absolute.copy()
    absolute["ID_check"] = absolute["Configuration"].map(CONFIG_LABEL)
    merged = absolute.merge(classwise, on="Configuration", suffixes=("", "_cw"))
    assert len(merged) == 6, f"expected 6 configs, got {len(merged)}"
    for _, r in merged.iterrows():
        assert np.isclose(r["Acc"], r["Acc_recomputed"], atol=1e-6), (r["Configuration"], r["Acc"], r["Acc_recomputed"])
        assert np.isclose(r["M-F1"], r["M_F1_recomputed"], atol=1e-6), (r["Configuration"], r["M-F1"], r["M_F1_recomputed"])
        assert np.isclose(r["M-Rec"], r["M_Recall_recomputed"], atol=1e-6), (r["Configuration"], r["M-Rec"], r["M_Recall_recomputed"])
    log_lines.append("PASS: recomputed Acc/M-F1/M-Rec from run-level predictions match A1_A6_absolute.csv exactly (atol=1e-6) for all 6 configs.")

    a1 = absolute[absolute["Configuration"] == "Temperature-scaled raw stage head"].iloc[0]
    a4 = absolute[absolute["Configuration"] == "Raw plus weighted fine/prior mixture"].iloc[0]
    a5 = absolute[absolute["Configuration"] == "Causal ordered filter applied to A4 mix"].iloc[0]
    a6 = absolute[absolute["Configuration"] == "Final blend of A4 mix and A5 ordered output"].iloc[0]

    assert np.isclose(a1["Acc"], a4["Acc"], atol=1e-9) and np.isclose(a1["Macro-F1"], a4["Macro-F1"], atol=1e-9), \
        "A1-A4 hard classification should be identical"
    log_lines.append("PASS: A1-A4 argmax classification metrics identical (Acc, Macro-F1, M-F1, M-Rec).")

    smooth_a1, smooth_a5, smooth_a6 = a1["Smooth"], a5["Smooth"], a6["Smooth"]
    pct_a5 = (smooth_a1 - smooth_a5) / smooth_a1 * 100
    pct_a6 = (smooth_a1 - smooth_a6) / smooth_a1 * 100
    assert np.isclose(pct_a5, 42.4, atol=0.5), f"A5 Smooth benefit vs A1 expected ~42.4%, got {pct_a5:.2f}%"
    assert np.isclose(pct_a6, 20.5, atol=0.5), f"A6 Smooth benefit vs A1 expected ~20.5%, got {pct_a6:.2f}%"
    log_lines.append(f"PASS: Smooth benefit vs A1 -- A5={pct_a5:.2f}% (expected ~42.4%), A6={pct_a6:.2f}% (expected ~20.5%).")

    d_acc = (a6["Acc"] - a5["Acc"]) * 100
    d_mf1 = (a6["M-F1"] - a5["M-F1"]) * 100
    d_mrec = (a6["M-Rec"] - a5["M-Rec"]) * 100
    assert np.isclose(d_acc, 0.99, atol=0.1), d_acc
    assert np.isclose(d_mf1, 1.18, atol=0.15), d_mf1
    assert np.isclose(d_mrec, 1.55, atol=0.15), d_mrec
    log_lines.append(f"PASS: A6 recovery vs A5 -- dAcc={d_acc:.2f}pp (~0.99), dM-F1={d_mf1:.2f}pp (~1.18), dM-Rec={d_mrec:.2f}pp (~1.55).")
    return merged


def panel_predictive(ax, absolute):
    absolute = absolute.copy()
    absolute["ID"] = pd.Categorical(absolute["Configuration"].map(CONFIG_LABEL), categories=ABLATION_IDS, ordered=True)
    absolute = absolute.sort_values("ID")
    x = np.arange(len(ABLATION_IDS))
    for metric, marker in [("Acc", "o"), ("Macro-F1", "s"), ("M-F1", "^")]:
        ax.plot(x, absolute[metric].values * 100, marker=marker, ms=4, lw=1.4, label=metric)
    ax.set_xticks(x)
    ax.set_xticklabels(ABLATION_IDS)
    ax.set_ylabel("% (higher better)")
    ax.set_title("(a) Predictive performance", loc="left", fontweight="bold")
    ax.legend(loc="lower left", ncol=1)
    ax.axvspan(3.5, 4.5, color=ABLATION_COLORS["A5"], alpha=0.08)
    ax.set_ylim(97.0, 99.15)
    ax.annotate("A5: strongest ordered\nfilter -> classification dip",
                xy=(4, absolute.loc[absolute["ID"] == "A5", "M-F1"].values[0] * 100),
                xytext=(3.05, 97.05), fontsize=6.5, color="#7A2E2E")
    ax.annotate("A6: final blend\nrecovers classification",
                xy=(5, absolute.loc[absolute["ID"] == "A6", "Acc"].values[0] * 100),
                xytext=(4.55, 98.55), fontsize=6.5, color=ABLATION_COLORS["A6"])


def panel_statewise(ax, classwise):
    x = np.arange(len(ABLATION_IDS))
    for stage, col, marker in [("E_F1", STAGE_COLORS["early"], "o"),
                                ("M_F1_recomputed", STAGE_COLORS["middle"], "s"),
                                ("L_F1", STAGE_COLORS["late"], "^")]:
        label = {"E_F1": "E-F1", "M_F1_recomputed": "M-F1", "L_F1": "L-F1"}[stage]
        ax.plot(x, classwise[stage].values * 100, marker=marker, ms=4, lw=1.4, color=col, label=label)
    ax.set_xticks(x)
    ax.set_xticklabels(ABLATION_IDS)
    ax.set_ylabel("Class F1 % (higher better)")
    ax.set_title("(b) State-wise recognition profile", loc="left", fontweight="bold")
    ax.legend(loc="lower left", ncol=3)


def panel_consistency_heatmap(ax, absolute):
    absolute = absolute.copy()
    absolute["ID"] = pd.Categorical(absolute["Configuration"].map(CONFIG_LABEL), categories=ABLATION_IDS, ordered=True)
    absolute = absolute.sort_values("ID").set_index("ID")
    m_to_e_col = [c for c in absolute.columns if c.startswith("M") and "E" in c and "→" in c]
    m_to_l_col = [c for c in absolute.columns if c.startswith("M") and "L" in c and "→" in c]
    m_to_e = m_to_e_col[0] if m_to_e_col else "M_to_E"
    m_to_l = m_to_l_col[0] if m_to_l_col else "M_to_L"
    metrics = [("M-Rec", "higher", "M-Rec"), (m_to_e, "lower", "M→E"), (m_to_l, "lower", "M→L"),
               ("Rev", "lower", "Rev"), ("Jump", "lower", "Jump"), ("Smooth", "lower", "Smooth")]
    grid = np.zeros((len(metrics), len(ABLATION_IDS)))
    raw = np.zeros_like(grid)
    for i, (col, direction, _) in enumerate(metrics):
        vals = absolute[col].values.astype(float)
        raw[i] = vals
        vmin, vmax = vals.min(), vals.max()
        if vmax - vmin < 1e-12:
            norm = np.ones_like(vals) * 0.5
        else:
            norm = (vals - vmin) / (vmax - vmin)
        if direction == "lower":
            norm = 1 - norm
        grid[i] = norm
    im = ax.imshow(grid, aspect="auto", cmap="RdYlGn", vmin=0, vmax=1)
    ax.set_xticks(np.arange(len(ABLATION_IDS)))
    ax.set_xticklabels(ABLATION_IDS)
    ax.set_yticks(np.arange(len(metrics)))
    ax.set_yticklabels([f"{lab} {'↑' if d=='higher' else '↓'}" for _, d, lab in metrics])
    for i in range(len(metrics)):
        for j in range(len(ABLATION_IDS)):
            fmt = f"{raw[i, j]:.3f}" if metrics[i][0] != "Rev" and metrics[i][0] != "Jump" else f"{int(raw[i, j])}"
            ax.text(j, i, fmt, ha="center", va="center", fontsize=6.3,
                     color="black" if 0.25 < grid[i, j] < 0.85 else "white")
    ax.set_title("(c) Middle-stage & transition consistency (color = within-row normalized benefit; numbers = raw values)",
                 loc="left", fontweight="bold")
    cbar = plt.colorbar(im, ax=ax, fraction=0.025, pad=0.01)
    cbar.set_label("within-row benefit\n(normalized, 1=best)", fontsize=6.5)
    cbar.ax.tick_params(labelsize=6)


def panel_lifecycle_variation(ax_local, ax_cum, local_var, cum_var):
    for cid in ABLATION_IDS:
        label_map = {v: k for k, v in CONFIG_LABEL.items()}
        config_name = label_map[cid]
        sub = local_var[local_var["Configuration"] == config_name] if "Configuration" in local_var.columns else local_var[local_var["ID"] == cid]
        sub = sub.sort_values("relative_tool_life")
        ax_local.plot(sub["relative_tool_life"], sub["local_variation_l1_smoothed"],
                       color=ABLATION_COLORS[cid], lw=1.3, label=cid,
                       alpha=1.0 if cid in ("A1", "A5", "A6") else 0.75)

        subc = cum_var[cum_var["Configuration"] == config_name] if "Configuration" in cum_var.columns else cum_var[cum_var["ID"] == cid]
        subc = subc.sort_values("relative_tool_life")
        ax_cum.plot(subc["relative_tool_life"], subc["cumulative_variation_l1"],
                    color=ABLATION_COLORS[cid], lw=1.3, label=cid,
                    alpha=1.0 if cid in ("A1", "A5", "A6") else 0.75)

    ax_local.set_xlabel("Relative tool life")
    ax_local.set_ylabel("Local prob. variation\n(smoothed, L1)")
    ax_local.set_title("(d) Lifecycle local probability variation, A1→A6", loc="left", fontweight="bold")
    ax_local.legend(loc="upper right", ncol=6, fontsize=6.3, columnspacing=0.8, handlelength=1.3)

    ax_cum.set_xlabel("Relative tool life")
    ax_cum.set_ylabel("Cumulative prob.\nvariation (L1)")
    ax_cum.set_title("(e) Cumulative probability variation, A1→A6", loc="left", fontweight="bold")


def main():
    apply_style()
    absolute, traj, local_var, cum_var, delta = load()

    assert len(traj) == 1824, f"expected 6x304=1824 rows in probability trajectories, got {len(traj)}"
    assert len(local_var) == 1824
    assert len(cum_var) == 1824
    assert set(traj["true_stage"].unique()) <= set(STAGE_ORDER)

    classwise = recompute_classwise(traj)
    classwise.to_csv(os.path.join(DERIVED_DIR, "A1_A6_classwise_metrics.csv"), index=False, encoding="utf-8")

    log_lines = []
    merged = validate(absolute, classwise, log_lines)

    # local_var / cum_var already carry their own "ID" column (A1..A6) natively -- verified
    # against the schema printed during precheck. panel_lifecycle_variation() uses "ID" directly
    # via the CONFIG_LABEL-derived cid, with a "Configuration" fallback only if present.
    assert "ID" in local_var.columns and "ID" in cum_var.columns
    assert set(local_var["ID"].unique()) == set(ABLATION_IDS)
    for cid in ABLATION_IDS:
        n_local = (local_var["ID"] == cid).sum()
        n_cum = (cum_var["ID"] == cid).sum()
        assert n_local == 304 and n_cum == 304, (cid, n_local, n_cum)
    log_lines.append("PASS: local/cumulative variation files each contain 304 runs per A1-A6 configuration (identified via native 'ID' column).")

    fig = plt.figure(figsize=(11.5, 9.2))
    gs = GridSpec(3, 2, height_ratios=[1.0, 0.9, 1.0], hspace=0.55, wspace=0.28, figure=fig)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, :])
    ax_d = fig.add_subplot(gs[2, 0])
    ax_e = fig.add_subplot(gs[2, 1])

    panel_predictive(ax_a, absolute)
    panel_statewise(ax_b, classwise)
    panel_consistency_heatmap(ax_c, absolute)
    panel_lifecycle_variation(ax_d, ax_e, local_var, cum_var)

    fig.suptitle("A1→A6 module-progression ablation: predictive performance, middle-stage/transition\n"
                 "consistency, and lifecycle probability dynamics (PHM2010 D1, C6 test set, n=304)",
                 fontsize=10.5, y=0.995)

    paths = save_all(fig, OUT_DIR, "fig3_main")
    log_lines.append(f"Saved outputs: {paths}")

    with open(os.path.join(LOG_DIR, "validation.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")

    print("\n".join(log_lines))
    print("Fig.3 done.")


if __name__ == "__main__":
    main()
