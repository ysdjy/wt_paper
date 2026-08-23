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


# ---------------------------------------------------------------------------
# Panel (c) v2: DC-PSR vs backbone paired effect -- paired moving-block bootstrap
#
# Protocol reuse: block_length=12, n_bootstrap=5000, random_seed=20260820, n_test_runs=304 are
# traced verbatim from paper_data/01_PHM2010/01_main_D1/bootstrap/{multitask_tcn_gru,dc_psr}/
# bootstrap_config.json (both files agree; identical values). No generating script or PROTOCOL.md
# was found anywhere under paper_data/ (searched paper_data/01_PHM2010, 99_scripts, 90_provenance
# for "block_length"/"moving_block"/"moving-block") -- the config JSONs are the only formal record
# of this protocol, so these three parameters are reused exactly, per explicit instruction not to
# invent a new protocol. The per-method bootstrap_samples.csv files themselves are NOT reused here
# (no script exists to confirm their block draws are aligned per-replicate across methods, and using
# two independently-resampled distributions to derive a paired CI is explicitly forbidden by the
# task brief) -- this function performs its own block resampling, drawing ONE shared set of block
# start indices per replicate and applying it to BOTH methods' aligned (same run_id order) sequences.
PAIRED_BLOCK_LENGTH = 12
PAIRED_N_BOOTSTRAP = 5000
PAIRED_SEED = 20260820
PAIRED_PROTOCOL_SOURCE = (
    "paper_data/01_PHM2010/01_main_D1/bootstrap/multitask_tcn_gru/bootstrap_config.json ; "
    "paper_data/01_PHM2010/01_main_D1/bootstrap/dc_psr/bootstrap_config.json"
)

# Frozen point estimates (Acc/MacroF1/M_F1/M_Rec/M_to_E/M_to_L/Rev/Jump/Smooth), authoritative,
# from D1_9methods_bootstrap_CI.csv / D1_main_metrics.csv -- used only to cross-validate the local
# recomputation below (assert-and-fail-loud, never silently substituted).
FROZEN_B11_B12 = {
    "Multi-task TCN-GRU": {
        "Acc": 0.9901315789473685, "MacroF1": 0.9902304781561747, "M_F1": 0.9882352941176471,
        "M_Rec": 0.9767441860465116, "M_to_E": 0.02325581395348819, "M_to_L": 0.0,
        "Rev": 0, "Jump": 0, "Smooth": 0.023590099009900993,
    },
    "DC-PSR": {
        "Acc": 0.9868421052631579, "MacroF1": 0.9871020928241414, "M_F1": 0.984375,
        "M_Rec": 0.9767441860465116, "M_to_E": 0.02325581395348819, "M_to_L": 0.0,
        "Rev": 0, "Jump": 0, "Smooth": 0.018762706270627056,
    },
}


def paired_moving_block_bootstrap(log_lines, block_length=PAIRED_BLOCK_LENGTH,
                                   n_bootstrap=PAIRED_N_BOOTSTRAP, seed=PAIRED_SEED):
    """Paired moving-block bootstrap of the DC-PSR (B12) vs Multi-task TCN-GRU (B11) effect.

    For each of n_bootstrap replicates, ONE shared sequence of resampled positions (drawn from the
    same 304-run common test universe, non-circular overlapping-block draws, block_length=12) is
    applied to BOTH methods -- preserving the run-to-run pairing/correlation between the two methods'
    predictions on the same underlying test runs. The replicate-level difference is computed AFTER
    resampling (Delta = metric_B12 - metric_B11 per replicate), never by subtracting two
    independently-bootstrapped CIs.

    Direction convention: positive always favors DC-PSR.
      - Acc/MacroF1/M_F1/M_Rec (higher=better): effect_pp = (B12-B11)*100, in percentage points.
      - M_to_E/M_to_L (lower=better): effect_pp = (B11-B12)*100, in percentage points.
      - Smooth (lower=better, order-dependent): point-estimate-only relative-improvement %,
        (Smooth_B11 - Smooth_B12) / Smooth_B11 * 100. NOT bootstrapped -- block resampling breaks
        the true temporal adjacency this metric depends on (same documented reason the existing
        per-method bootstraps in paper_data/01_PHM2010/01_main_D1/bootstrap/ never gave Smooth a CI
        either; see their bootstrap_config.json "note" field). Reported as a point estimate only.
      - Rev/Jump: both methods are 0->0 on the true sequence (frozen data); point-estimate only,
        no CI, annotation-only in the figure.
    """
    df11 = load_predictions("Multi-task TCN-GRU")
    df12 = load_predictions("DC-PSR")
    truth11, pred11, probs11 = du.ordered_prediction_arrays(df11)
    truth12, pred12, probs12 = du.ordered_prediction_arrays(df12)
    n = len(truth11)
    assert n == len(truth12) == 304, f"expected 304 aligned runs, got {n}/{len(truth12)}"
    assert np.array_equal(truth11, truth12), \
        "Multi-task TCN-GRU and DC-PSR prediction files are not aligned on the same run/truth sequence"

    point11 = du.classification_metrics_from_ids(truth11, pred11)
    point12 = du.classification_metrics_from_ids(truth12, pred12)
    seq11 = du.sequence_diagnostics_from_ids(pred11, probs11)
    seq12 = du.sequence_diagnostics_from_ids(pred12, probs12)

    for name, computed, frozen_key in [("Multi-task TCN-GRU", {**point11, **seq11}, "Multi-task TCN-GRU"),
                                        ("DC-PSR", {**point12, **seq12}, "DC-PSR")]:
        frozen = FROZEN_B11_B12[frozen_key]
        for metric, val in computed.items():
            exp = frozen[metric]
            close = np.isclose(val, exp, atol=2e-4) if metric != "Rev" and metric != "Jump" else (val == exp)
            log_lines.append(f"{'PASS' if close else 'FAIL'}: paired-bootstrap point estimate {name} "
                              f"{metric}={val:.6f} vs frozen {exp}")
            assert close, f"{name} recomputed {metric}={val} does not match frozen {exp}"
    log_lines.append("PASS: paired-bootstrap point estimates (Acc/MacroF1/M_F1/M_Rec/M_to_E/M_to_L/"
                      "Rev/Jump/Smooth) for Multi-task TCN-GRU and DC-PSR match FROZEN_B11_B12 "
                      "(atol=2e-4), recomputed independently from sample-level 304-run predictions.")

    pp_metrics_higher = ["Acc", "MacroF1", "M_F1", "M_Rec"]
    pp_metrics_lower = ["M_to_E", "M_to_L"]
    all_pp_metrics = pp_metrics_higher + pp_metrics_lower
    rng = np.random.RandomState(seed)
    n_starts = n - block_length + 1
    n_blocks_needed = int(np.ceil(n / block_length))
    deltas = {m: np.empty(n_bootstrap, dtype=float) for m in all_pp_metrics}
    for b in range(n_bootstrap):
        starts = rng.randint(0, n_starts, size=n_blocks_needed)
        idx = np.concatenate([np.arange(s, s + block_length) for s in starts])[:n]
        m11 = du.classification_metrics_from_ids(truth11[idx], pred11[idx])
        m12 = du.classification_metrics_from_ids(truth12[idx], pred12[idx])
        for m in pp_metrics_higher:
            deltas[m][b] = (m12[m] - m11[m]) * 100.0
        for m in pp_metrics_lower:
            deltas[m][b] = (m11[m] - m12[m]) * 100.0
    log_lines.append(f"PASS: paired moving-block bootstrap complete -- block_length={block_length}, "
                      f"n_bootstrap={n_bootstrap}, seed={seed}, n_test={n}, identical block-start "
                      f"indices applied to both methods per replicate (source: {PAIRED_PROTOCOL_SOURCE}).")

    rows = []
    for m in pp_metrics_higher:
        effect = (point12[m] - point11[m]) * 100.0
        rows.append({
            "metric": m, "B11_value": point11[m], "B12_value": point12[m],
            "effect": effect, "effect_unit": "pp",
            "CI_low": float(np.percentile(deltas[m], 2.5)), "CI_high": float(np.percentile(deltas[m], 97.5)),
            "bootstrap_type": "paired_moving_block_bootstrap",
            "n_test": n, "block_length": block_length, "n_bootstrap": n_bootstrap, "seed": seed,
        })
    for m in pp_metrics_lower:
        effect = (point11[m] - point12[m]) * 100.0
        rows.append({
            "metric": m, "B11_value": point11[m], "B12_value": point12[m],
            "effect": effect, "effect_unit": "pp",
            "CI_low": float(np.percentile(deltas[m], 2.5)), "CI_high": float(np.percentile(deltas[m], 97.5)),
            "bootstrap_type": "paired_moving_block_bootstrap",
            "n_test": n, "block_length": block_length, "n_bootstrap": n_bootstrap, "seed": seed,
        })
    smooth_effect = (seq11["Smooth"] - seq12["Smooth"]) / seq11["Smooth"] * 100.0
    rows.append({
        "metric": "Smooth", "B11_value": seq11["Smooth"], "B12_value": seq12["Smooth"],
        "effect": smooth_effect, "effect_unit": "relative_%",
        "CI_low": "", "CI_high": "",
        "bootstrap_type": "point_estimate_no_CI (order-dependent metric; block resampling injects "
                           "artificial sequence-boundary discontinuities -- same exclusion already "
                           "applied to every per-method bootstrap in paper_data/01_PHM2010/01_main_D1/bootstrap/)",
        "n_test": n, "block_length": block_length, "n_bootstrap": n_bootstrap, "seed": seed,
    })
    for m in ("Rev", "Jump"):
        rows.append({
            "metric": m, "B11_value": seq11[m], "B12_value": seq12[m],
            "effect": seq11[m] - seq12[m], "effect_unit": "count",
            "CI_low": "", "CI_high": "",
            "bootstrap_type": "point_estimate_no_CI (both methods 0 on the true sequence; "
                               "order-dependent, not bootstrapped)",
            "n_test": n, "block_length": block_length, "n_bootstrap": n_bootstrap, "seed": seed,
        })
    out = pd.DataFrame(rows, columns=["metric", "B11_value", "B12_value", "effect", "effect_unit",
                                       "CI_low", "CI_high", "bootstrap_type", "n_test",
                                       "block_length", "n_bootstrap", "seed"])
    log_lines.append(f"PASS: DC-PSR vs Multi-task TCN-GRU paired effects -- "
                      + "; ".join(f"{r['metric']}={r['effect']:+.3f}{r['effect_unit'] if r['effect_unit']!='pp' else 'pp'}"
                                  for r in rows if r["metric"] not in ("Rev", "Jump")))
    return out


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

    paired_df = paired_moving_block_bootstrap(log_lines)

    main_df.to_csv(os.path.join(DERIVED_DIR, "D1_heatmap_table.csv"), index=False, encoding="utf-8")
    ac_df.to_csv(os.path.join(DERIVED_DIR, "accuracy_consistency_points.csv"), index=False, encoding="utf-8")
    b1112_df.to_csv(os.path.join(DERIVED_DIR, "B11_B12_controlled_comparison.csv"), index=False, encoding="utf-8")
    rep_df.to_csv(os.path.join(DERIVED_DIR, "representative_recomputed.csv"), index=False, encoding="utf-8")
    paired_df.to_csv(os.path.join(DERIVED_DIR, "B11_B12_paired_bootstrap_effects.csv"), index=False, encoding="utf-8")
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
