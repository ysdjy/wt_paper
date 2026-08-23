"""
Fig4-5 (退化语义与表示几何) data loading, PCA computation, and headline-number validation.

Inputs (read-only):
  - New_figure/Fig4_5.../derived/repr_raw_features_frozen_780.csv    (Layer I, raw-vs-shared, panel A)
  - New_figure/Fig4_5.../derived/repr_hidden_hct_frozen_780.csv      (Layer I, raw-vs-shared, panel B)
    -- both already provenance-verified byte-identical to the frozen 304-run C6 test universe on
       every overlapping metadata column (see RAW_FEATURE_PROVENANCE.md); this script does not
       re-derive them, only loads and PCA-projects.
  - 07_figure_ready/fig5/lifecycle_semantics.csv   (304 rows, panels C/D/E2)
  - 07_figure_ready/fig5/q_agreement.csv           (304 rows, panel E1)
  - 07_figure_ready/fig5/wear_by_predicted_stage.csv  (3-row aggregate, cross-check for E2)

PCA pipeline: mean-center + std-normalize + SVD (代码/8.2图18.py::pca_2d convention), via
_shared/data_utils.py::pca_2d_standardized -- NOT the mean-center-only pca_2d used by the old
paper_data/figure/_shared/prepare_shared_pca_v4.py, per this round's explicit instruction to follow
the original manuscript's own PCA pipeline for this figure.
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

META_COLS = {
    "sample_id", "split", "condition", "run_id", "true_stage", "true_stage_id",
    "pred_stage", "q_true", "q_hat", "p_E", "p_M", "p_L",
    "uncertainty", "entropy", "misclassified",
}


def load_raw_hidden():
    raw = pd.read_csv(os.path.join(DERIVED_DIR, "repr_raw_features_frozen_780.csv"), encoding="utf-8")
    hidden = pd.read_csv(os.path.join(DERIVED_DIR, "repr_hidden_hct_frozen_780.csv"), encoding="utf-8")
    assert len(raw) == 780 and len(hidden) == 780
    assert (raw["sample_id"].values == hidden["sample_id"].values).all(), "raw/hidden must be row-aligned"
    return raw, hidden


def feature_cols(df, hidden=False):
    if hidden:
        return [c for c in df.columns if c.startswith("h_")]
    return [c for c in df.columns if c not in META_COLS and pd.api.types.is_numeric_dtype(df[c])]


def pca_with_sign_convention(df, hidden, log_lines, tag):
    cols = feature_cols(df, hidden=hidden)
    assert len(cols) == (64 if hidden else 45), f"{tag}: unexpected feature count {len(cols)}"
    scores, explained, _ = du.pca_2d_standardized(df[cols].values)
    q = df["q_true"].values.astype(float)
    corr = np.corrcoef(scores[:, 0], q)[0, 1]
    if corr < 0:
        scores[:, 0] = -scores[:, 0]
        corr = -corr
        log_lines.append(f"{tag}: PC1 sign flipped so corr(PC1, q_true) > 0 (display convention, no data change).")
    else:
        log_lines.append(f"{tag}: PC1 sign already satisfies corr(PC1, q_true) > 0, no flip needed.")
    log_lines.append(f"{tag}: PCA done ({len(cols)} features -> 2D), explained variance PC1={explained[0]:.4f} "
                      f"PC2={explained[1]:.4f}, corr(PC1,q_true)={corr:.4f}.")
    return scores


def load_lifecycle():
    df = du.read_csv("07_figure_ready", "fig5", "lifecycle_semantics.csv")
    assert len(df) == 304
    return df


def load_q_agreement():
    df = du.read_csv("07_figure_ready", "fig5", "q_agreement.csv")
    assert len(df) == 304
    assert (df["q_comparison_definition"] == "q_true_vs_raw_q_pred_no_renormalization").all()
    return df


def load_wear_by_stage():
    df = du.read_csv("07_figure_ready", "fig5", "wear_by_predicted_stage.csv")
    assert len(df) == 3
    return df


def validate(q_df, wear_df, lifecycle_df, log_lines):
    r2 = du.r2_coefficient_of_determination(q_df["q_true"].values, q_df["q_pred"].values)
    rho = pd.Series(q_df["q_true"]).corr(pd.Series(q_df["q_pred"]), method="spearman")
    mae = float(np.mean(np.abs(q_df["q_true"].values - q_df["q_pred"].values)))
    checks = [("R2", r2, 0.748, 0.01), ("Spearman rho", rho, 0.963, 0.01), ("MAE", mae, 0.113, 0.005)]
    ok = True
    for name, val, exp, atol in checks:
        close = np.isclose(val, exp, atol=atol)
        ok = ok and close
        log_lines.append(f"{'PASS' if close else 'FAIL'}: q-agreement {name}={val:.4f} vs expected {exp} (atol={atol})")

    expected_vb = {"early": 100.55, "middle": 126.29, "late": 205.46}
    for _, r in wear_df.iterrows():
        exp = expected_vb[r["predicted_stage"]]
        close = np.isclose(r["VB_mean"], exp, atol=0.5)
        ok = ok and close
        log_lines.append(f"{'PASS' if close else 'FAIL'}: VB_mean[{r['predicted_stage']}]={r['VB_mean']:.2f} vs expected {exp}")

    assert lifecycle_df["run_id"].is_monotonic_increasing, "lifecycle_semantics.csv must be run_id-ordered for panel C/D surfaces"
    assert ok, "q-agreement or VB headline checks failed"


def main():
    log_lines = []
    raw, hidden = load_raw_hidden()
    lifecycle_df = load_lifecycle()
    q_df = load_q_agreement()
    wear_df = load_wear_by_stage()
    log_lines.append("PASS: loaded raw (780x60), hidden (780x79), lifecycle_semantics (304 rows), "
                      "q_agreement (304 rows), wear_by_predicted_stage (3 rows).")

    validate(q_df, wear_df, lifecycle_df, log_lines)

    raw_scores = pca_with_sign_convention(raw, hidden=False, log_lines=log_lines, tag="raw")
    hidden_scores = pca_with_sign_convention(hidden, hidden=True, log_lines=log_lines, tag="hidden")

    raw_out = raw[["sample_id", "split", "condition", "run_id", "true_stage", "pred_stage",
                    "q_true", "q_hat", "uncertainty", "entropy", "misclassified"]].copy()
    raw_out["PC1"], raw_out["PC2"] = raw_scores[:, 0], raw_scores[:, 1]
    hidden_out = hidden[["sample_id", "split", "condition", "run_id", "true_stage", "pred_stage",
                          "q_true", "q_hat", "uncertainty", "entropy", "misclassified"]].copy()
    hidden_out["PC1"], hidden_out["PC2"] = hidden_scores[:, 0], hidden_scores[:, 1]

    raw_out.to_csv(os.path.join(DERIVED_DIR, "raw_pca_780.csv"), index=False, encoding="utf-8")
    hidden_out.to_csv(os.path.join(DERIVED_DIR, "hidden_pca_780.csv"), index=False, encoding="utf-8")
    lifecycle_df.to_csv(os.path.join(DERIVED_DIR, "lifecycle_semantics.csv"), index=False, encoding="utf-8")
    q_df.to_csv(os.path.join(DERIVED_DIR, "q_agreement.csv"), index=False, encoding="utf-8")
    wear_df.to_csv(os.path.join(DERIVED_DIR, "wear_by_predicted_stage.csv"), index=False, encoding="utf-8")

    with open(os.path.join(LOG_DIR, "validation.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
    print("\n".join(log_lines))
    print(f"\nWrote files to {DERIVED_DIR}")


if __name__ == "__main__":
    main()
