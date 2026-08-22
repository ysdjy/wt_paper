"""
Shared PCA scores for V4: fig4(d) and fig5(a)/(b)/(c) must show the SAME latent geometry.

Problem this fixes: in v1-v3, fig4's "latent manifold overview" panel and fig5's own PCA panels
each independently fit PCA on the same 64-D hidden_representation.csv. PCA sign/rotation is
mathematically arbitrary (an eigenvector and its negation are equally valid), so two independent
fits can legitimately come out mirrored relative to each other -- which would make the SAME shared
representation look inconsistent across the two hero figures for a reader, even though nothing
about the underlying data changed. This script fits PCA exactly ONCE and both figures read its
output, so they are always geometrically identical.

Sign convention (deterministic, documented, not a data change):
  - PC1 sign is chosen so that corr(PC1, q_true) > 0 -- i.e. Early (low q) trends toward one end,
    Late (high q) trends toward the other, consistently, run to run.
  - PC2 sign is left exactly as numpy's SVD produces it (no additional constraint specified by the
    task brief). If a future round wants a second deterministic rule for PC2, add it here, in one
    place, so both figures stay consistent automatically.
PCA sign/rotation carries no statistical meaning; fixing it is a display convention, not a change
to any data value.

Output: paper_data/figure/_shared/derived/shared_pca_scores_v4.csv
Columns: run_id, sample_id, PC1, PC2, true_stage, pred_stage, q_true, q_hat, uncertainty, entropy,
         misclassified

Run: python paper_data/figure/_shared/prepare_shared_pca_v4.py
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import data_utils as du  # noqa: E402

HERE = os.path.dirname(__file__)
DERIVED_DIR = os.path.join(HERE, "derived")
LOG_DIR = os.path.join(HERE, "logs")
os.makedirs(DERIVED_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)


def main():
    log_lines = []
    hidden = du.read_csv("07_figure_ready", "fig5", "hidden_representation.csv")
    assert len(hidden) == 304, f"expected 304 rows, got {len(hidden)}"
    h_cols = [c for c in hidden.columns if c.startswith("h_")]
    assert len(h_cols) == 64, f"expected 64 hidden dims, got {len(h_cols)}"
    log_lines.append(f"PASS: hidden_representation.csv has 304 rows x {len(h_cols)} h_* columns.")

    X = hidden[h_cols].values
    scores, explained, components = du.pca_2d(X)

    # Deterministic PC1 sign: corr(PC1, q_true) > 0
    corr_pc1_q = np.corrcoef(scores[:, 0], hidden["q_true"].values)[0, 1]
    if corr_pc1_q < 0:
        scores[:, 0] = -scores[:, 0]
        corr_pc1_q = -corr_pc1_q
        log_lines.append("PC1 sign flipped so corr(PC1, q_true) > 0 (display convention only, no data change).")
    else:
        log_lines.append("PC1 sign already satisfies corr(PC1, q_true) > 0, no flip needed.")
    assert corr_pc1_q > 0
    log_lines.append(f"PASS: corr(PC1, q_true) = {corr_pc1_q:.4f} (> 0, as required).")
    log_lines.append("PC2 sign left exactly as numpy SVD produced it -- no additional sign rule specified this round.")

    out = pd.DataFrame({
        "run_id": hidden["run_id"].values,
        "sample_id": hidden["sample_id"].values,
        "PC1": scores[:, 0],
        "PC2": scores[:, 1],
        "true_stage": hidden["true_stage"].values,
        "pred_stage": hidden["pred_stage"].values,
        "q_true": hidden["q_true"].values,
        "q_hat": hidden["q_hat"].values,
        "uncertainty": hidden["uncertainty"].values,
        "entropy": hidden["entropy"].values,
        "misclassified": hidden["misclassified"].values,
    })
    assert len(out) == 304 and out.isna().sum().sum() == 0
    out_path = os.path.join(DERIVED_DIR, "shared_pca_scores_v4.csv")
    out.to_csv(out_path, index=False, encoding="utf-8")
    log_lines.append(f"PASS: wrote {out_path} (304 rows, 0 NaN).")
    log_lines.append(f"Explained variance ratio: PC1={explained[0]:.4f}, PC2={explained[1]:.4f}.")

    with open(os.path.join(LOG_DIR, "validation_shared_pca_v4.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")
    print("\n".join(log_lines))
    print("Shared PCA v4 done.")


if __name__ == "__main__":
    main()
