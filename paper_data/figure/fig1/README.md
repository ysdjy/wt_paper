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

## v3: dense landscape reconstruction (style_v2 discarded as the visual reference)

`plot_fig1_v3.py` produces `outputs/fig1_v3.{png,pdf,svg}` using the new
`_shared/style_v3.py` module. **Statistics unchanged again** — v3 reuses v1's `load()`,
`build_heatmap_table()`, `validate_headline()`, `load_predictions()` verbatim.

This round explicitly demoted `reference/` (the `nature_figures`/`figures/*_refined` mockups) and
promoted `视觉参考效果图/` (the AI-generated dashboard mockup previously set aside per the user's
v2-round decision) as the primary **layout-only** style reference — proportions and panel
arrangement, never its numbers/method-roster (which are fictional there).

**Layout, ground-up rebuilt:**
- Canvas: landscape 15.5×10.0in (was v2's portrait 13.8×15.5in).
- Two-row dashboard: top row = (a) 9-method×metric heatmap (58% width) + (b) 2×2 representative
  confusion matrices (42% width); bottom row = (c) one composite middle-stage/transition/
  consistency diagnostics panel split into 3 internal blocks (M-Pre/M-Rec+M→E/M→L | Rev/Jump |
  Smooth), all for the same 4 representative methods.
- v2's Pareto scatter and bootstrap-CI-strip panels are **dropped from this composite** per the
  task brief's explicit instruction not to let them consume a full row; not deleted from the
  codebase (still available via v1/v2 for a future supplementary figure).
- No figure-level title anywhere — not even v2's bottom-centered "主比较" caption. The Chinese
  figure name now lives only in the folder name / README / output-filename semantics.
- Every panel caption reads "(a)/(b)/(c) description" and sits **below** its panel via
  `style_v3.panel_container()`, which nests the plot area and caption strip in the SAME GridSpec
  cell via `subgridspec()` — geometrically exact by construction, not a `fig.text()` position
  guess (v2's mechanism). No upper-left panel-letter is used anywhere in v3.

**Bugs found and fixed while building this (all now documented as lessons for fig2-5):**
1. Mixing the legacy `GridSpecFromSubplotSpec(rows, cols, subplot_spec=X, ...)` constructor with
   the modern `X.subgridspec(rows, cols, ...)` method across nesting levels caused group captions
   (panel b's 2×2 confusion-matrix group, panel c's 3-block group) to render at the wrong height —
   floating mid-panel instead of below the whole group. Fixed by using `.subgridspec()`
   consistently at every nesting level, everywhere.
2. Matplotlib tick labels and axis labels render *outside* their Axes' nominal GridSpec box and
   are not clipped to it — so increasing a caption strip's `caption_height` (the row-height
   *ratio*) does **not** create clearance from overflowing tick labels; only `hspace` (an actual
   gap between GridSpec rows) does. Both `panel_container()` and `sub_caption()` needed generous
   `hspace`, not larger `caption_height`, to stop long/rotated tick labels from bleeding into the
   caption strip below them.
3. `plt.colorbar(im, ax=ax, ...)`'s automatic space-stealing from `ax` does not respect a caption
   strip reserved by `panel_container()` in a nested GridSpec — panel (a)'s colorbar now gets its
   own explicit GridSpec sub-row (`content_spec.subgridspec(2, 1, height_ratios=[0.86, 0.14])`)
   instead, drawn via `plt.colorbar(im, cax=cbar_ax, ...)`.
4. Panel (b)'s per-matrix `"Predicted"` x-axis label (row 2 only) collided with that row's
   sub-caption (method name) below it for the same reason as (2). Fixed by dropping the
   redundant per-matrix axis labels entirely and stating the row/column convention once in the
   panel's own group caption instead ("rows=true, columns=predicted").

## v4: publication-grade true-physical-size refinement

`plot_fig1_v4.py` produces `outputs/fig1_v4.{pdf,svg}`, `fig1_v4_600dpi.png`, and
`fig1_v4_paper_preview.png`, using new module `_shared/style_v4.py`. **Statistics unchanged a
third time** — v4 imports v1's `load()`/`build_heatmap_table()`/`validate_headline()`/
`load_predictions()` verbatim. Full rationale: `paper_data/figure/V4_DESIGN_AUDIT.md`. Detailed
scoring: `VISUAL_QA_V4.md` (status: **DONE**, scientific faithfulness 10/10, every text element
≥6.5pt).

**The structural change this round**: the figure is authored at its actual print size from the
start — 178×120mm (7.008×4.724in) — not a big screen canvas shrunk down later. This surfaced real
layout bugs that v3's larger 15.5×10in canvas never hit, because the same *relative* GridSpec
`hspace` fractions produce much smaller *absolute* gaps on a physically smaller canvas:
1. Panel (a)'s and (b)'s single-line captions, which fit fine at v3's scale, overflowed
   horizontally into each other at 178mm width (long caption text simply doesn't fit a ~60mm-wide
   column at 8.4pt). Fixed by wrapping both to 2 lines and shortening.
2. The confusion-matrix method-name sub-captions, first tried via `style_v3`'s `sub_caption()`
   with a larger `hspace` correction, over-corrected: the extra-large relative gap ate so much of
   each matrix's own tiny cell that the matrix content itself became compressed and started
   overlapping internally. Fixed by abandoning the nested-GridSpec sub-caption for this specific
   case and using `ax.set_title(method, y=-0.34)` instead — appropriate here because these are
   short, single-line labels permanently tied to one specific axes (title position is relative to
   that axes' own transform, so it's robust without needing a separately-computed cell).

**Typography**: switched to Times New Roman + STIX mathtext — confirmed (not just adopted) as the
paper's own established convention by reading `代码/1.3.1可视化.py`, `代码/7.3主实验.py`, and
several other original plotting scripts, all of which set exactly this `rcParams` combination.
Every text element, including the smallest (colorbar ticks, confusion-matrix cell text, CI-inset
labels), sits at ≥6.5pt at final print size — found to be as low as 5.2–5.9pt on the first pass and
explicitly raised after review.

**Color system**: switched to the round-4 brief's exact new hex palette (`STAGE_COLORS`,
`METHOD_COLORS`, `BENEFIT_CMAP`, `DIVERGING_CMAP` in `style_v4.py`) — a higher-contrast, more
print-confident palette than v2/v3's more muted navy/teal/gold, while keeping the same underlying
design language (sequential benefit scale, diverging delta scale, consistent stage/method accents).
Confusion matrices now use true sequential `Blues` — visually distinct from the landscape heatmap's
`BENEFIT_CMAP`, per the brief's explicit instruction not to reuse one palette for both roles.

**Content restored, not just restyled**: v3 dropped the Pareto/bootstrap-CI evidence entirely from
the main composite. `DCPSR_Chapter4_CN_Detailed.docx` §4.2 does call for this evidence, so v4 adds
it back as a compact bootstrap-95%-CI inset (Acc, 5 representative methods) in reclaimed corner
whitespace inside panel (c), rather than re-introducing a full separate panel that would unbalance
the layout — exactly the brief's own suggested resolution for this tension.

**Panel (c) redesigned** as one connected diagnostic landscape for 5 representative methods (RF,
TCN-GRU, MTF-AViTK, Multi-task TCN-GRU, DC-PSR) instead of v3's 3 visually separate blocks: M-Pre/
M-Rec as solid bars, M→E/M→L as hatched bars in the same 0–1 axis (all four are genuinely 0–1-scale
metrics, so no third axis is needed), Smooth as an explicitly-labeled "Smooth ↓" teal line on a
twin axis, Rev/Jump folded into the x-tick labels themselves as real integer counts (avoids wasting
a whole sub-panel on values that are mostly zero, while keeping every number traceable).

**Deliberately not copied from `视觉参考效果图/fig1`**: its bright saturated icon/badge treatment,
top banner, and highlighted conclusion callout box (all conflict with this round's own hard rules);
any of its numbers (fictional/illustrative there).

## Open issues (v3)

- At 6.0-6.9pt base font sizes, the dense 9×12 heatmap and 2×2 confusion matrices are sized for a
  full-page thesis figure, not a journal double-column width — if this figure is ever scaled down
  to a ~9cm journal column, text will be too small to read. Not addressed this round (this is a
  doctoral thesis chapter, where full-page landscape figures are normal); flag before journal
  submission if applicable.
- Pareto/bootstrap-CI content from v2 is intentionally absent from v3's main composite per the
  task brief; if reviewers want it back, it exists in `plot_fig2.py`'s panel and could become a
  small supplementary figure rather than being force-fit back into Fig.1.

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
