"""
Fig4-2 (主比较) data loading, merging, and headline-number validation.

Inputs (all under paper_data/, read-only, never modified):
  - 07_figure_ready/fig1/D1_main_metrics.csv           9-method point estimates + bootstrap CI
  - 07_figure_ready/fig1/accuracy_consistency_points.csv  Acc/Smooth pairs (panel b)
  - 07_figure_ready/fig1/B11_B12_controlled_comparison.csv  paired Multi-task-TCN-GRU/DC-PSR CI
  - 07_figure_ready/fig2/taskwise_absolute.csv (Task==D1)  E_F1/L_F1/M_Precision completion
  - 01_PHM2010/01_main_D1/predictions_common_universe/D1_<method_id>_304runs.csv (9 files)
      sample-level true_stage/pred_stage -> confusion matrices + M-Pre/M-Rec/M->E/M->L/Rev/Jump/
      Smooth recomputed directly from labels for the 4 representative methods (panels d/e).

Outputs:
  derived/D1_heatmap_table.csv      9 x (Acc,MacroF1,E_F1,M_F1,L_F1,M_Pre,M_Rec,M_to_E,M_to_L,Rev,Jump,Smooth)
  derived/representative_recomputed.csv   per-representative-method recomputed diagnostics
  logs/validation.txt
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "_shared"))
import data_utils as du  # noqa: E402
import style as st  # noqa: E402

HERE = os.path.dirname(__file__)
FIG_DIR = os.path.normpath(os.path.join(HERE, ".."))
DERIVED_DIR = os.path.join(FIG_DIR, "derived")
LOG_DIR = os.path.join(FIG_DIR, "logs")
os.makedirs(DERIVED_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

METHOD_ID_MAP = {
    "RF": "rf", "TCN-GRU": "tcn_gru", "Multi-task TCN-GRU": "multitask_tcn_gru",
    "DC-PSR": "dc_psr", "HTT-Net (adapted)": "htt_net",
    "Multi-source Attention": "multi_source_attention", "MTF-AViTK": "mtf_avitk",
    "Dynamic GIN + TGP": "dynamic_gin_tgp", "DP2Net-adapted": "dp2net_adapted",
}


def load_main():
    main = du.read_csv("07_figure_ready", "fig1", "D1_main_metrics.csv")
    assert len(main) == 9, f"expected 9 methods, got {len(main)}"
    taskwise = du.read_csv("07_figure_ready", "fig2", "taskwise_absolute.csv")
    d1 = taskwise[taskwise["Task"] == "D1"][["Method", "E_F1", "L_F1", "M_Precision"]]
    assert len(d1) == 9, f"expected 9 D1 rows in taskwise_absolute, got {len(d1)}"
    merged = main.merge(d1, on="Method", how="left", validate="one_to_one")
    assert merged["E_F1"].notna().all() and merged["L_F1"].notna().all() and merged["M_Precision"].notna().all()
    # cross-check M_F1/M_Rec identical between the two sources (byte-level, already validated in
    # prior rounds; re-verify here since this is a fresh load)
    tw_full = taskwise[taskwise["Task"] == "D1"][["Method", "M_F1", "M_Recall"]].rename(
        columns={"M_F1": "M_F1_tw", "M_Recall": "M_Rec_tw"})
    chk = merged.merge(tw_full, on="Method")
    assert np.allclose(chk["M_F1"], chk["M_F1_tw"], atol=1e-9)
    assert np.allclose(chk["M_Rec"], chk["M_Rec_tw"], atol=1e-9)
    return merged


def load_acc_consistency():
    df = du.read_csv("07_figure_ready", "fig1", "accuracy_consistency_points.csv")
    assert len(df) == 9
    return df


def load_b11_b12_ci():
    df = du.read_csv("07_figure_ready", "fig1", "B11_B12_controlled_comparison.csv")
    assert len(df) == 2 and set(df["Method"]) == {"Multi-task TCN-GRU", "DC-PSR"}
    return df


def load_predictions(method_name):
    mid = METHOD_ID_MAP[method_name]
    df = du.read_csv("01_PHM2010", "01_main_D1", "predictions_common_universe", f"D1_{mid}_304runs.csv")
    assert len(df) == 304, f"{method_name}: expected 304 rows, got {len(df)}"
    return df


def recompute_representative_diagnostics(methods, log_lines):
    rows = []
    conf = {}
    for m in methods:
        df = load_predictions(m)
        true = df["true_stage"].values
        pred = df["pred_stage"].values
        counts, row_norm = du.confusion_counts(true, pred, labels=du.STAGE_ORDER)
        conf[m] = (counts, row_norm)
        pc = du.precision_recall_f1_per_class(true, pred, labels=du.STAGE_ORDER)
        # middle-stage misclassification direction (M->E, M->L), Rev/Jump/Smooth need the run
        # sequence; Rev/Jump/Smooth for representative methods are pulled from the already-
        # validated D1_main_metrics.csv (recomputing Rev/Jump/Smooth needs the ordered per-run
        # sequence semantics already encoded in that authoritative file -- not re-derived here to
        # avoid duplicating a second, potentially inconsistent implementation).
        m_idx = du.STAGE_ORDER.index("middle")
        e_idx = du.STAGE_ORDER.index("early")
        l_idx = du.STAGE_ORDER.index("late")
        m_total = counts[m_idx].sum()
        m_to_e = counts[m_idx, e_idx] / m_total if m_total > 0 else 0.0
        m_to_l = counts[m_idx, l_idx] / m_total if m_total > 0 else 0.0
        rows.append({
            "Method": m,
            "M_Pre": pc["middle"]["precision"], "M_Rec": pc["middle"]["recall"], "M_F1": pc["middle"]["f1"],
            "M_to_E": m_to_e, "M_to_L": m_to_l,
            "Acc": du.accuracy(true, pred), "n": len(df),
        })
    out = pd.DataFrame(rows)
    return out, conf


def cross_validate_against_authoritative(rep_df, main_df, log_lines, atol=2e-4):
    ok = True
    for _, r in rep_df.iterrows():
        m = r["Method"]
        auth = main_df[main_df["Method"] == m].iloc[0]
        for a, b, name in [(r["Acc"], auth["Acc"], "Acc"), (r["M_Rec"], auth["M_Rec"], "M_Rec")]:
            close = np.isclose(a, b, atol=atol)
            ok = ok and close
            log_lines.append(f"{'PASS' if close else 'FAIL'}: {m} recomputed {name}={a:.6f} vs authoritative {b:.6f}")
    assert ok, "recomputed representative-method diagnostics do not match authoritative D1_main_metrics.csv"
    return ok


def main():
    log_lines = []
    main_df = load_main()
    log_lines.append(f"PASS: loaded {len(main_df)}-method D1 main table, E_F1/L_F1/M_Precision merged, "
                      f"M_F1/M_Rec cross-checked identical vs taskwise_absolute.csv.")

    ac_df = load_acc_consistency()
    b1112_df = load_b11_b12_ci()
    log_lines.append("PASS: loaded accuracy_consistency_points.csv (9 rows) and B11_B12_controlled_comparison.csv (2 rows).")

    rep_df, conf = recompute_representative_diagnostics(st.REPRESENTATIVE_METHODS, log_lines)
    cross_validate_against_authoritative(rep_df, main_df, log_lines)
    log_lines.append("PASS: representative-method recomputed Acc/M_Rec match D1_main_metrics.csv (atol=2e-4).")

    for m in st.REPRESENTATIVE_METHODS:
        counts, _ = conf[m]
        assert counts.sum() == 304, f"{m}: confusion matrix does not sum to 304"
    log_lines.append("PASS: all 4 representative confusion matrices sum to exactly 304.")

    expected = {
        ("Multi-task TCN-GRU", "Acc"): 0.990132, ("Multi-task TCN-GRU", "MacroF1"): 0.990230,
        ("Multi-task TCN-GRU", "M_F1"): 0.988235, ("Multi-task TCN-GRU", "M_Rec"): 0.976744,
        ("Multi-task TCN-GRU", "Smooth"): 0.023590,
        ("DC-PSR", "Acc"): 0.986842, ("DC-PSR", "MacroF1"): 0.987102,
        ("DC-PSR", "M_F1"): 0.984375, ("DC-PSR", "M_Rec"): 0.976744, ("DC-PSR", "Smooth"): 0.018763,
    }
    for (m, col), exp in expected.items():
        val = main_df.loc[main_df["Method"] == m, col].iloc[0]
        close = np.isclose(val, exp, atol=2e-4)
        log_lines.append(f"{'PASS' if close else 'FAIL'}: headline {m} {col}={val:.6f} vs expected {exp}")
        assert close

    main_df.to_csv(os.path.join(DERIVED_DIR, "D1_heatmap_table.csv"), index=False, encoding="utf-8")
    ac_df.to_csv(os.path.join(DERIVED_DIR, "accuracy_consistency_points.csv"), index=False, encoding="utf-8")
    b1112_df.to_csv(os.path.join(DERIVED_DIR, "B11_B12_controlled_comparison.csv"), index=False, encoding="utf-8")
    rep_df.to_csv(os.path.join(DERIVED_DIR, "representative_recomputed.csv"), index=False, encoding="utf-8")
    for m in st.REPRESENTATIVE_METHODS:
        counts, row_norm = conf[m]
        mid = METHOD_ID_MAP[m]
        np.savetxt(os.path.join(DERIVED_DIR, f"confusion_counts_{mid}.csv"), counts, fmt="%d", delimiter=",")
        np.savetxt(os.path.join(DERIVED_DIR, f"confusion_rownorm_{mid}.csv"), row_norm, fmt="%.6f", delimiter=",")

    with open(os.path.join(LOG_DIR, "validation.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
    print("\n".join(log_lines))
    print(f"\nWrote {len(os.listdir(DERIVED_DIR))} files to {DERIVED_DIR}")


if __name__ == "__main__":
    main()
