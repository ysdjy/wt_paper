# DC-PSR Chapter 4 result figures — overview

Five figures, generated directly from frozen `paper_data`, corresponding to paper Fig. 4-2
through Fig. 4-6 (Chapter 4's "1 design figure + 5 result figures" plan; the design figure,
Fig. 4-1, is a non-data schematic and is out of scope here).

```
figure/fig1  → Paper Fig. 4-2  PHM2010 D1 core-task overall performance          (主比较)
figure/fig2  → Paper Fig. 4-3  Cross-condition (D1/D2/D3) + cross-dataset generalization (鲁棒性)
figure/fig3  → Paper Fig. 4-4  A1–A6 ablation mechanism band                      (消融实验)
figure/fig4  → Paper Fig. 4-5  Ordered degradation semantics (lifecycle/simplex/q/VB) (退化语义)
figure/fig5  → Paper Fig. 4-6  Shared latent representation + joint probability/position evolution (表示几何)
```

The Chinese names above are the figure's identity in the folder/README/filename sense only — none
of them render as an on-canvas title anywhere in the current (v3/v4) figures.

**Important**: the on-disk `paper_data/07_figure_ready/fig1..fig5/` folder numbering does **not**
match this final figure numbering (e.g., final Fig.2 reads from on-disk `fig2/` *and* `fig3/`;
final Fig.3 reads from on-disk `fig4/`; final Fig.4/Fig.5 both read from on-disk `fig5/`). See
`FIGURE_PROGRESS.md` §1 for the precise mapping, and each `figX/README.md` for exact file paths.

## Data-freeze status

`paper_data/FINAL_FREEZE_CLEANUP_HANDOFF.md` reads as if the build/validate cleanup were still in
progress, but that document is itself stale: `git log` shows the cleanup was actually finished and
committed (`a6cf5d8`, 2026-08-21T17:17:05Z) **before** this figure-generation task began, and
`git diff HEAD -- paper_data` shows zero drift on every tracked file. Every headline number used
across all 5 figures was also independently recomputed from the on-disk CSVs and cross-checked
against `DCPSR_Chapter4_CN_Detailed.docx`'s Appendix A — all matched exactly. Full detail:
`FIGURE_PROGRESS.md` §0.

## How to reproduce everything

Each figure is fully self-contained and re-runnable independently, across four rounds (v1/v2/v3/v4
all still work — v2/v3/v4 import v1's data/validation functions, they don't replace them):

```powershell
# v4 -- current, publication-grade, true-physical-size (178mm width) layout (recommended for use)
python paper_data/figure/_shared/prepare_shared_pca_v4.py   # run once, before fig4/fig5 v4
python paper_data/figure/fig1/plot_fig1_v4.py
python paper_data/figure/fig2/plot_fig2_v4.py
python paper_data/figure/fig3/plot_fig3_v4.py
python paper_data/figure/fig4/plot_fig4_v4.py
python paper_data/figure/fig5/prepare_fig5_v4.py             # exports derived/*.csv
& "C:\Program Files\Polyspace\R2021a\bin\matlab.exe" -nosplash -nodesktop -batch "cd('paper_data/figure/fig5'); plot_fig5_v4"

# v3 -- dense-landscape, screen-canvas scale, below-panel-caption layout, still fully working
python paper_data/figure/fig1/plot_fig1_v3.py   # ... fig2/3/4 analogous
python paper_data/figure/fig5/prepare_fig5_v3.py
& "C:\Program Files\Polyspace\R2021a\bin\matlab.exe" -nosplash -nodesktop -batch "cd('paper_data/figure/fig5'); plot_fig5_v3"

# v2 -- reference-style, figure-level bottom caption, still fully working
python paper_data/figure/fig1/plot_fig1_v2.py   # ... fig2/3/4/5 analogous

# v1 -- first-pass, correctness-first, still fully working
python paper_data/figure/fig1/plot_fig1.py      # ... fig2/3/4/5 analogous
```

Each Python script: reads only frozen `paper_data` CSVs (via `_shared/data_utils.py::read_csv`,
always `encoding="utf-8"`), recomputes every plotted statistic from source rows rather than reading
pre-baked numbers where an independent recomputation is possible, runs a validation section that
`assert`s/`np.isclose`s against the task's stated headline numbers, and writes a `logs/validation*.txt`.
fig5's MATLAB stage reads the CSVs its `prepare_fig5_v{3,4}.py` companion exports and writes its
own `logs/validation_v{3,4}_matlab.txt`.

## Shared infrastructure (`_shared/`)

Four parallel style modules, one per round — kept separate so earlier rounds stay byte-for-byte
reproducible rather than being edited out from under themselves:

- `style.py` (v1) / `style_v2.py` (v2) — matplotlib rcParams, color constants (Early/Middle/Late
  stage colors, 9-method colors, A1–A6 ablation colors), `save_all()`, metric-direction dictionary.
  v2 adds the navy/teal/gold `BENEFIT_CMAP`/`DIVERGING_CMAP`/`DEGRADATION_CMAP` and the
  bbox-guessing `panel_caption()`/`figure_caption()` helpers (superseded by v3, kept for v2's own
  reproducibility).
- `style_v3.py` — re-exports v2's color constants unchanged; replaces the caption machinery with
  `panel_container()` (plot area + caption strip nested in the same `GridSpec` cell via
  `subgridspec`, geometrically exact) and `sub_caption()` (same mechanism for sub-panels inside an
  already-captioned group). No figure-level caption helper exists in v3 — none is used.
- `style_v4.py` — re-exports v3's `panel_container()`/`sub_caption()` caption mechanism unchanged
  (it was never the bug source — only how its `hspace`/`caption_height` were tuned needed fixing at
  the smaller physical scale). New: Times New Roman + STIX typography (confirmed as the *original
  paper's own* established convention by reading `代码/1.3.1可视化.py`/`代码/7.3主实验.py`, not a
  new stylistic choice), a higher-contrast hex color palette, `master_figsize_in(fig_key)` for
  true-physical-size figure creation (mm→inch, no post-hoc shrink), and `save_all()` emitting
  `.pdf`/`.svg`/`_600dpi.png`/`_paper_preview.png` (the last is the actual QA artifact — always
  review that one, not the 600dpi PNG at screen zoom).
- `prepare_shared_pca_v4.py` → `derived/shared_pca_scores_v4.csv` — new in v4: ONE PCA fit (numpy
  SVD) on the real 304×64 `hidden_representation.csv`, with a deterministic PC1 sign convention
  (`corr(PC1, q_true) > 0`, verified 0.933). fig4(d) and fig5(a)/(b)/(c) both read this file
  directly instead of each fitting their own PCA — closes a real risk that two independent fits on
  the same data could come out mirrored relative to each other (PCA sign/rotation is mathematically
  arbitrary), which would make the same shared representation look inconsistent between the two
  hero figures for a reader.
- `data_utils.py` — CSV loading, confusion-matrix computation, manual precision/recall/F1 (no
  sklearn dependency — not installed in this environment), the coefficient-of-determination R²
  formula (verified to match the design doc's q-agreement number, which squared-Pearson-r does
  not), numpy-SVD-based 2-component PCA, and ternary-simplex coordinate transform.

Stage colors and the DC-PSR / Multi-task TCN-GRU method-accent colors are held constant within
each round (v4 switched to a new, higher-contrast hex palette relative to v2/v3's more muted
navy/teal/gold — see `style_v4.py` for the exact values) and are internally consistent across all
5 figures in that round.

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
  better." Where a chart axis needs "up = better" (e.g. fig3's Smooth panel), it is always shown
  as an explicitly labeled **derived benefit/improvement (%)**, never raw Smooth silently flipped.
- Flank wear VB is in **micrometers (μm)**, not millimeters, on a **linear** axis — resolved from
  `DCPSR_Chapter4_CN_Detailed.docx` since `00_metadata/Q_DEFINITIONS.md` doesn't state a unit.
- fig4(b)'s probability-simplex vertex convention changed in v4 to match the *original paper's own*
  convention found in `代码/7.3主实验.py::plot_probability_simplex` — Early=bottom-left,
  Middle=bottom-right, Late=top (v1-v3 used a different arrangement). Same real trajectory, only
  the corner labeling changed, for consistency with the rest of the thesis.

## Status

All 5 figures: **Done**, in four rounds — v1/v2/v3 unchanged from before, v4 newly added:

- **v1** (`plot_figX.py` → `figX_main.{png,pdf,svg}`): first-pass Python/matplotlib,
  correctness-first, top titles + above-panel captions, RdYlGn/viridis stock colormaps.
- **v2** (`plot_figX_v2.py` → `figX_v2_reference_style.{png,pdf,svg}`): same data/statistics,
  visualization layer rebuilt — no top title, figure name as a bottom-centered caption, panel
  captions moved below each panel, coherent navy/teal/gold palette (`_shared/style_v2.py`).
- **v3** (`plot_figX_v3.py` → `figX_v3.{png,pdf,svg}`; fig5 = `prepare_fig5_v3.py` + MATLAB
  `plot_fig5_v3.m`): no figure-level caption in either direction, every panel caption geometrically
  locked below its panel via `_shared/style_v3.py::panel_container()`, strict landscape
  dense-dashboard canvases sized for on-screen work, `视觉参考效果图/` promoted to the primary
  layout-only reference.
- **v4** (`plot_figX_v4.py` → `figX_v4.{pdf,svg}` + `figX_v4_600dpi.png` + `figX_v4_paper_preview.png`;
  fig5 = `prepare_fig5_v4.py` + MATLAB `plot_fig5_v4.m`): same data/statistics a third time,
  **authored at true physical print size** (178mm width; 120-132mm height per figure) instead of a
  large screen canvas, Times New Roman + STIX typography (the original paper's own convention),
  every text element ≥6.5pt, real statistical content restored where v3 had dropped it (fig1's
  bootstrap-CI inset), two genuine structural content fixes (fig3 panel (d) now shows real
  lifecycle probability-variation data instead of near-all-zero Rev/Jump bars; fig4 panel (d) and
  fig5 panels (a)-(c) now share one PCA fit instead of two independent ones). fig5's two 3D panels
  substantially reworked from v3's thin ribbons into broad ridge curtains (panel d) and a
  real-uncertainty-width-encoded confidence ribbon (panel e). Full build log, the pre-code design
  audit, the recurring true-physical-size bug class and its fix pattern, and the fig1-first
  sequential-validation process: `FIGURE_PROGRESS.md` §10, and `paper_data/figure/V4_DESIGN_AUDIT.md`.
  Every figure has a `figX/VISUAL_QA_V4.md` with 7 scored criteria (Scientific faithfulness = 10/10
  required for DONE) and 8 answered review questions.

All four rounds' outputs are kept side by side in each `figX/outputs/` — nothing is
superseded/deleted, since later rounds import earlier rounds' functions and all four remain
independently reproducible.

## Remaining human decisions

- Whether to complete the separate, unfinished `build_paper_data.py`/`validate_paper_data.py`
  cleanup described in `FINAL_FREEZE_CLEANUP_HANDOFF.md` — moot for data correctness (see
  "Data-freeze status" above) but the document itself could use an update to stop reading as
  in-progress.
- Fig.4/Fig.5 panel-content overlap (both show an ordered Early→Middle→Late structure, in
  different spaces, though now via the *same* shared PCA coordinates as of v4) is flagged in
  `fig5/README.md`'s Open Issues; manuscript caption language should make the space distinction
  explicit rather than requiring a figure redesign.
- A second, AI-generated "dashboard" style reference set (`视觉参考效果图/`) arrived mid-task
  during round 2; the user was asked directly and at that time confirmed keeping the muted
  academic-journal style. Round 3 reversed that specifically for *layout* (promoting
  `视觉参考效果图/` to primary layout reference) while keeping a muted color palette; round 4
  (this one) introduced its own new, higher-contrast palette per this round's explicit brief — if
  the user wants the mockups' full brighter/saturated color treatment, that remains a color-only
  follow-up, not a layout rebuild.
- Minor open cosmetics noted in individual `figX/VISUAL_QA_V4.md` "Open issues" sections (fig1:
  none outstanding; fig2: radar-card axis labels from adjacent cards sit close but legible; fig3:
  none outstanding; fig4: none outstanding; fig5: two MATLAB caption/label spots are tight but
  legible, and MATLAB's text sizing was audited at a conservative ≥7pt rather than matplotlib's
  exact ≥6.5pt-per-artist grep-audit since MATLAB doesn't expose the same granular control) — none
  block use, listed for a future polish pass if desired.
