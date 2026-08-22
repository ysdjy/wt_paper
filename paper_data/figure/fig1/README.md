# Fig.1 — PHM2010 D1 core-task overall performance (paper Fig. 4-2)

## Figure purpose

On the PHM2010 core task D1 (C1+C4→C6, n=304), answers: how do all 9 formal methods compare
across classification and consistency metrics simultaneously; where does DC-PSR sit on the
accuracy–consistency trade-off relative to its direct backbone (Multi-task TCN-GRU) and other
strong baselines; what do representative methods' confusion patterns look like; and how do
representative methods compare on middle-stage recognition and trajectory-consistency
diagnostics. Core narrative (confirmed by validation, not asserted): DC-PSR is not the #1
classifier — Multi-task TCN-GRU edges it out by 0.3–0.4pp on Acc/Macro-F1/M-F1 — but DC-PSR has
the single lowest Smooth (0.01876) of all 9 methods, and Rev=Jump=M→L=0.

## Input files

- `paper_data/07_figure_ready/fig1/D1_main_metrics.csv` — 9-method authoritative point estimates
  + moving-block bootstrap 95% CI (core source for panels a/c).
- `paper_data/07_figure_ready/fig1/accuracy_consistency_points.csv` — Acc/Smooth pairs, panel (b).
- `paper_data/07_figure_ready/fig1/B11_B12_controlled_comparison.csv` — paired Multi-task
  TCN-GRU/DC-PSR CI, used preferentially in panel (c) when available.
- `paper_data/07_figure_ready/fig2/taskwise_absolute.csv` filtered to `Task == "D1"` — supplies
  `E_F1`, `L_F1`, `M_Precision`, which `D1_main_metrics.csv` does not carry (needed to complete the
  panel (a) heatmap). Cross-checked: its `M_F1`/`M_Recall` columns are byte-identical to
  `D1_main_metrics.csv`'s `M_F1`/`M_Rec` for all 9 methods, confirming they are the same
  underlying evaluation, not a divergent recomputation.
- `paper_data/01_PHM2010/01_main_D1/predictions_common_universe/D1_{rf,mtf_avitk,multitask_tcn_gru,dc_psr}_304runs.csv`
  — sample-level `true_stage`/`pred_stage` for the 4 representative methods (panel d). Confusion
  matrices are computed directly from these labels, never hand-entered.

See `inputs_manifest.csv` for row/column counts and SHA-256 of each file as read.

### Representative-method choice (panels d/e)

RF (classical ML baseline), MTF-AViTK (strongest published-literature baseline on D1 by Acc),
Multi-task TCN-GRU (DC-PSR's direct structural backbone/predecessor), DC-PSR (proposed). This
replaces the legacy B1/B5/B8/B12 labeling scheme entirely.

## Derived data

- `derived/D1_heatmap_complete.csv` — the 9-method × 12-metric table actually plotted in panel
  (a), produced by merging `D1_main_metrics.csv` with the D1 rows of `taskwise_absolute.csv`.

## Plot script

`plot_fig1.py` — run with:

```
python paper_data/figure/fig1/plot_fig1.py
```

Panels:
- (a) 9-method × 12-metric performance landscape. Color = within-column min-max normalized
  "benefit" (direction-corrected so lower-is-better metrics are flipped before normalizing, used
  for cell color only); every cell shows the true raw value. Column headers carry `↑`/`↓` to mark
  metric direction explicitly.
- (b) Accuracy (x, higher better) vs Smooth (y, inverted axis so "up-right" reads as better) —
  scatter/Pareto view, DC-PSR and Multi-task TCN-GRU emphasized.
- (c) Bootstrap 95% CI strips for Acc/Macro-F1/M-F1, representative methods only (avoids
  over-dense CI clutter).
- (d) Row-normalized confusion matrices for the 4 representative methods, fixed class order
  [early, middle, late], each cell showing proportion and `(count)`.
- (e) Middle-stage & trajectory-consistency diagnostics (M-Pre, M-Rec, M→E, M→L, Smooth) for the
  4 representative methods, grouped bars, axis labels carry direction arrows.

## Outputs

- `outputs/fig1_main.png` / `.pdf` / `.svg`

## Validation (see `logs/validation.txt`)

- Merge of `D1_main_metrics.csv` with D1 rows of `taskwise_absolute.csv` yields exactly 9 rows
  with no missing classwise fields.
- Headline numbers asserted via `np.isclose` (atol=2e-4) against the task's stated expected
  values: Multi-task TCN-GRU Acc/MacroF1/M-F1/M-Rec/Smooth and DC-PSR Acc/MacroF1/M-F1/M-Rec/Smooth
  — all 10 checks pass.
- All 4 representative-method prediction files have exactly 304 rows with valid
  {early,middle,late} labels; all 4 confusion matrices sum to exactly 304.

## v2: reference-style visual reconstruction

`plot_fig1_v2.py` produces `outputs/fig1_v2_reference_style.{png,pdf,svg}`. **Statistics are
byte-identical to v1** — v2 imports `load()`, `build_heatmap_table()`, `validate_headline()`, and
`load_predictions()` directly from `plot_fig1.py` rather than recomputing anything; only the
visualization layer changed. Style reference: `reference/reference_mockup.png` (copied from
`nature_figures/fig1_overall_performance/fig1_overall_performance.png` — see
`reference/SOURCE.md` for exactly what was/wasn't learned from it).

**Layout changes vs. v1:**
- No top figure-level title. A figure-level caption ("主比较" + English subtitle) is centered at
  the bottom of the canvas instead (`_shared/style_v2.py::figure_caption`).
- Each panel's descriptive title moved from *above* the panel to a centered caption *below* it
  (`panel_caption`); only a small bold `(a)`/`(b)`/... letter remains inside the panel's own
  top-left corner (`panel_letter`).
- New panel (c): "controlled comparison" mini-panels (5 small paired axes, one per metric, DC-PSR
  vermillion circle vs. Multi-task TCN-GRU blue diamond connected by a dumbbell line) — directly
  visualizes the DC-PSR-vs-backbone relationship the task brief calls out, replacing v1's plain
  bootstrap-CI-strip panel. Style borrowed from the reference mockup's own panel (c).
- Heatmap and confusion-matrix colormap switched from generic `RdYlGn` to a custom
  navy/teal/gold-derived sequential colormap (`BENEFIT_CMAP` in `style_v2.py`) so every heatmap
  across all 5 figures reads as one coherent palette family instead of a rainbow scale.

**Deliberately not copied from the reference mockup:** its dot-whisker CI panel (a) layout (kept
v1's fuller 9×12 heatmap instead, since the task brief explicitly requires "总体 performance
heatmap", not just a 1-metric CI plot); its specific method count/order (mockup predates the
current frozen 9-method scheme); any number visible in the mockup.

**Bug found and fixed while building this**: calling `fig.subplots_adjust(...)` *after* panels
were already drawn and captioned silently detached every `panel_caption()` from its axis (captions
were positioned for one layout, then the whole figure reflowed under them). Fix: pass
`left`/`right`/`top`/`bottom` directly to the `GridSpec` constructor so the layout is final
*before* any panel is drawn — documented as a comment in `plot_fig1_v2.py` and followed in every
other v2 script.

**Note on a second, later-arriving reference set**: after this v2 build was finished, a folder
`视觉参考效果图/` appeared in every `figX/` directory (AI-generated dashboard-style mockups, bright
saturated palette, top banner title, icon badges, highlighted conclusion boxes). Its top-banner
convention directly conflicts with this round's explicit "no top title" rule, and (in fig2's copy)
its method roster is fictional (8 generic baselines, not the real 9-method scheme) — reinforcing
that it is style inspiration at most, not a literal template. Asked the user directly whether to
rework all 5 figures to match its brighter dashboard aesthetic; they confirmed keeping the current
academic-journal style. No changes made as a result.

## Open issues

- Vertical spacing between the confusion-matrix row and its neighbors is generous (matplotlib's
  default equal-aspect handling of 3×3 `imshow` panels leaves whitespace above/below within that
  GridSpec row); layout is correct and fully legible but a second visual pass could tighten this.
  Not prioritized this round — Fig.1/Fig.2 are the "reviewer-friendly, regular" figures per the
  design doc, with visual-design effort intentionally concentrated on Fig.4/Fig.5.
