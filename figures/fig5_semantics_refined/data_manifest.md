# Figure 5 refined — data manifest

## Source data

| Panel(s) | Project-relative source | Rows used | Variables / operation | SHA-256 |
|---|---|---:|---|---|
| (a), (b), (c), (e) | `补充材料/小论文/9_probability_wear_consistency_analysis/Data_5_4_A6_probability_wear_trajectory.csv` | 304 | `run_id`, `VB_true`, `q_true`, `q_pred`, stage labels, and Early/Middle/Late probabilities | `c20016d4479b6faa7de4a3f5205f2517c6b67d62f75d6f98daa07fd930102557` |
| (d) | `补充材料/小论文/10_第五章顶刊风格可视化/figures_representation_space/repr_hidden_hct.csv` | 304 (`split=test_C6`, `condition=C6`) | `h_00`–`h_63`, standardized feature-wise; two-component deterministic NumPy SVD PCA | `b259ac455887fe1b49e26afa54fe4f3e199a390623532210a1e0b16360ebb923` |

No synthetic observations, fitted smoothing, retraining, label-guided embedding, or manual point deletion are used.

## Recomputed audit values

- Lifecycle observations: **304**
- $R^2$: **0.747801875266**
- Spearman $\rho$: **0.963458757032**
- MAE: **0.113230994503**
- Stage agreement: **98.6842%**
- Predicted-stage counts (Early / Middle / Late): **87 / 127 / 90**
- Median true VB (Early / Middle / Late): **102.608842 / 123.141072 / 210.392291**
- PCA explained variance (PC1 / PC2): **55.1835% / 36.4781%**

## Display transformations

- Relative life is min–max normalized from `run_id` only for the horizontal lifecycle coordinate.
- Panel (b) applies the standard barycentric-to-Cartesian mapping to the three probabilities.
- Panel (c) uses logarithmic hex-bin counts for display; the statistics are calculated from all raw pairs.
- Panel (d) standardizes each saved hidden feature before deterministic SVD PCA, exactly as in the existing Figure 5 workflow.
- Panel (e) groups unmodified `VB_true` by `pred_stage` and displays every observation with deterministic jitter.
