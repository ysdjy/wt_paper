# Fig4-2 主比较 (paper's "Fig.6") — Panel (c) redesign: paired effect vs. backbone

Scope of this round: **panel (c) only**. Panels (a)/(b)/(d)/(e1)-(e3) unchanged. No retraining, no
hand-edited numbers. Fig4-3/4-4/4-5 (paper's "Fig.7/8/9") not touched.

## 1. What changed and why

The previous panel (c) was a moving-block-bootstrap 95% CI forest plot showing four methods'
(RF/MTF-AViTK/Multi-task TCN-GRU/DC-PSR) *absolute* Acc/Macro-F1/M-F1 CIs. This was flagged as
redundant with Table 5 and — more importantly — did not isolate the paper's actual scientific claim
about DC-PSR: not "DC-PSR is the best classifier" but "DC-PSR is within a small, honestly-reported
margin of its own backbone (Multi-task TCN-GRU) on classification, while meaningfully improving
probability-trajectory smoothness". An absolute 4-method CI plot cannot show a *paired* effect size
between two specific methods; two overlapping independent CIs are not a valid substitute for a
paired CI (overlap/non-overlap of two independent CIs is a well-known statistically invalid proxy
for a paired significance test).

Panel (c) is now **"(c) Paired effect of DC-PSR relative to its backbone"**: a paired
moving-block-bootstrap comparison of DC-PSR (B12) against Multi-task TCN-GRU (B11) only, plus a
separate Smooth-reduction element, per the task brief.

## 2. Code modified (in place, no new parallel script set)

- `_shared/data_utils.py` — added `stage_id()`, `ordered_prediction_arrays()`,
  `classification_metrics_from_ids()` (order-independent: Acc/MacroF1/M_F1/M_Rec/M_to_E/M_to_L,
  safe to evaluate on a block-resampled sequence), `sequence_diagnostics_from_ids()`
  (order-dependent: Rev/Jump/Smooth, valid ONLY on the true unresampled sequence). Formula/ordering
  ported verbatim from `paper_data/99_scripts/build_paper_data.py::recompute_transfer_metrics`
  (the authoritative source of the frozen numbers), not reinvented.
- `scripts/load_data.py` — added `paired_moving_block_bootstrap()` (the paired resampling +
  effect/CI computation), `FROZEN_B11_B12` (cross-validation targets), `PAIRED_BLOCK_LENGTH=12`,
  `PAIRED_N_BOOTSTRAP=5000`, `PAIRED_SEED=20260820` constants; wired into `main()` to write
  `derived/B11_B12_paired_bootstrap_effects.csv` and log validation lines.
- `scripts/panels.py` — `load_all()` now also returns `paired_df`; `panel_c()` fully rewritten,
  signature changed from `panel_c(ax, main_df)` to `panel_c(ax_top, ax_bot, main_df, paired_df)`
  (two sub-axes: forest on top, Smooth dumbbell below); `render_previews()` updated to build a
  2-row sub-gridspec for the standalone panel-c preview.
- `scripts/assemble.py` — row1's column-c slot is now a `subgridspec(2, 1, ...)` instead of a
  single Axes; panel (c)'s caption and its two short annotation lines
  ("point estimate only, no CI...", "Rev = 0 → 0; Jump = 0 → 0...") are placed here (not inside
  `panels.py`) from the real rendered positions of `ax_c_top`/`ax_c_bot`, following this project's
  standing rule against guessed caption offsets. Column-c width-ratio widened 0.90→1.05.

## 3. Panel (c) layout

Two stacked areas inside one panel, deliberately NOT sharing one numeric x-scale:

- **Top — paired-effect forest plot.** y-axis: Acc, Macro-F1, M-F1, M-Rec. x-axis: Δ (percentage
  points), `DC-PSR − backbone`, positive = favors DC-PSR (explicit in the axis label and via a
  vertical x=0 reference line). Dot = observed B12−B11; whiskers = paired moving-block bootstrap
  95% CI. All four dots/whiskers use one neutral blue-gray color (`#5B7A96`) — never red/alarming —
  since the largest gap is only ~0.4pp. M-Rec's CI collapses to a single point (both methods agree
  on every middle-stage sample); a small italic "identical" label replaces what would otherwise be
  an invisible zero-width whisker.
- **Bottom — Smooth reduction, separate unit.** A B11→B12 dumbbell (diamond = Multi-task TCN-GRU,
  star = DC-PSR, same colors/markers as panel (b)) on its own absolute-Smooth x-axis, with the
  relative-improvement percentage (`-20.5%`) annotated above the connecting line. Labeled "point
  estimate only, no CI (order-dependent metric)" directly underneath — no CI is fabricated for a
  metric block resampling cannot validly bootstrap.
- **Bottom annotation line**: `Rev = 0 → 0;  Jump = 0 → 0  (both methods, identical on the 304-run
  sequence)` — exactly the short annotation-only treatment requested, no full visual sub-panel.

## 4. Formal paired-bootstrap settings (traced, reused, not invented)

| Parameter | Value | Source |
|---|---|---|
| block_length | 12 | `paper_data/01_PHM2010/01_main_D1/bootstrap/{multitask_tcn_gru,dc_psr}/bootstrap_config.json` |
| n_bootstrap | 5000 | same |
| random_seed | 20260820 | same |
| n_test_runs | 304 | same |
| test universe | `run_id_12_315_common_304` (C6, run_id 12–315, contiguous) | `predictions_common_universe/D1_{multitask_tcn_gru,dc_psr}_304runs.csv` |

No generating script or `PROTOCOL.md` was found anywhere under `paper_data/` (`grep`-searched
`01_PHM2010`, `99_scripts`, `90_provenance` for `block_length`/`moving_block`/`moving-block`) — the
three config JSONs above are the only formal record of this protocol; see README §13 for the
disclosed follow-up recommendation. Block-resampling mechanism implemented here (non-circular,
overlapping-block draws from the 293 possible start positions, `ceil(304/12)=26` blocks drawn per
replicate then truncated to 304) is standard moving-block bootstrap, applied identically (same
random block-start draw) to BOTH methods per replicate — never two independently-bootstrapped CIs
subtracted afterward.

## 5. Observed effects (95% CI), reused from `derived/B11_B12_paired_bootstrap_effects.csv`

| Metric | B11 (Multi-task TCN-GRU) | B12 (DC-PSR) | Effect | 95% CI |
|---|---|---|---|---|
| Acc | 0.990132 | 0.986842 | −0.329 pp | [−0.987, 0.000] pp |
| Macro-F1 | 0.990230 | 0.987102 | −0.313 pp | [−1.128, 0.000] pp |
| M-F1 | 0.988235 | 0.984375 | −0.386 pp | [−1.369, 0.000] pp |
| M-Rec | 0.976744 | 0.976744 | 0.000 pp | [0.000, 0.000] pp (degenerate — identical on every middle-stage sample) |
| Smooth | 0.023590 | 0.018763 | +20.46 % (relative reduction) | point estimate only, no CI |

All four classification-metric CIs have `CI_high = 0.0` exactly (see README §12 — this traces to a
single disagreeing prediction, `run_id=225`, out of 304). This is reported as-is: small, honestly
one-sided, never described as "significant decline".

## 6. Newly-discovered issues

1. **No formal bootstrap-generating script / PROTOCOL.md exists** for the original 9-method
   bootstrap, despite `bootstrap_config.json`'s own `"note"` field referencing one. Recommend
   locating or reconstructing it so this round's implementation choices (non-circular block
   sampling) can be verified against the original. See README §13.
2. **The entire DC-PSR-vs-backbone classification gap is driven by one sample** (`run_id=225`, true
   stage `late`; B11 correct, B12 predicts `middle`). Every other prediction, and all 129
   middle-stage predictions, are identical between the two methods. This is a genuinely useful,
   previously-undocumented fact for the manuscript's discussion of the ~0.3-0.4pp gap's practical
   (in)significance — worth citing explicitly in the main text if the authors want to preempt a
   reviewer asking "is this gap real."

## 7. Outputs

- `outputs/Fig4_2_main_comparison.{pdf,svg}`, `_600dpi.png`, `_preview.png` (regenerated).
- `outputs/panel_previews/panel_c_preview.png` (regenerated, two-part panel).
- `../final_pdf/fig4_2_main_comparison.pdf` / `_600dpi.png` (regenerated, fixed submission name).
- `derived/B11_B12_paired_bootstrap_effects.csv` (new).
- `logs/validation.txt` (regenerated — includes new paired-bootstrap PASS/FAIL assertions).
