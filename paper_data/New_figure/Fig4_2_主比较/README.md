# Fig4-2 主比较 (Main Comparison) — DONE (first-pass, visually reviewed)

## 1. Scientific question
On PHM2010 core task D1 (C1+C4→C6, n=304): how does DC-PSR compare against the final 8-baseline
roster (9 methods total) on classification and trajectory consistency simultaneously? Headline
(verified against frozen data, not asserted): Multi-task TCN-GRU is the top classifier
(Acc/Macro-F1/M-F1 = 0.9901/0.9902/0.9882); DC-PSR is close behind (0.9868/0.9871/0.9844, −0.3 to
−0.4pp) but has the lowest Smooth of all 9 methods (0.01876, −20.5% vs. Multi-task TCN-GRU) with
Rev=Jump=M→L=0. **This figure never claims DC-PSR is the top classifier** — panel (a) and (c) show
Multi-task TCN-GRU winning on raw classification honestly.

## 2. Panel list
- (a) Overall classification performance (Acc/Macro-F1/M-F1), 9 methods, hatched grouped bars,
  DC-PSR's column highlighted.
- (b) Accuracy–consistency trade-off scatter (raw Accuracy vs. raw Smooth, Smooth axis explicitly
  labeled "↓ better", never inverted-without-saying-so). DC-PSR and Multi-task TCN-GRU emphasized.
- (c) **DC-PSR vs backbone: paired effect** (redesigned, see §12) — top: paired moving-block-
  bootstrap forest plot of Delta (pp), DC-PSR (B12) vs Multi-task TCN-GRU (B11), for
  Acc/Macro-F1/M-F1/M-Rec (positive always favors DC-PSR); bottom: Smooth reduction, B11→B12
  dumbbell with relative-% point estimate (separate axis/unit from the pp forest above it,
  deliberately not sharing one numeric scale). Replaces the earlier 4-method absolute-CI forest
  plot (RF/MTF-AViTK/Multi-task TCN-GRU/DC-PSR x Acc/Macro-F1/M-F1), which was redundant with
  Table 5 and did not isolate the DC-PSR-vs-its-own-backbone comparison this figure's narrative
  needs.
- (d) Representative confusion matrices (row-normalized + count), same 4 methods, custom
  white→blue→purple→red colormap ported from `代码/8.2图9.py`.
- (e) Middle-stage & consistency triptych (原 Fig.10 framework): (e1) M-Pre/M-Rec/M-F1,
  (e2) M→E/M→L misclassification direction, (e3) Rev/Jump bars + Smooth line, same 4 methods.

## 3. Data source
See `inputs_manifest.csv`. Primary: `paper_data/07_figure_ready/fig1/D1_main_metrics.csv`,
`accuracy_consistency_points.csv`, `B11_B12_controlled_comparison.csv` (loaded but not directly
plotted — CI for the other 7 methods drawn straight from `D1_main_metrics.csv`'s own CI columns),
`paper_data/07_figure_ready/fig2/taskwise_absolute.csv` (D1 rows, E_F1/L_F1/M_Precision
completion), and 4 sample-level prediction files under
`paper_data/01_PHM2010/01_main_D1/predictions_common_universe/`. Panel (c) additionally reads the
Multi-task TCN-GRU and DC-PSR 304-run prediction files directly (`run_id,true_stage,pred_stage,
p_early,p_middle,p_late`) to run its own paired moving-block bootstrap — see §12.

## 4. Original manuscript code reused (visual framework, never hardcoded data)
- `代码/8.2图10.py`: `add_axis_arrows()`, `style_axis()`, `add_highlight_for_last_group()` ported
  near-verbatim into `_shared/style.py` — this is the manuscript's own middle-stage/consistency
  triptych, directly reused for panel (e). Hatched-white-bar convention (facecolor="white",
  colored edge, `hatch="////"/"\\\\\\\\"/"...."`) reused for panels (a)/(e1)/(e2).
- `代码/8.2图9.py`: `CMAP_ORIGINAL_LIKE` diverging colormap (white→cyan→blue→purple→red), ported
  as `style.CONFUSION_CMAP`, used for panel (d).

## 5. Previous `paper_data/figure` code reused for data calculation only
- `figure/fig1/plot_fig1.py`'s merge/validation pattern (D1_main_metrics + taskwise_absolute join,
  headline-number `np.isclose` assertions) — re-implemented in `scripts/load_data.py`, not
  imported directly (kept New_figure self-contained per the "New_figure must not modify/depend
  fragile-ly on paper_data/figure" boundary), but the logic and the exact expected headline values
  are the same, re-verified fresh in this round's own validation log.
- `figure/_shared/data_utils.py`'s `confusion_counts`/`precision_recall_f1_per_class`/`accuracy` —
  copied into `New_figure/_shared/data_utils.py` and used for panel (d)/(e) recomputation.

## 6. New code written
- `_shared/style.py`, `_shared/data_utils.py` (this round's shared infrastructure).
- `scripts/load_data.py` (load/merge/validate → `derived/*.csv` + `logs/validation.txt`).
- `scripts/panels.py` (5 independently-testable panel-drawing functions + `render_previews()`).
- `scripts/assemble.py` (final composite, 178×158mm, 3-row GridSpec).

## 7. Visual interpolation
None. Every value plotted is either a frozen authoritative number or a direct recomputation from
304-row sample-level labels (confusion counts, precision/recall). No surface, no fabricated
density, no interpolation.

## 8. Data validation
`logs/validation.txt` — headline Acc/MacroF1/M_F1/M_Rec/Smooth for Multi-task TCN-GRU and DC-PSR
checked via `np.isclose` (atol=2e-4) against the task's stated expected values (all PASS);
recomputed representative-method Acc/M_Rec cross-validated against `D1_main_metrics.csv` (all
PASS); all 4 confusion matrices confirmed to sum to exactly 304.

## 9a. Refinement round (CIE-submission pass, journal border/block-structure)
Per `../FIGURE_REFINEMENT_AUDIT.md`: added one outer canvas border and two light block borders
("Overall D1 comparison" wrapping a/b/c; "Representative-method diagnostics" wrapping d/e1-e3),
via new `_shared/style.py` helpers (`add_outer_border`, `add_block_border`,
`caption_bottom_fig_frac`). Canvas height adjusted 158mm→160mm (a small *increase*, not a
reduction) — direct measurement found panel (a)'s caption (`y=-0.42`, pushed deep by its rotated
9-method x-tick labels) needs slightly more row-to-row gap than the original layout gave once a
border boundary also has to fit in that same gap; solved with an explicit thin spacer GridSpec row
between row 1 and row 2 rather than uniformly shrinking margins (which caused a real collision on
the first attempt — the block border briefly overlapped panel (a)'s caption and the confusion-
matrix row; found and fixed by opening the PNG, not assumed correct from the code alone). Also
added a fixed-name export (`fig4_2_main_comparison.pdf`/`_600dpi.png`) to
`New_figure/final_pdf/`, alongside (not replacing) the existing versioned `outputs/` files.

## 9. Output path
`outputs/Fig4_2_main_comparison.{pdf,svg}`, `_600dpi.png`, `_preview.png`. Panel-first review PNGs
in `outputs/panel_previews/` (kept for provenance/reviewability, not part of the final deliverable).

## 10. Refinement pass (post-approval)
Structure/composition approved by user; refinement-only changes made afterward, no scientific
content or panel layout changed:
- Panel (c): x-axis tightened from a generic 0.55–1.03 span to the actual representative-method CI
  data range (~89–100.5%, computed from the real min/max CI bounds, not eyeballed), values now
  displayed in percentage points instead of raw 0–1 fractions, and its column narrowed
  (width-ratio 1.0→0.85 relative to (a)/(b)) since it no longer needs to draw a wide near-empty
  axis.
- Panel (b): dropped the inline text labels for Multi-task TCN-GRU/DC-PSR — recomputation showed
  these two points differ by only 0.0033 (Accuracy) / 0.0048 (Smooth), i.e. well under one
  rendered pixel at this panel's true physical column width, so any inline label placement
  collided with the other. The legend (diamond vs. star, same colors) still identifies both
  unambiguously; the markers' near-total overlap is itself a real, disclosed finding (panel (c)'s
  CI strip is the correct place for the statistical-closeness claim, not a crowded inline label).

## 12. Panel (c) redesign: DC-PSR vs backbone paired effect (this round)
Replaces the old absolute-CI forest plot with a **paired** comparison, DC-PSR (B12) vs its own
backbone Multi-task TCN-GRU (B11) only. Full detail in `CHANGELOG_fig6_paired_effect.md`; summary:

- **Protocol reuse, not invention**: `block_length=12`, `n_bootstrap=5000`, `random_seed=20260820`,
  `n_test_runs=304` are traced verbatim from
  `paper_data/01_PHM2010/01_main_D1/bootstrap/{multitask_tcn_gru,dc_psr}/bootstrap_config.json`
  (both agree). No generating script or `PROTOCOL.md` exists anywhere under `paper_data/` for the
  per-method bootstraps (searched `01_PHM2010`, `99_scripts`, `90_provenance` for
  "block_length"/"moving_block"/"moving-block" — no hits besides these two config files and their
  aggregate `D1_9methods_bootstrap_CI.csv`) — this is itself a disclosed gap, see §13.
- **True pairing**: `scripts/load_data.py::paired_moving_block_bootstrap()` draws ONE shared
  sequence of block-start indices per replicate and applies it to BOTH methods' aligned (same
  `run_id` order, verified identical truth sequence) 304-run predictions, then computes
  Delta = metric_B12 − metric_B11 per replicate. The existing per-method `bootstrap_samples.csv`
  files are NOT reused for this — no script exists to confirm their draws are replicate-aligned
  across methods, and subtracting two independently-bootstrapped CIs is explicitly out of scope.
- **Direction convention**: positive always favors DC-PSR. Acc/MacroF1/M_F1/M_Rec:
  `(B12−B11)×100` pp. M_to_E/M_to_L (lower=better, computed but not plotted, see below):
  `(B11−B12)×100` pp. Smooth (lower=better, order-dependent): relative improvement
  `(Smooth_B11−Smooth_B12)/Smooth_B11×100`, point estimate only.
- **Smooth has no bootstrap CI, by design**: block resampling concatenates non-adjacent 12-run
  blocks, injecting artificial sequence-boundary jumps into this order-dependent metric — the exact
  reason the existing per-method bootstraps never gave Smooth (or Rev/Jump) a CI either (see their
  `bootstrap_config.json` `"note"` field). The new panel respects this same, already-established
  project decision rather than fabricating a CI band with no defensible basis.
- **A striking finding, disclosed**: the entire Acc/Macro-F1/M-F1 gap traces to **exactly one**
  disagreeing prediction out of 304 (`run_id=225`, true stage=late; Multi-task TCN-GRU predicts
  `late` correctly, DC-PSR predicts `middle`). Every middle-stage prediction (n=129) is identical
  between the two methods, which is why M-Rec/M_to_E/M_to_L bootstrap CIs are degenerate
  (width exactly 0 — every possible block resample gives Delta=0 for these). Because this single
  disagreement always hurts B12 and never helps it, the Acc/MacroF1/M-F1 bootstrap CIs are
  one-sided: `CI_high` is exactly `0.0` for all three (DC-PSR is never favored, at best tied), while
  `CI_low` is a small negative number. This is reported plainly, not smoothed over.
- **M_to_E/M_to_L**: computed and written to `derived/B11_B12_paired_bootstrap_effects.csv` (both
  identical between methods, same reason as M-Rec) but not drawn in the forest plot — optional per
  the task brief, and would only add two more degenerate zero-CI rows without new information; the
  "identical" annotation on the M-Rec row already communicates this.
- **New derived output**: `derived/B11_B12_paired_bootstrap_effects.csv` — columns `metric,
  B11_value, B12_value, effect, effect_unit, CI_low, CI_high, bootstrap_type, n_test, block_length,
  n_bootstrap, seed`. Every row's point estimates (`B11_value`/`B12_value`) are asserted
  (`np.isclose`, atol=2e-4) against the frozen `D1_9methods_bootstrap_CI.csv` values before being
  written (see `logs/validation.txt`).
- **Layout**: panel (c) is now internally two stacked sub-axes (a paired-effect forest on top, a
  Smooth dumbbell strip below) inside the same GridSpec column, sized via
  `col_c = row1[4].subgridspec(2, 1, height_ratios=[0.56, 0.44], hspace=0.70)` in `assemble.py`;
  its column width-ratio widened slightly (0.90→1.05) to fit the wider "Multi-task TCN-GRU" tick
  label plus whisker+value-label text at this panel's true physical size. Its caption and two short
  annotation lines ("point estimate only, no CI...", "Rev = 0 → 0; Jump = 0 → 0...") are placed in
  `assemble.py` (not inside `panels.py`) from the REAL rendered positions of `ax_c_top`/`ax_c_bot`
  (`ax.get_position()` / `caption_bottom_fig_frac()`), not guessed offsets — this project's standing
  rule after repeated caption-collision bugs on panel (d) and Fig4-5 blocks A/B.
- **Panels (a)/(b)/(d)/(e1)-(e3) untouched** in this round except (a)/(b) receiving zero changes and
  (b) already having its legend style from a prior round; no scientific content, method roster, or
  color scheme changed anywhere else.

## 13. Newly-discovered protocol gap (disclosed)
No script or `PROTOCOL.md` documenting the original 9-method moving-block bootstrap procedure was
found anywhere under `paper_data/` — the `bootstrap_config.json`/`bootstrap_samples.csv`/
`bootstrap_summary.csv` files under `paper_data/01_PHM2010/01_main_D1/bootstrap/{method}/` are the
only formal record, and even their own `"note"` field references a `PROTOCOL.md` that does not
exist in this repository. This round's paired bootstrap reuses their three numeric parameters
exactly (block_length/n_bootstrap/seed) but had to write its own block-resampling implementation
(non-circular overlapping-block moving-block bootstrap, `ceil(n/block_length)` blocks drawn per
replicate then truncated to n=304) since no generating script exists to reuse directly. Recommended
follow-up: locate or reconstruct that original script/PROTOCOL.md so future work (e.g. Table 5) can
verify this round's implementation choice (non-circular blocks) matches the one used to produce the
original 9-method `D1_9methods_bootstrap_CI.csv`.

## 14. Remaining limitations (disclosed, not hidden)
- Panel (b)'s "Multi-source Attention" label sits high on the panel because that method genuinely
  has the highest Smooth (0.342) of all 9 methods — not a clipping bug (headroom above it was
  re-confirmed after the ylim adjustment), just visually close to the legend box; acceptable.
- This is a **first full pass**: script ran AND the assembled PNG was opened and visually reviewed
  at every iteration (multiple real layout bugs found and fixed this way, not just "ran without
  error") — but has not yet had the "≥6.5-7pt at true print size" micro-audit or a second reviewer
  pass that prior rounds' `VISUAL_QA_V*.md` documents performed. Recommended before this is called
  fully DONE for submission.
