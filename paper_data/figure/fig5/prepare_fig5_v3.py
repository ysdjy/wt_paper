"""
Fig.5 v3 (paper Fig. 4-6) -- Python data-preparation half of a Python+MATLAB split build.

This script does NOT render anything. It loads the same real data v1 (plot_fig5.py) uses --
paper_data/07_figure_ready/fig5/hidden_representation.csv (304 rows x 64 h_* dims) and
lifecycle_semantics.csv (304 rows) -- validates it, fits ONE PCA (numpy SVD, via
_shared/data_utils.py::pca_2d, independent of v1's own PCA run but the same method), and exports
three derived CSVs that paper_data/figure/fig5/plot_fig5_v3.m reads to render panels (a)-(e).

No fabrication: every row in every exported CSV traces back to one of the 304 real C6 test runs.
MATLAB does not refit PCA, does not interpolate a grid, and does not add points -- see
plot_fig5_v3.m's own header comment for what its "ribbon extrusion" in panels (d)/(e) is (a purely
visual thickening of a 1-D real trajectory, not a second measured dimension).

Run: python paper_data/figure/fig5/prepare_fig5_v3.py
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_shared"))
import data_utils as du  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
from plot_fig5 import load, fit_pca  # noqa: E402

HERE = os.path.dirname(__file__)
DERIVED_DIR = os.path.join(HERE, "derived")
LOG_DIR = os.path.join(HERE, "logs")
os.makedirs(DERIVED_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)


def main():
    log_lines = []
    hidden, lifecycle = load()
    assert len(hidden) == 304 and len(lifecycle) == 304
    h_cols = [c for c in hidden.columns if c.startswith("h_")]
    assert len(h_cols) == 64
    log_lines.append(f"PASS: hidden_representation.csv={len(hidden)} rows x {len(h_cols)} h_* cols; "
                      f"lifecycle_semantics.csv={len(lifecycle)} rows.")

    scores = fit_pca(hidden, log_lines)
    assert not np.isnan(scores).any()

    # --- pca_scores_v3.csv ---
    pca_df = pd.DataFrame({
        "sample_id": hidden["sample_id"].values,
        "PC1": scores[:, 0],
        "PC2": scores[:, 1],
        "true_stage": hidden["true_stage"].values,
        "pred_stage": hidden["pred_stage"].values,
        "q_true": hidden["q_true"].values,
        "q_hat": hidden["q_hat"].values,
        "uncertainty": hidden["uncertainty"].values,
        "entropy": hidden["entropy"].values,
        "misclassified": hidden["misclassified"].values.astype(int),
    })
    assert len(pca_df) == 304 and pca_df.isna().sum().sum() == 0
    pca_path = os.path.join(DERIVED_DIR, "pca_scores_v3.csv")
    pca_df.to_csv(pca_path, index=False, encoding="utf-8")
    log_lines.append(f"PASS: wrote {pca_path} (304 rows, 10 cols, 0 NaN).")

    # --- stage_ridges_v3.csv ---
    lc = lifecycle.sort_values("relative_life").reset_index(drop=True)
    ridge_df = lc[["relative_life", "prob_early", "prob_middle", "prob_late"]].copy()
    ridge_df.insert(0, "run_id", lc["run_id"].values if "run_id" in lc.columns else np.arange(len(lc)))
    assert len(ridge_df) == 304 and ridge_df.isna().sum().sum() == 0
    assert (ridge_df["relative_life"].diff().dropna() >= 0).all(), "must be sorted by relative_life"
    ridge_path = os.path.join(DERIVED_DIR, "stage_ridges_v3.csv")
    ridge_df.to_csv(ridge_path, index=False, encoding="utf-8")
    log_lines.append(f"PASS: wrote {ridge_path} (304 rows, sorted by relative_life, 0 NaN).")

    # --- confidence_trajectory_v3.csv ---
    conf_df = lc[["relative_life", "q_pred", "max_prob", "pred_stage"]].copy()
    conf_df.insert(0, "run_id", lc["run_id"].values if "run_id" in lc.columns else np.arange(len(lc)))
    assert len(conf_df) == 304 and conf_df[["relative_life", "q_pred", "max_prob"]].isna().sum().sum() == 0
    conf_path = os.path.join(DERIVED_DIR, "confidence_trajectory_v3.csv")
    conf_df.to_csv(conf_path, index=False, encoding="utf-8")
    log_lines.append(f"PASS: wrote {conf_path} (304 rows, sorted by relative_life, 0 NaN).")

    # sanity read-back
    for p, expected_rows in [(pca_path, 304), (ridge_path, 304), (conf_path, 304)]:
        back = pd.read_csv(p, encoding="utf-8")
        assert len(back) == expected_rows
        log_lines.append(f"PASS: read-back check {os.path.basename(p)}: shape={back.shape}")

    print(pca_df.describe(include="all").to_string())
    print()
    print(ridge_df.head().to_string())
    print()
    print(conf_df.head().to_string())

    with open(os.path.join(LOG_DIR, "validation_v3_python.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
    print("\n".join(log_lines))
    print("prepare_fig5_v3.py done.")


if __name__ == "__main__":
    main()
