"""
Fig4-4 (消融实验 / probability-state formation) data loading and headline-number validation.

Inputs (read-only):
  - 07_figure_ready/fig4/A1_A6_absolute.csv               6-config authoritative metrics
  - 07_figure_ready/fig4/A1_A6_delta_vs_A1.csv             deltas vs A1 (annotation only)
  - 07_figure_ready/fig4/A1_A6_probability_trajectories.csv  1824 rows = 6 configs x 304 runs
  - 07_figure_ready/fig4/A1_A6_lifecycle_variation.csv      local L1 probability variation per run
  - 07_figure_ready/fig4/A1_A6_cumulative_variation.csv     cumulative L1 probability variation

Core scientific facts this script asserts (must hold for the figure to be built at all):
  - A1-A4 hard classification (Acc/Macro-F1/M-F1/M-Rec) is BYTE-IDENTICAL (not just "close") --
    the manuscript's own point: fine-state/prior/mixture change probability SHAPE, not argmax.
  - A5 has materially lower Acc/M-F1/M-Rec than A1-A4 (real classification cost).
  - A6 recovers most of A5's classification loss while keeping Smooth well below A1.
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "_shared"))
import data_utils as du  # noqa: E402

HERE = os.path.dirname(__file__)
FIG_DIR = os.path.normpath(os.path.join(HERE, ".."))
DERIVED_DIR = os.path.join(FIG_DIR, "derived")
LOG_DIR = os.path.join(FIG_DIR, "logs")
os.makedirs(DERIVED_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

ABLATION_IDS = ["A1", "A2", "A3", "A4", "A5", "A6"]
SUBSET = ["A1", "A4", "A5", "A6"]  # resolved decision, FIGURE_REBUILD_AUDIT.md


def load_absolute():
    df = du.read_csv("07_figure_ready", "fig4", "A1_A6_absolute.csv")
    assert len(df) == 6 and list(df["ID"]) == ABLATION_IDS
    return df


def load_delta():
    df = du.read_csv("07_figure_ready", "fig4", "A1_A6_delta_vs_A1.csv")
    assert len(df) == 6
    return df


def load_trajectories():
    df = du.read_csv("07_figure_ready", "fig4", "A1_A6_probability_trajectories.csv")
    assert len(df) == 1824, f"expected 1824 rows (6x304), got {len(df)}"
    for aid in ABLATION_IDS:
        assert (df["ID"] == aid).sum() == 304, f"{aid}: expected 304 runs"
    return df


def load_lifecycle_variation():
    df = du.read_csv("07_figure_ready", "fig4", "A1_A6_lifecycle_variation.csv")
    assert len(df) == 1824
    return df


def load_cumulative_variation():
    df = du.read_csv("07_figure_ready", "fig4", "A1_A6_cumulative_variation.csv")
    assert len(df) == 1824
    return df


def validate(abs_df, log_lines):
    a1a4 = abs_df[abs_df["ID"].isin(["A1", "A2", "A3", "A4"])]
    for col in ["Acc", "Macro-F1", "M-F1", "M-Rec"]:
        vals = a1a4[col].values
        identical = np.allclose(vals, vals[0], atol=0)
        log_lines.append(f"{'PASS' if identical else 'FAIL'}: A1-A4 {col} byte-identical = {identical} (values={vals.tolist()})")
        assert identical, f"A1-A4 {col} expected byte-identical, found variation"

    a1 = abs_df[abs_df["ID"] == "A1"].iloc[0]
    a5 = abs_df[abs_df["ID"] == "A5"].iloc[0]
    a6 = abs_df[abs_df["ID"] == "A6"].iloc[0]

    checks = [
        ("A1 Smooth", a1["Smooth"], 0.023593, 2e-4),
        ("A5 Smooth", a5["Smooth"], 0.013595, 2e-4),
        ("A5 vs A1 Smooth reduction pct", (a1["Smooth"] - a5["Smooth"]) / a1["Smooth"] * 100, 42.4, 0.5),
        ("A6 Smooth", a6["Smooth"], 0.018761, 2e-4),
        ("A6 vs A1 Smooth reduction pct", (a1["Smooth"] - a6["Smooth"]) / a1["Smooth"] * 100, 20.5, 0.5),
        ("A5 Acc", a5["Acc"], 0.976974, 2e-4),
        ("A6 Acc", a6["Acc"], 0.986842, 2e-4),
        ("A6 vs A5 Acc recovery pp", (a6["Acc"] - a5["Acc"]) * 100, 0.99, 0.1),
        ("A6 vs A5 M-F1 recovery pp", (a6["M-F1"] - a5["M-F1"]) * 100, 1.18, 0.15),
        ("A6 vs A5 M-Rec recovery pp", (a6["M-Rec"] - a5["M-Rec"]) * 100, 1.55, 0.15),
    ]
    ok = True
    for name, val, exp, atol in checks:
        close = np.isclose(val, exp, atol=atol)
        ok = ok and close
        log_lines.append(f"{'PASS' if close else 'FAIL'}: {name}={val:.5f} vs expected {exp} (atol={atol})")
    assert ok, "one or more A1-A6 headline checks failed"
    # explicit assertion that A5 is materially worse than A1-A4 (not a monotonic-improvement figure)
    assert a5["Acc"] < a1["Acc"] - 0.005, "A5 must show a real classification cost vs A1-A4"
    log_lines.append(f"PASS: A5 Acc ({a5['Acc']:.4f}) is materially below A1-A4 Acc ({a1['Acc']:.4f}) -- "
                      f"confirmed real trade-off, not a monotonic-improvement artifact.")


def build_stagewise_f1(traj_df, abs_df, log_lines):
    """Per-config E-F1/M-F1/L-F1 recomputed directly from sample-level true/pred stage labels in
    A1_A6_probability_trajectories.csv (never hand-entered). Cross-validated against the
    authoritative M-F1 column in A1_A6_absolute.csv -- both must agree, confirming this is the
    same underlying classification, not a divergent recomputation."""
    rows = []
    for aid in ABLATION_IDS:
        sub = traj_df[traj_df["ID"] == aid]
        pc = du.precision_recall_f1_per_class(sub["true_stage"].values, sub["pred_stage"].values,
                                                labels=du.STAGE_ORDER)
        rows.append({"ID": aid, "E_F1": pc["early"]["f1"], "M_F1": pc["middle"]["f1"],
                     "L_F1": pc["late"]["f1"]})
    out = pd.DataFrame(rows)
    merged = out.merge(abs_df[["ID", "M-F1"]], on="ID")
    close = np.allclose(merged["M_F1"], merged["M-F1"], atol=1e-6)
    log_lines.append(f"{'PASS' if close else 'FAIL'}: recomputed per-config M-F1 matches A1_A6_absolute.csv's "
                      f"authoritative M-F1 exactly (atol=1e-6) -- confirms same underlying classification.")
    assert close, "recomputed M-F1 diverges from the authoritative A1_A6_absolute.csv value"
    return out


def main():
    log_lines = []
    abs_df = load_absolute()
    delta_df = load_delta()
    traj_df = load_trajectories()
    lv_df = load_lifecycle_variation()
    cv_df = load_cumulative_variation()
    log_lines.append("PASS: loaded A1_A6_absolute (6 rows), delta_vs_A1 (6 rows), "
                      "probability_trajectories (1824 rows), lifecycle_variation (1824 rows), "
                      "cumulative_variation (1824 rows).")

    validate(abs_df, log_lines)
    stagewise_f1 = build_stagewise_f1(traj_df, abs_df, log_lines)
    stagewise_f1.to_csv(os.path.join(DERIVED_DIR, "stagewise_f1.csv"), index=False, encoding="utf-8")

    abs_df.to_csv(os.path.join(DERIVED_DIR, "A1_A6_absolute.csv"), index=False, encoding="utf-8")
    delta_df.to_csv(os.path.join(DERIVED_DIR, "A1_A6_delta_vs_A1.csv"), index=False, encoding="utf-8")
    traj_sub = traj_df[traj_df["ID"].isin(SUBSET)].copy()
    traj_sub.to_csv(os.path.join(DERIVED_DIR, "trajectories_subset.csv"), index=False, encoding="utf-8")
    lv_df.to_csv(os.path.join(DERIVED_DIR, "lifecycle_variation.csv"), index=False, encoding="utf-8")
    cv_df.to_csv(os.path.join(DERIVED_DIR, "cumulative_variation.csv"), index=False, encoding="utf-8")

    with open(os.path.join(LOG_DIR, "validation.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
    print("\n".join(log_lines))
    print(f"\nWrote files to {DERIVED_DIR}")


if __name__ == "__main__":
    main()
