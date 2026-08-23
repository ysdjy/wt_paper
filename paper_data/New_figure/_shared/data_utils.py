"""
Shared data-loading / metric-recomputation helpers for paper_data/New_figure/Fig4_2..Fig4_5.

Ported verbatim from paper_data/figure/_shared/data_utils.py (validated, reused per this round's
explicit "reuse frozen-data loading / metric calculation / confusion-matrix / PCA logic" policy --
see FIGURE_REBUILD_AUDIT.md section 1). Only addition: pca_2d_standardized(), needed because
Fig4-5's raw-feature PCA must follow the original manuscript pipeline (mean-center + std-normalize
+ SVD, per 代码/8.2图18.py::pca_2d), which the old pca_2d() (mean-center only, fine for the
already-homogeneous-scale 64-D hidden representation) does not do -- the 45 raw feature columns
have very different scales and would be dominated by a few high-variance columns without
standardization.

All functions read CSVs with explicit encoding="utf-8" and never hardcode headline numbers --
callers must recompute from frozen CSVs and assert/np.isclose against expected values.
"""
import os
import numpy as np
import pandas as pd

STAGE_ORDER = ["early", "middle", "late"]

# Resolve paper_data root relative to this file: New_figure/_shared/data_utils.py -> paper_data/
PAPER_DATA_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
NEW_FIGURE_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))


def pd_path(*parts):
    return os.path.join(PAPER_DATA_ROOT, *parts)


def nf_path(*parts):
    """Path relative to paper_data/New_figure/ (for this round's own derived/frozen files)."""
    return os.path.join(NEW_FIGURE_ROOT, *parts)


def read_csv(*parts, **kwargs):
    path = pd_path(*parts)
    kwargs.setdefault("encoding", "utf-8")
    return pd.read_csv(path, **kwargs)


def read_csv_nf(*parts, **kwargs):
    path = nf_path(*parts)
    kwargs.setdefault("encoding", "utf-8")
    return pd.read_csv(path, **kwargs)


def confusion_counts(true_stage, pred_stage, labels=STAGE_ORDER):
    """Return (counts, row_normalized) both as (len(labels) x len(labels)) numpy arrays.
    counts[i, j] = number of samples with true label i predicted as label j."""
    n = len(labels)
    idx = {lab: i for i, lab in enumerate(labels)}
    counts = np.zeros((n, n), dtype=int)
    for t, p in zip(true_stage, pred_stage):
        counts[idx[t], idx[p]] += 1
    row_sums = counts.sum(axis=1, keepdims=True)
    row_norm = np.divide(counts, row_sums, out=np.zeros_like(counts, dtype=float), where=row_sums != 0)
    return counts, row_norm


def precision_recall_f1_per_class(true_stage, pred_stage, labels=STAGE_ORDER):
    """Manual per-class precision/recall/F1 (no sklearn dependency)."""
    true_stage = np.asarray(true_stage)
    pred_stage = np.asarray(pred_stage)
    out = {}
    for lab in labels:
        tp = np.sum((true_stage == lab) & (pred_stage == lab))
        fp = np.sum((true_stage != lab) & (pred_stage == lab))
        fn = np.sum((true_stage == lab) & (pred_stage != lab))
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        out[lab] = {"precision": precision, "recall": recall, "f1": f1, "support": int(tp + fn)}
    return out


def accuracy(true_stage, pred_stage):
    true_stage = np.asarray(true_stage)
    pred_stage = np.asarray(pred_stage)
    return float(np.mean(true_stage == pred_stage))


def macro_f1(true_stage, pred_stage, labels=STAGE_ORDER):
    pc = precision_recall_f1_per_class(true_stage, pred_stage, labels)
    return float(np.mean([pc[l]["f1"] for l in labels]))


def r2_coefficient_of_determination(y_true, y_pred):
    """Standard coefficient of determination 1 - SS_res/SS_tot using y_pred AS-IS (no refit
    regression line). Matches Q_DEFINITIONS.md: raw q_pred paired directly with q_true, never
    renormalized/refit. NOT the same as squared Pearson r (verified: pearson_r**2=0.881 vs
    coef_det=0.748 on frozen fig5/q_agreement.csv -- the manuscript's R^2~=0.748 is this formula)."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - y_true.mean()) ** 2)
    return float(1 - ss_res / ss_tot)


def pca_2d(X):
    """Mean-center-only 2-component PCA via numpy SVD. Matches paper_data/figure's existing
    shared_pca_scores_v4.csv convention -- use this only when cross-checking against that file
    (already-homogeneous-scale 64-D hidden representation)."""
    X = np.asarray(X, dtype=float)
    mean = X.mean(axis=0)
    Xc = X - mean
    U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
    scores = Xc @ Vt[:2].T
    total_var = np.sum(S ** 2)
    explained = (S[:2] ** 2) / total_var
    return scores, explained, Vt[:2]


def pca_2d_standardized(X):
    """Mean-center + std-normalize + SVD PCA -- the ORIGINAL manuscript's own pipeline
    (代码/8.2图18.py::pca_2d). Required for the raw-feature PCA (45 columns of very different
    scale); also used for the shared-representation PCA in Fig4-5 Layer I so both rows of the
    raw-vs-shared comparison use the identical, manuscript-faithful pipeline."""
    X = np.asarray(X, dtype=float)
    X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
    Xc = X - X.mean(axis=0, keepdims=True)
    Xc = Xc / (Xc.std(axis=0, keepdims=True) + 1e-12)
    U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
    scores = Xc @ Vt[:2].T
    total_var = np.sum(S ** 2)
    explained = (S[:2] ** 2) / total_var if total_var > 0 else np.array([0.0, 0.0])
    return scores, explained, Vt[:2]


def ternary_coords(p_early, p_middle, p_late):
    """Map (p_E, p_M, p_L) simplex coordinates to 2D ternary-plot (x, y).
    Vertex order: Early=left(0,0), Late=right(1,0), Middle=top(0.5, sqrt(3)/2)."""
    p_early = np.asarray(p_early, dtype=float)
    p_middle = np.asarray(p_middle, dtype=float)
    p_late = np.asarray(p_late, dtype=float)
    x = p_late + 0.5 * p_middle
    y = (np.sqrt(3) / 2) * p_middle
    return x, y
