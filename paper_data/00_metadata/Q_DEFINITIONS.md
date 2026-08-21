
# Frozen q and wear definitions (Q_DEFINITION_V1)

This document is normative for every Fig.5 table, plot, caption, and statistic.

- `VB_true`: observed flank-wear value for the run, in the source wear unit; it is never normalized or model-predicted.
- `VB_smooth`: centered 7-run rolling mean of `VB_true` within one condition, with `min_periods=1` at the ends.
- `q_true`: condition-relative normalized wear position, `(VB_smooth - min(VB_smooth)) / (max(VB_smooth) - min(VB_smooth) + 1e-12)`. It is the regression target and lies in `[0,1]`.
- `q_pred`: raw sigmoid output of the frozen model q head for the run. This is the only prediction field paired with `q_true` for MAE, R2, Spearman rho, and other agreement statistics.
- `q_pred_norm`: display-only min-max normalization of `q_pred` over the frozen C6 304-run test universe, `(q_pred - min(q_pred)) / (max(q_pred) - min(q_pred) + 1e-12)`. It must not replace `q_pred` in agreement statistics.
- `relative_life`: index position in the frozen test lifecycle, `(run_id - 12) / (315 - 12)`. It is an x-axis coordinate, not a wear label and not a model target.

Frozen relationship: `VB_true -> centered rolling mean -> VB_smooth -> condition-relative min-max -> q_true`; the model independently emits `q_pred`; `q_pred_norm` is a post-hoc display transform only. Do not compare `q_true` against `q_pred_norm` when reporting model agreement.
