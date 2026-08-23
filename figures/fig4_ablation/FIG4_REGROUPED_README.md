# Fig.4 Regrouped — A1–A6 Ablation Figure

## Figure contract

- Core conclusion: A6 recovers most of the predictive performance lost by the pure ordered filter (A5), while retaining improved probability continuity, demonstrating the accuracy–consistency balance contributed by ordered probability inference.
- Figure archetype: quantitative 2×2 grid.
- Backend: Python / matplotlib only.
- Final size: 7.2 × 5.75 in (approximately 183 × 146 mm), suitable for double-column placement.
- Test protocol: PHM2010 D1, train C1+C4 and test C6; 304 test windows from one frozen formal B11/B12 backbone/checkpoint.
- Statistics: deterministic single-checkpoint ablation summaries; no error bars, confidence intervals, or cross-seed aggregation are implied.

## Data-source and pre-plot checks

The primary plotting table is:

- `figures/fig4_ablation/AUTHORITATIVE_A1_A6.csv`

The retired `FINAL_ablation_outputs.csv` is not loaded by `plot_fig4_regrouped.py` and is not used as plotting evidence.

Checks performed before plotting:

1. The authoritative CSV exists and contains the required primary columns.
2. Available primary fields are: `ID`, `Configuration`, `Acc`, `Macro-F1`, `M-F1`, `M-Rec`, `M→E`, `M→L`, `Rev`, `Jump`, `Smooth`.
3. The row order is exactly `A1, A2, A3, A4, A5, A6`, with no duplicate IDs.
4. All primary metric fields are parsed as numeric values.
5. The plotting script contains no path to the retired result table. The former
   `plot_fig4.py` heatmap entry point now delegates to `plot_fig4_regrouped.py`,
   preventing accidental regeneration from the retired source.
6. The requested panels additionally require `E-F1`, `L-F1`, and middle-stage precision, which are not columns in the authoritative wide table. These three values are completed in memory from the `Recomputed` column of `ABLATION_RECOMPUTED.csv`, the prediction-level audit comparison table; that file is not used as the primary ablation table.
7. The field mapping is `M-Rec` → displayed `M-Rec` / internal `M-Recall`, and audited `M-Precision` → displayed `M-Pre`.
8. The completed fields must pass two exact consistency gates before any figure is created:
   - mean(`E-F1`, `M-F1`, `L-F1`) = authoritative `Macro-F1`;
   - harmonic mean(`M-Precision`, `M-Rec`) = authoritative `M-F1`.
9. The audit-table `Difference` for all 18 completion cells must be no larger than `1×10⁻¹²`.

This design keeps `AUTHORITATIVE_A1_A6.csv` as the sole primary A1–A6 table while using the audit comparison only to expose the three already recomputed state metrics required by the requested panels. No values are copied from an image or entered manually.

## Panel contents

### (a) Overall predictive performance across A1–A6

- Grouped bars: `Acc`, `Macro-F1`, `M-F1` (higher is better).
- Warm line on the right axis: `Smooth` (lower is better).
- A5 and A6 receive restrained background bands and outlines.
- Callouts identify A5 as the strongest smoothing variant and A6 as the variant that restores predictive accuracy.

### (b) State-wise recognition profile

- Lines: `E-F1`, `M-F1`, `L-F1` (higher is better).
- The flat A1–A4 segment is explicitly identified as identical class decisions, while A5/A6 points receive compact value labels.

### (c) Middle-stage and transition consistency

- Bars: `M-Pre`, `M-Rec` (higher is better).
- Lines on the right axis: `M→E`, `M→L` (lower is better).
- The A6 annotation highlights recovery of middle-stage recall after A5.

### (d) Trajectory stability diagnostics

- Bars: `Rev`, `Jump` (lower is better).
- Line on the right axis: `Smooth` (lower is better).
- Because audited `Rev` and `Jump` are exactly zero for every A1–A6 variant, the panel states this directly and renders zero-level bar markers rather than inventing visible nonzero heights.
- The A5→A6 annotation marks the transition from pure ordered output to the final probability blend.

## Direction of interpretation

- Higher is better: `Acc`, `Macro-F1`, `E-F1`, `M-F1`, `L-F1`, `M-Pre`, `M-Rec`.
- Lower is better: `M→E`, `M→L`, `Rev`, `Jump`, `Smooth`.

## Outputs

- `fig4_ablation_regrouped.pdf` — vector PDF with embedded editable TrueType text.
- `fig4_ablation_regrouped.svg` — vector SVG with text retained as text nodes.
- `fig4_ablation_regrouped.png` — 600 dpi raster preview.
- `plot_fig4_regrouped.py` — reproducible Python plotting and validation script.
- `FIG4_REGROUPED_README.md` — data contract, checks, field mapping, and panel guide.

Run from the project root with:

```powershell
python figures/fig4_ablation/plot_fig4_regrouped.py
```
