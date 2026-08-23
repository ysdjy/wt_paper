"""
Fig4-3 (鲁棒性) data loading, merging, and headline-number validation.

Panel list (resolved in FIGURE_REBUILD_AUDIT.md, no confusion-matrix inset -- Fig4-2 already
carries one):
  (a) PHM D1/D2/D3 x 9-method mini-heatmaps, Acc/M-F1/Smooth only.
  (b) Multi-task-TCN-GRU -> DC-PSR paired change across PHM D1/D2/D3 + NASA + MTW-CM
      (delta_Acc, delta_M_F1 in pp; Smooth-benefit, Jump-benefit in relative %, positive=improvement).
  (c) External task-level paired profiles: NASA N1-N4 + MTW-CM D1-M/D2-M/D3-M,
      Multi-task TCN-GRU vs DC-PSR only, individual tasks kept (not collapsed to one average bar).

Inputs (read-only):
  - 07_figure_ready/fig2/taskwise_absolute.csv          D1/D2/D3 x 9 methods
  - 07_figure_ready/fig3/cross_dataset_absolute.csv      PHM/NASA/MTW-CM x {B11,B12} absolute
  - 07_figure_ready/fig3/cross_dataset_deltas.csv        precomputed deltas (PHM D1, NASA, MTW-CM x3 + avg)
  - 02_NASA/task_level_results.csv                       NASA N1-N4 per-task, B9-B12
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

TASKS = ["D1", "D2", "D3"]


def load_taskwise():
    df = du.read_csv("07_figure_ready", "fig2", "taskwise_absolute.csv")
    assert len(df) == 27, f"expected 27 rows (9 methods x 3 tasks), got {len(df)}"
    for t in TASKS:
        assert (df["Task"] == t).sum() == 9, f"expected 9 methods for {t}"
    return df


def load_cross_dataset():
    abs_df = du.read_csv("07_figure_ready", "fig3", "cross_dataset_absolute.csv")
    delta_df = du.read_csv("07_figure_ready", "fig3", "cross_dataset_deltas.csv")
    assert len(abs_df) == 12, f"expected 12 rows, got {len(abs_df)}"
    assert len(delta_df) == 6, f"expected 6 delta rows, got {len(delta_df)}"
    return abs_df, delta_df


def load_nasa_tasklevel():
    df = du.read_csv("02_NASA", "task_level_results.csv")
    assert len(df) == 16, f"expected 16 rows (4 methods x 4 tasks), got {len(df)}"
    df = df.rename(columns={"M-F1": "M_F1"})
    return df


def build_panel_b_table(taskwise, cross_delta, cross_abs, log_lines):
    """PHM D1/D2/D3 deltas computed fresh from taskwise_absolute (Multi-task TCN-GRU -> DC-PSR);
    NASA + MTW-CM deltas taken from the precomputed, already-validated cross_dataset_deltas.csv.
    Smooth/Jump benefit expressed as RELATIVE % improvement (positive = improvement), computed
    from the ABSOLUTE Smooth/Jump of the backbone (never re-flipped silently)."""
    rows = []
    for t in TASKS:
        sub = taskwise[taskwise["Task"] == t]
        bb = sub[sub["Method"] == "Multi-task TCN-GRU"].iloc[0]
        dc = sub[sub["Method"] == "DC-PSR"].iloc[0]
        smooth_benefit_pct = (bb["Smooth"] - dc["Smooth"]) / bb["Smooth"] * 100 if bb["Smooth"] > 0 else np.nan
        jump_benefit_pct = (bb["Jump"] - dc["Jump"]) / bb["Jump"] * 100 if bb["Jump"] > 0 else 0.0
        rows.append({
            "group": f"PHM {t}", "delta_Acc_pp": (dc["Acc"] - bb["Acc"]) * 100,
            "delta_MF1_pp": (dc["M_F1"] - bb["M_F1"]) * 100,
            "Smooth_benefit_pct": smooth_benefit_pct, "Jump_benefit_pct": jump_benefit_pct,
        })

    nasa_delta = cross_delta[cross_delta["dataset"] == "NASA_MILLING"].iloc[0]
    nasa_abs = cross_abs[(cross_abs["dataset"] == "NASA_MILLING")]
    bb_smooth = nasa_abs[nasa_abs["method"] == "B11"]["Smooth"].iloc[0]
    bb_jump = nasa_abs[nasa_abs["method"] == "B11"]["Jump"].iloc[0]
    rows.append({
        "group": "NASA (N1–N4 avg)", "delta_Acc_pp": nasa_delta["delta_Acc"] * 100,
        "delta_MF1_pp": nasa_delta["delta_M_F1"] * 100,
        "Smooth_benefit_pct": nasa_delta["Smooth_benefit"] / bb_smooth * 100,
        "Jump_benefit_pct": nasa_delta["Jump_benefit"] / bb_jump * 100 if bb_jump > 0 else 0.0,
    })

    mtw_delta = cross_delta[(cross_delta["dataset"] == "MILLING_CROSS_MACHINE") &
                              (cross_delta["task_scope"] == "D1-M,D2-M,D3-M")].iloc[0]
    mtw_abs = cross_abs[cross_abs["dataset"] == "MILLING_CROSS_MACHINE"]
    # backbone absolute Smooth/Jump for the 3-task average: mean of D1-M/D2-M/D3-M B11 rows
    bb_mtw = mtw_abs[(mtw_abs["method"] == "B11") & (mtw_abs["task_scope"].isin(["D1-M", "D2-M", "D3-M"]))]
    bb_smooth_mtw = bb_mtw["Smooth"].mean()
    bb_jump_mtw = bb_mtw["Jump"].mean()
    rows.append({
        "group": "MTW-CM (3-task avg)", "delta_Acc_pp": mtw_delta["delta_Acc"] * 100,
        "delta_MF1_pp": mtw_delta["delta_M_F1"] * 100,
        "Smooth_benefit_pct": mtw_delta["Smooth_benefit"] / bb_smooth_mtw * 100,
        "Jump_benefit_pct": mtw_delta["Jump_benefit"] / bb_jump_mtw * 100,
    })

    out = pd.DataFrame(rows)
    # cross-check against docx headline numbers (verified in FIGURE_PROGRESS.md, re-verify here)
    checks = [
        ("PHM D1", "Smooth_benefit_pct", 20.5, 1.0),
        ("NASA (N1–N4 avg)", "Smooth_benefit_pct", 35.0, 1.0),
        ("NASA (N1–N4 avg)", "Jump_benefit_pct", 50.0, 1.0),
        ("MTW-CM (3-task avg)", "delta_MF1_pp", 10.04, 0.5),
        ("MTW-CM (3-task avg)", "Smooth_benefit_pct", 23.9, 1.0),
        ("MTW-CM (3-task avg)", "Jump_benefit_pct", 82.5, 1.0),
    ]
    ok = True
    for grp, col, exp, atol in checks:
        val = out.loc[out["group"] == grp, col].iloc[0]
        close = np.isclose(val, exp, atol=atol)
        ok = ok and close
        log_lines.append(f"{'PASS' if close else 'FAIL'}: {grp} {col}={val:.3f} vs expected {exp} (atol={atol})")
    assert ok, "panel (b) recomputed deltas do not match docx headline numbers"
    return out


def build_panel_c_table(nasa_task, cross_abs, log_lines):
    rows = []
    for task in ["N1", "N2", "N3", "N4"]:
        sub = nasa_task[nasa_task["Task"] == task]
        for mid, name in [("B11", "Multi-task TCN-GRU"), ("B12", "DC-PSR")]:
            r = sub[sub["Method"] == mid].iloc[0]
            rows.append({"dataset": "NASA", "task": task, "Method": name,
                         "M_F1": r["M_F1"], "Smooth": r["Smooth"]})
    for task in ["D1-M", "D2-M", "D3-M"]:
        sub = cross_abs[(cross_abs["dataset"] == "MILLING_CROSS_MACHINE") & (cross_abs["task_scope"] == task)]
        for mid, name in [("B11", "Multi-task TCN-GRU"), ("B12", "DC-PSR")]:
            r = sub[sub["method"] == mid].iloc[0]
            rows.append({"dataset": "MTW-CM", "task": task, "Method": name,
                         "M_F1": r["M_F1"], "Smooth": r["Smooth"]})
    out = pd.DataFrame(rows)
    assert len(out) == 14, f"expected 14 rows (7 tasks x 2 methods), got {len(out)}"
    log_lines.append("PASS: panel (c) table has 7 tasks (NASA N1-N4 + MTW-CM D1-M/D2-M/D3-M) x 2 methods = 14 rows.")
    return out


def main():
    log_lines = []
    taskwise = load_taskwise()
    cross_abs, cross_delta = load_cross_dataset()
    nasa_task = load_nasa_tasklevel()
    log_lines.append("PASS: loaded taskwise_absolute (27 rows), cross_dataset_absolute (12 rows), "
                      "cross_dataset_deltas (6 rows), NASA task_level_results (16 rows).")

    panel_b = build_panel_b_table(taskwise, cross_delta, cross_abs, log_lines)
    panel_c = build_panel_c_table(nasa_task, cross_abs, log_lines)

    taskwise.to_csv(os.path.join(DERIVED_DIR, "taskwise_absolute.csv"), index=False, encoding="utf-8")
    panel_b.to_csv(os.path.join(DERIVED_DIR, "panel_b_deltas.csv"), index=False, encoding="utf-8")
    panel_c.to_csv(os.path.join(DERIVED_DIR, "panel_c_tasklevel.csv"), index=False, encoding="utf-8")

    with open(os.path.join(LOG_DIR, "validation.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
    print("\n".join(log_lines))
    print(f"\nWrote files to {DERIVED_DIR}")


if __name__ == "__main__":
    main()
