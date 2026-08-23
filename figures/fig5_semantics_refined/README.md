# Figure 5 — semantic consistency / probability trajectory (refined)

## Purpose

This figure shows that DC-PSR produces a continuous and ordered degradation representation rather than isolated stage labels. The five panels connect lifecycle probabilities, continuous degradation position, the saved hidden-space manifold, and true physical flank wear.

## Panel story

- **(a) Full lifecycle probability trajectory** — Early/Middle/Late probabilities and continuous `q_pred` across the complete C6 lifecycle. Pale background zones are calculated from contiguous `true_stage` spans.
- **(b) Ordered trajectory in probability simplex** — the same three probabilities mapped to an equilateral simplex and ordered by relative life. Sparse arrows, start/end markers, and the continuous colorbar expose direction without changing the trajectory.
- **(c) Continuous degradation-position agreement** — all `q_true`/`q_pred` pairs as log-density hexbins, with `y=x`, the unchanged audit statistics, and a display-only 12-bin median trend.
- **(d) Shared latent degradation manifold** — deterministic PCA of the saved 64-dimensional test-C6 hidden representations. Marker shape denotes stage, color denotes `q_true`, and a restrained guide path connects median PCA centers from 18 `q_true` bins.
- **(e) Physical wear semantics** — a half-violin raincloud, boxplot, and every raw `VB_true` observation grouped by predicted stage. No significance marks are added.

## Authoritative data

The project-level audit `nature_figures/FIGURE_DATA_AUDIT.md` explicitly designates these sources:

1. `补充材料/小论文/9_probability_wear_consistency_analysis/Data_5_4_A6_probability_wear_trajectory.csv`
   - Panels `(a)`, `(b)`, `(c)`, and `(e)`.
   - Complete C6 lifecycle, 304 runs; no row selection.
2. `补充材料/小论文/10_第五章顶刊风格可视化/figures_representation_space/repr_hidden_hct.csv`
   - Panel `(d)`.
   - Only `split=test_C6` and `condition=C6`, giving 304 saved real hidden representations.

The script validates required columns, probability sums, lifecycle stage order, 64 hidden features, and row alignment before drawing. Source hashes, generated time, panel-level transformations, and integrity statements are recorded in `data_manifest.json`.

## Files

- `fig5_semantics_refined.svg` — primary editable vector output; SVG text remains editable.
- `fig5_semantics_refined.pdf` — publication vector output with embedded Type-42 fonts.
- `fig5_semantics_refined.png` — 600 dpi review preview.
- `make_fig5_semantics_refined.py` — canonical reproducible Python source.
- `data_manifest.json` — source provenance, authority status, hashes, transformations, metrics, and generation metadata.
- `plot_fig5_semantics_refined.py` — backward-compatible entry point that calls the canonical script.
- `data_manifest.md` — human-readable compatibility pointer to the JSON manifest.

## Reproduce

From the project root:

```powershell
C:\Users\banghai\miniconda3\python.exe figures\fig5_semantics_refined\make_fig5_semantics_refined.py
```

No model training, inference rerun, or alternative embedding is performed.

## Where to modify appearance

Open `make_fig5_semantics_refined.py` and edit:

- **Titles:** `PANEL_TITLES`.
- **Stage colors:** `STAGE_COLORS`; pale zone colors are in `STAGE_ZONE_COLORS`.
- **Continuous colormaps:** `LIFE_CMAP` and `DENSITY_CMAP`.
- **Font and line sizes:** `apply_style()`.
- **Whole-figure size:** `figsize=(7.20, 6.15)` inside `build_figure()`.
- **Panel width/height allocation:** the `outer`, `top`, and `bottom` GridSpec definitions in `build_figure()`.
- **Caption typography and vertical position:** `add_caption()`.
- **PNG resolution:** `dpi=600` inside `export_figure()`.
- **Simplex arrows:** the `add_path_arrows(...)` call in panel `(b)`.
- **PCA center-path granularity:** `manifold_centers(..., bins=18)` in panel `(d)`.

## Scientific content held fixed

- The same audited 304 C6 observations and 304 saved hidden representations are used.
- Probabilities, `q_true`, `q_pred`, stage labels, and `VB_true` are not altered.
- `R²`, Spearman `ρ`, and MAE retain the existing definitions and are recomputed from every pair.
- PCA remains feature-standardized deterministic NumPy SVD; no UMAP/t-SNE, label fitting, retraining, or simulated point is used.
- Background zones, direction arrows, binned median guides, and deterministic jitter are display aids derived directly from existing observations.
