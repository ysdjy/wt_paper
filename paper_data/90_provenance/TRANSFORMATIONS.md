
# Transformations

- Cross-dataset: `ΔAcc = B12 - B11`; `ΔM-F1 = B12 - B11`; `Smooth_benefit = B11 - B12`; `Jump_benefit = B11 - B12`.
- Fig.2 normalized scores: within each task, `(x-min)/(max-min)` for high-is-good and `(max-x)/(max-min)` for Smooth. Absolute values are retained separately.
- Fig.4 delta table: `Ai - A1`; absolute A1-A6 remains authoritative.
- Fig.5 q statistics: directly recomputed on all 304 `q_true`/`q_pred` pairs; no `q_pred_norm` substitution.
- Mendeley task summaries retain across-seed std; collapsed dataset effects average the three task means and do not pool runs.
- NASA summary retains across-task std from N1-N4; it is not represented as across-seed uncertainty.
