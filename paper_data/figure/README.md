# DC-PSR Chapter 4 result figures — overview

Five figures, generated directly from frozen `paper_data`, corresponding to paper Fig. 4-2
through Fig. 4-6 (Chapter 4's "1 design figure + 5 result figures" plan; the design figure,
Fig. 4-1, is a non-data schematic and is out of scope here).

```
figure/fig1  → Paper Fig. 4-2  PHM2010 D1 core-task overall performance
figure/fig2  → Paper Fig. 4-3  Cross-condition (D1/D2/D3) + cross-dataset generalization
figure/fig3  → Paper Fig. 4-4  A1–A6 ablation mechanism band
figure/fig4  → Paper Fig. 4-5  Ordered degradation semantics (lifecycle/simplex/q/VB)
figure/fig5  → Paper Fig. 4-6  Shared latent representation + joint probability/position evolution
```

**Important**: the on-disk `paper_data/07_figure_ready/fig1..fig5/` folder numbering does **not**
match this final figure numbering (e.g., final Fig.2 reads from on-disk `fig2/` *and* `fig3/`;
final Fig.3 reads from on-disk `fig4/`; final Fig.4/Fig.5 both read from on-disk `fig5/`). See
`FIGURE_PROGRESS.md` §1 for the precise mapping, and each `figX/README.md` for exact file paths.

## Data-freeze status (read before treating any number as final)

`paper_data/FINAL_FREEZE_CLEANUP_HANDOFF.md` (dated the same day as this work) states the
paper_data build/validate cleanup is in progress, not freshly re-validated. Every headline number
used across all 5 figures was independently recomputed from the on-disk CSVs and cross-checked
against `DCPSR_Chapter4_CN_Detailed.docx`'s Appendix A — all matched exactly. Decision and full
reasoning: see `FIGURE_PROGRESS.md` §0.

## How to reproduce everything

Each figure is fully self-contained and re-runnable independently:

```powershell
python paper_data/figure/fig3/plot_fig3.py   # A1-A6 ablation (run first; most self-contained)
python paper_data/figure/fig1/plot_fig1.py   # D1 core comparison
python paper_data/figure/fig2/plot_fig2.py   # cross-condition / cross-dataset
python paper_data/figure/fig4/plot_fig4.py   # degradation semantics
python paper_data/figure/fig5/plot_fig5.py   # latent representation
```

Each script: reads only frozen `paper_data` CSVs (via `_shared/data_utils.py::read_csv`, always
`encoding="utf-8"`), recomputes every plotted statistic from source rows rather than reading
pre-baked numbers where an independent recomputation is possible, runs a validation section that
`assert`s/`np.isclose`s against the task's stated headline numbers, writes
`figX/logs/validation.txt`, and saves `figX/outputs/figX_main.{png,pdf,svg}` at 300 DPI.

## Shared infrastructure (`_shared/`)

- `style.py` — matplotlib rcParams, fixed color constants (Early/Middle/Late stage colors,
  9-method colors, A1–A6 ablation colors), `save_all()`, and the metric-direction dictionary.
- `data_utils.py` — CSV loading, confusion-matrix computation, manual precision/recall/F1 (no
  sklearn dependency — not installed in this environment), the coefficient-of-determination R²
  formula (verified to match the design doc's q-agreement number, which squared-Pearson-r does
  not), numpy-SVD-based 2-component PCA, and ternary-simplex coordinate transform.

Stage colors (Early=blue, Middle=gold, Late=orange-red) and the DC-PSR=red / Multi-task
TCN-GRU=blue method colors are held constant across all 5 figures.

## Methods, datasets, and metric-direction conventions used throughout

See `FIGURE_PROGRESS.md` §4–§5 for the full, verified reference. Summary:
- 9 formal methods only (RF, TCN-GRU, Multi-task TCN-GRU, DC-PSR, HTT-Net (adapted),
  Multi-source Attention, MTF-AViTK, Dynamic GIN + TGP, DP2Net-adapted) — the legacy B1–B12
  labeling is never used as a primary axis label (only as an internal shorthand inside
  `04_cross_dataset`-derived tables, always translated to full names in the figures).
- Third dataset is `MILLING_CROSS_MACHINE` / MTW-CM (Mendeley Data), never "MIMII".
- Higher-is-better: Acc, Macro-F1, E/M/L-F1, M-Precision, M-Recall. Lower-is-better: M→E, M→L,
  Rev, Jump, Smooth. Every heatmap that colors by a direction-unified "benefit" score still prints
  the true raw value in the cell, and never relabels a lower-is-better metric as "higher is
  better" — this was one of the task's explicit hard constraints and is checked in every panel
  that uses such a heatmap (fig1 panels a/e, fig2 panel c, fig3 panel c).
- Flank wear VB is in **micrometers (μm)**, not millimeters — resolved from
  `DCPSR_Chapter4_CN_Detailed.docx` since `00_metadata/Q_DEFINITIONS.md` doesn't state a unit.

## Status

All 5 figures: **Done**, in two rounds:

- **v1** (`plot_figX.py` → `figX_main.{png,pdf,svg}`): first-pass Python/matplotlib,
  correctness-first, top titles + above-panel captions, RdYlGn/viridis stock colormaps.
- **v2** (`plot_figX_v2.py` → `figX_v2_reference_style.{png,pdf,svg}`): same data/statistics
  (v2 scripts import v1's data/validation functions directly), visualization layer rebuilt —
  no top title, figure name as a bottom-centered caption, panel captions moved below each panel,
  and a coherent navy/teal/gold palette shared across all 5 figures via `_shared/style_v2.py`.
  See `FIGURE_PROGRESS.md` §8 for the full v2 build log, including a real reference-material
  conflict that was surfaced to and resolved by the user rather than guessed at.

Both rounds' outputs are kept side by side in each `figX/outputs/` — v1 is not superseded/deleted,
since v2 depends on it (imports its functions) and both remain independently reproducible.

## Remaining human decisions

- Whether to complete the separate, unfinished `build_paper_data.py`/`validate_paper_data.py`
  cleanup described in `FINAL_FREEZE_CLEANUP_HANDOFF.md` before this data is treated as formally
  re-frozen — out of scope for this figure-generation task, flagged for awareness.
- Fig.4/Fig.5 panel-content overlap (both show an ordered Early→Middle→Late structure, in
  different spaces) is flagged in `fig5/README.md`'s Open Issues; manuscript caption language
  should make the space distinction explicit rather than requiring a figure redesign.
- A second, AI-generated "dashboard" style reference set arrived mid-task in every
  `figX/视觉参考效果图/` folder; the user was asked directly and confirmed keeping the current
  muted academic-journal style over reworking to that brighter aesthetic (see `FIGURE_PROGRESS.md`
  §8). Revisit only if that preference changes.
- fig5 v2's 3D panels (d)/(e) have a cosmetic `mpl_toolkits.mplot3d` vertical-spacing quirk noted
  in `fig5/README.md`'s Open Issues — not a data or layout-bug issue, left for a future polish pass
  if desired.
