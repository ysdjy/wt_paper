# Fig4-3 鲁棒性 (Robustness / Generalization) — first pass, visually reviewed

## 1. Scientific question
Does DC-PSR's advantage generalize across target-condition difficulty (PHM2010 D1/D2/D3) and
across datasets (NASA Milling, MTW-CM)? Headline (verified against frozen data): method ranking is
target-condition-dependent — no single method wins on every task (D1: Multi-task TCN-GRU/DC-PSR
lead; D2: HTT-Net (adapted)/Dynamic GIN+TGP lead; D3: Dynamic GIN+TGP leads). Backbone→DC-PSR
trades a small/mixed classification delta for a consistently-signed M-F1/Smooth/Jump improvement
direction on NASA and MTW-CM, though PHM D3 shows a genuine counter-example (Smooth slightly
*worse* for DC-PSR there) — kept visible in panel (b), not hidden.

## 2. Panel list
- (a) PHM D1/D2/D3 × 9-method task-level landscape (Acc/M-F1/Smooth only, not the full metric
  roster), direction-corrected color, raw value always shown, DC-PSR row outlined.
- (b) Multi-task TCN-GRU → DC-PSR paired change (ΔAcc, ΔM-F1 in percentage points; Smooth-benefit,
  Jump-benefit as *relative* % change, positive = improvement) across PHM D1/D2/D3 + NASA (N1–N4
  avg) + MTW-CM (3-task avg).
- (c1)/(c2) External task-level paired dumbbell profiles (Multi-task TCN-GRU vs. DC-PSR), M-F1 and
  Smooth, individual NASA N1–N4 and MTW-CM D1-M/D2-M/D3-M tasks kept separate (not collapsed to one
  averaged bar).

**No confusion-matrix inset** (resolved decision — Fig4-2 already carries representative confusion
matrices; this figure stays focused on domain-shift/generalization).

## 3. Data source
See `inputs_manifest.csv`. Primary: `paper_data/07_figure_ready/fig2/taskwise_absolute.csv` (D1/D2/D3
× 9 methods), `paper_data/07_figure_ready/fig3/cross_dataset_absolute.csv` +
`cross_dataset_deltas.csv` (PHM/NASA/MTW-CM, B11/B12 internal shorthand for Multi-task
TCN-GRU/DC-PSR), `paper_data/02_NASA/task_level_results.csv` (per-task N1–N4 breakdown, not
available in the pre-aggregated cross-dataset file).

## 4. Original manuscript code reused (visual framework)
- `_shared/style.py`'s `add_axis_arrows`/`style_axis`/hatched-bar helpers (ported from
  `代码/8.2图10.py`, same module built for Fig4-2, reused here for consistency).
- `代码/8.2图11.py`'s diverging colormap (`CONFUSION_CMAP`, same one used for Fig4-2 panel (d))
  reused for panel (a)'s heatmap cells, keeping one consistent color language across both figures.
- `代码/8.2图13.py`'s dual-source/single-source dumbbell-style paired comparison idiom informed
  panel (c)'s design (dumbbell/slope, not mean±std dots, since individual task values — not just
  mean/std — were the explicit requirement this round).

## 5. Previous `paper_data/figure` code reused for data calculation only
- None imported directly (kept `New_figure` self-contained); the *data selection* precedent —
  using `cross_dataset_deltas.csv`'s already sign-corrected `Smooth_benefit`/`Jump_benefit` columns
  rather than re-deriving direction from scratch — follows the same convention validated in the
  prior `figure/fig3` round.

## 6. New code written
- `scripts/load_data.py`: loads/merges/validates all three panels' tables; recomputes PHM
  D1/D2/D3 deltas directly from `taskwise_absolute.csv` (Multi-task TCN-GRU vs. DC-PSR) since no
  pre-built PHM per-task delta file exists; converts NASA/MTW-CM absolute `Smooth_benefit`/
  `Jump_benefit` (which are in absolute units) to *relative* % by dividing by the backbone's own
  absolute Smooth/Jump — this is what makes panel (b)'s bars comparable across PHM (Smooth~0.02),
  NASA (Smooth~0.34), and MTW-CM (Smooth~0.04), which have very different absolute scales.
- `scripts/panels.py`, `scripts/assemble.py` — panel-first rendering + final composite, same
  pattern as Fig4-2.

## 7. Visual interpolation
None. Every value is a frozen authoritative number or a direct arithmetic transform (percentage
points, relative-% benefit) of one, never an interpolated or fabricated point.

## 8. Data validation
`logs/validation.txt` — panel (b)'s recomputed PHM D1 Smooth-benefit (20.46% vs. docx's 20.5%),
NASA Smooth-benefit (34.96% vs. 35.0%) and Jump-benefit (50.0% vs. 50.0%), MTW-CM ΔM-F1 (10.04pp),
Smooth-benefit (23.9%) and Jump-benefit (82.5%) all checked via `np.isclose` against the docx's
stated headline numbers — all PASS. Panel (c) table shape asserted (7 tasks × 2 methods = 14 rows).

## 8a. Refinement round (CIE-submission pass)
Added outer canvas border + two block borders ("Task-level landscape" wrapping (a);
"Backbone → DC-PSR change" wrapping (b)/(c1)/(c2)), via `_shared/style.py`'s new border helpers.
Canvas height 140mm→142mm to fit the block-boundary gap (explicit thin spacer GridSpec row, same
pattern as Fig4-2). One collision found and fixed by opening the PNG: the bottom block's label
initially overlapped panel (b)'s own legend, which floats above its axes
(`bbox_to_anchor=(0,1.18)`) — fixed by computing the block's top edge from the legend's actual
extent, not just the axes top. Added fixed-name export (`fig4_3_robustness.pdf`/`_600dpi.png`) to
`New_figure/final_pdf/`.

## 9. Output path
`outputs/Fig4_3_robustness.{pdf,svg}`, `_600dpi.png`, `_preview.png`. Panel-first review PNGs kept
in `outputs/panel_previews/`.

## 10. Panel-first review notes (bugs found and fixed via actually opening the PNGs)
- Panel (c1)/(c2) captions collided when first assembled at the composite's true column width
  ("(c1) M-F1, NASA N1–N4 & MTW(c2) Smooth..." ran together) — fixed by shortening both captions
  to two lines and increasing the `wspace` between the two sub-panels, the same fix pattern used
  for Fig4-2's panel (e).
- Panel (a) cross-checked against the manuscript narrative during review: D2's HTT-Net (adapted)
  (0.928/0.923) and Dynamic GIN+TGP (0.908/0.883) are visibly the two strongest cells in that
  column, and D3's Dynamic GIN+TGP (0.964/0.948) is the single darkest/best cell in that column —
  both match the docx's target-condition-dependence claims exactly, confirming the heatmap is
  telling the right story rather than an artifact of the color scale.

## 11. Remaining limitations (disclosed)
- Panel (a)'s Multi-source Attention row has markedly worse Smooth on D1/D3 (0.325/0.659) than
  every other method — real data, not an error, but visually dominates the "worst" end of that
  column; no adjustment made (would misrepresent the data to clip or rescale it).
- First full pass: assembled PNG opened and visually reviewed, one real caption-collision bug
  found and fixed this way; has not yet had a second-reviewer pass or the full ≥6.5pt-at-print-size
  micro-audit prior rounds' `VISUAL_QA_V*.md` performed.
