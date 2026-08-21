# Figure 5 — semantic consistency (refined)

This directory contains a visual refinement of the existing Figure 5. The scientific evidence chain, sample set, stage definitions, continuous-degradation variables, PCA procedure, and physical-wear grouping are unchanged.

## Outputs

- `fig5_semantics_refined.svg` — primary editable vector figure; text remains editable.
- `fig5_semantics_refined.pdf` — publication vector export with Type-42 fonts.
- `fig5_semantics_refined.png` — 600 dpi review/preview image.
- `plot_fig5_semantics_refined.py` — complete Python/matplotlib source.
- `data_manifest.md` — traceable source files, hashes, transformations, and recomputed audit values.

## Original data used

1. `补充材料/小论文/9_probability_wear_consistency_analysis/Data_5_4_A6_probability_wear_trajectory.csv`
   - Full C6 lifecycle (304 observations).
   - Supplies `run_id`, `VB_true`, `q_true`, `q_pred`, true/predicted stage, and Early/Middle/Late probabilities.
2. `补充材料/小论文/10_第五章顶刊风格可视化/figures_representation_space/repr_hidden_hct.csv`
   - Only rows with `split=test_C6` and `condition=C6` are used (304 observations).
   - Supplies saved `h_00`–`h_63` hidden features and labels needed for the unchanged deterministic PCA display.

## Original scripts and figures consulted

- `figures/fig5_semantics/plot_fig5.py`
- `nature_figures/scripts/fig5_semantics.py`
- `figures/fig5_semantics/fig5_semantics.{svg,pdf,png}`
- `nature_figures/fig5_semantics/fig5_semantics.{svg,pdf,png}`

The attached old-figure preview was used only for visual audit, never as a data source.

## Visual refinements

- Rebuilt the page as a compact two-row composition: `(a)–(c)` above and wider `(d)–(e)` below; panel `(b)` receives slightly more width as the geometric focal panel.
- Moved every panel identifier and title into a dedicated, centered caption band directly below its panel. No panel title remains above a plot.
- Unified stage semantics throughout: Early = deep blue, Middle = muted teal, Late = warm amber.
- Standardized typography, axis weights, tick sizes, colorbar geometry, whitespace, and restrained reference/grid lines for full two-column journal width.
- Refined the simplex boundary/grid, lifecycle gradient, start/end markers, density statistics box, PCA marker hierarchy, and violin/box/raw-point layering.
- Panel `(e)` displays every raw observation with deterministic jitter; no observations are removed for appearance.
- SVG text remains editable and the PNG is exported at 600 dpi.

## Scientific content deliberately unchanged

- The same 304 C6 lifecycle observations are used.
- The probability curves, q values, VB values, stage labels, and predicted-stage grouping are unmodified.
- `R²`, Spearman `ρ`, and MAE are recomputed from all `q_true`/`q_pred` pairs using the existing definitions.
- The simplex uses the same three probabilities and standard barycentric mapping.
- PCA uses the same saved 64-dimensional test-C6 hidden representations, feature-wise standardization, and deterministic NumPy SVD; there is no retraining, UMAP/t-SNE optimization, or label fitting.
- No smoothing, synthetic data, cherry-picking, or conclusion-changing transformation is introduced.

## Reproduce

From the project root:

```powershell
C:\Users\banghai\miniconda3\python.exe figures\fig5_semantics_refined\plot_fig5_semantics_refined.py
```

The script validates required columns, probability sums, hidden-feature count, and source row alignment before exporting all deliverables.
