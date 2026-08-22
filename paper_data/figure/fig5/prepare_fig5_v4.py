"""
Fig.5 v4 (paper Fig. 4-6) -- Python data-preparation half of a Python+MATLAB split build.

Unlike v3, panels (a)/(b)/(c) do NOT fit their own PCA here -- they read
paper_data/figure/_shared/derived/shared_pca_scores_v4.csv directly (built once by
_shared/prepare_shared_pca_v4.py), which is the SAME file paper_data/figure/fig4/plot_fig4_v4.py's
panel (d) reads. This guarantees Fig.4 and Fig.5 show geometrically identical latent geometry --
PCA sign/rotation is mathematically arbitrary, so two independent fits could legitimately mirror
each other even though both are "correct," which would make the same shared representation look
inconsistent across the two hero figures for a reader. plot_fig5_v4.m reads the shared CSV via a
relative path (../_shared/derived/shared_pca_scores_v4.csv) rather than a local copy, so there is
zero risk of the two files drifting apart.

This script's own job is the panels (d)/(e) MATLAB inputs:
  - derived/stage_ridges_v4.csv: real (run_id, relative_life, prob_early/middle/late), 304 rows,
    sorted by relative_life -- unchanged in kind from v3.
  - derived/confidence_ribbon_v4.csv: real (run_id, relative_life, q_pred, max_prob, pred_stage)
    PLUS real per-run `uncertainty`, joined in from the shared PCA file via run_id. The join is
    explicitly validated as exact 304<->304 one-to-one before being trusted (asserted below) --
    this is the data that drives panel (e)'s uncertainty-proportional ribbon half-width in MATLAB.

No fabrication: every row in every exported CSV traces back to one of the 304 real C6 test runs.
Interpolation (PCHIP, 304 -> ~800 display vertices) happens in MATLAB at render time for visual
smoothness only, never baked into these CSVs -- keeping the "real vs display-only" boundary
auditable at the file level.

Run: python paper_data/figure/fig5/prepare_fig5_v4.py
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_shared"))
import data_utils as du  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
from plot_fig5 import load  # noqa: E402  (v1's load(): hidden_representation + lifecycle_semantics)

HERE = os.path.dirname(__file__)
DERIVED_DIR = os.path.join(HERE, "derived")
LOG_DIR = os.path.join(HERE, "logs")
SHARED_PCA_PATH = os.path.join(HERE, "..", "_shared", "derived", "shared_pca_scores_v4.csv")
os.makedirs(DERIVED_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)


def main():
    log_lines = []
    hidden, lifecycle = load()
    assert len(hidden) == 304 and len(lifecycle) == 304
    log_lines.append(f"PASS: hidden_representation.csv={len(hidden)} rows; lifecycle_semantics.csv={len(lifecycle)} rows.")

    assert os.path.exists(SHARED_PCA_PATH), (
        f"Shared PCA file not found at {SHARED_PCA_PATH} -- run "
        f"paper_data/figure/_shared/prepare_shared_pca_v4.py first."
    )
    shared_pca = pd.read_csv(SHARED_PCA_PATH, encoding="utf-8")
    assert len(shared_pca) == 304
    log_lines.append(f"PASS: shared_pca_scores_v4.csv found and has 304 rows -- plot_fig5_v4.m will read this "
                     f"file directly (not a local copy), guaranteeing identical coordinates to fig4(d).")

    # --- stage_ridges_v4.csv: real (relative_life, prob_early/middle/late), sorted ---
    lc = lifecycle.sort_values("relative_life").reset_index(drop=True)
    ridge_df = lc[["run_id", "relative_life", "prob_early", "prob_middle", "prob_late"]].copy()
    assert len(ridge_df) == 304 and ridge_df.isna().sum().sum() == 0
    assert (ridge_df["relative_life"].diff().dropna() >= 0).all()
    ridge_path = os.path.join(DERIVED_DIR, "stage_ridges_v4.csv")
    ridge_df.to_csv(ridge_path, index=False, encoding="utf-8")
    log_lines.append(f"PASS: wrote {ridge_path} (304 rows, sorted by relative_life, 0 NaN).")

    # --- confidence_ribbon_v4.csv: real (relative_life, q_pred, max_prob, pred_stage) + real
    #     uncertainty joined in from the shared PCA file via run_id ---
    conf_df = lc[["run_id", "relative_life", "q_pred", "max_prob", "pred_stage"]].copy()
    uncertainty_by_run = shared_pca[["run_id", "uncertainty"]].drop_duplicates()
    assert uncertainty_by_run["run_id"].is_unique, "shared PCA run_id must be unique before joining"
    assert conf_df["run_id"].is_unique, "lifecycle run_id must be unique before joining"

    merged = conf_df.merge(uncertainty_by_run, on="run_id", how="inner")
    # Validate the join is exact 304<->304 one-to-one -- required before trusting this data to
    # drive panel (e)'s ribbon width in MATLAB.
    assert len(merged) == 304, f"join produced {len(merged)} rows, expected exactly 304 (one-to-one)"
    assert merged["run_id"].nunique() == 304
    assert merged["uncertainty"].isna().sum() == 0
    log_lines.append(f"PASS: uncertainty join to lifecycle data is exact 304<->304 one-to-one via run_id "
                     f"(no missing, no duplication).")

    merged = merged.sort_values("relative_life").reset_index(drop=True)
    conf_path = os.path.join(DERIVED_DIR, "confidence_ribbon_v4.csv")
    merged.to_csv(conf_path, index=False, encoding="utf-8")
    log_lines.append(f"PASS: wrote {conf_path} (304 rows, sorted by relative_life, real uncertainty attached, 0 NaN).")

    u = merged["uncertainty"].values
    log_lines.append(f"Uncertainty range for panel (e) ribbon-width mapping: min={u.min():.4f}, max={u.max():.4f}, "
                     f"mean={u.mean():.4f}.")

    for p, expected_rows in [(ridge_path, 304), (conf_path, 304)]:
        back = pd.read_csv(p, encoding="utf-8")
        assert len(back) == expected_rows
        log_lines.append(f"PASS: read-back check {os.path.basename(p)}: shape={back.shape}")

    with open(os.path.join(LOG_DIR, "validation_v4_python.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
    print("\n".join(log_lines))
    print("prepare_fig5_v4.py done.")


if __name__ == "__main__":
    main()
