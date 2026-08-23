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
- (c) Bootstrap 95% CI forest plot (Acc/Macro-F1/M-F1), 4 representative methods (RF, MTF-AViTK,
  Multi-task TCN-GRU, DC-PSR).
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
`paper_data/01_PHM2010/01_main_D1/predictions_common_universe/`.

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

## 11. Remaining limitations (disclosed, not hidden)
- Panel (b)'s "Multi-source Attention" label sits high on the panel because that method genuinely
  has the highest Smooth (0.342) of all 9 methods — not a clipping bug (headroom above it was
  re-confirmed after the ylim adjustment), just visually close to the legend box; acceptable.
- This is a **first full pass**: script ran AND the assembled PNG was opened and visually reviewed
  at every iteration (multiple real layout bugs found and fixed this way, not just "ran without
  error") — but has not yet had the "≥6.5-7pt at true print size" micro-audit or a second reviewer
  pass that prior rounds' `VISUAL_QA_V*.md` documents performed. Recommended before this is called
  fully DONE for submission.
