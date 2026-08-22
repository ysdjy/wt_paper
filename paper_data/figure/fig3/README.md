# Fig.3 — A1→A6 ablation mechanism band (paper Fig. 4-4)

## Figure purpose

Answers: what does each module in the A1→A6 progression actually change — hard classification,
middle-stage/transition consistency, or the shape of the probability trajectory over the tool
lifecycle? Shows this is a **trade-off + final balance** story, not a monotonic improvement:
A1–A4 leave argmax classification unchanged while progressively smoothing the probability
trajectory; A5 (causal ordered filter) gives the strongest smoothing but costs classification
accuracy and middle-stage recall; A6 (final blend) recovers most of A5's classification loss
while keeping most of its smoothing benefit relative to A1.

## Input files (all authoritative/derived, none touched by the pending freeze cleanup)

- `paper_data/07_figure_ready/fig4/A1_A6_absolute.csv` — config-level metrics, the **sole
  permitted ablation source** (per `paper_data/README.md`).
- `paper_data/07_figure_ready/fig4/A1_A6_probability_trajectories.csv` — 1,824 rows (6 configs ×
  304 runs), per-run `true_stage`/`pred_stage`/`p_E`/`p_M`/`p_L`. Used to independently recompute
  E-F1/M-F1/L-F1/M-Precision/M-Recall/Acc/Macro-F1 per configuration (panel b + validation).
- `paper_data/07_figure_ready/fig4/A1_A6_lifecycle_variation.csv` — 1,824 rows, per-run local L1
  probability variation (smoothed), used in panel (d).
- `paper_data/07_figure_ready/fig4/A1_A6_cumulative_variation.csv` — 1,824 rows, per-run
  cumulative L1 probability variation, used in panel (e).

See `inputs_manifest.csv` for row/column counts and SHA-256 of each file as read.

## Derived data

- `derived/A1_A6_classwise_metrics.csv` — E-F1/M-F1/L-F1/M-Precision/M-Recall/Acc/Macro-F1 per
  configuration, recomputed from `A1_A6_probability_trajectories.csv` (not read from any
  pre-aggregated table).

## Plot script

`plot_fig3.py` — self-contained, run with:

```
python paper_data/figure/fig3/plot_fig3.py
```

Panels:
- (a) Predictive performance (Acc/Macro-F1/M-F1) across A1→A6.
- (b) State-wise recognition profile (E-F1/M-F1/L-F1), recomputed from run-level labels —
  shows the A5 dip and A6 recovery per class, not just in aggregate.
- (c) Middle-stage & transition consistency heatmap (M-Rec, M→E, M→L, Rev, Jump, Smooth).
  Color is a **within-row min-max normalized "benefit" score** (always 1=best, direction-corrected
  so lower-is-better metrics are flipped before normalizing) — used **only** for cell color. Every
  cell's displayed number is the true raw metric value; Smooth is never itself relabeled as
  "higher is better."
- (d)/(e) Lifecycle local and cumulative L1 probability variation curves, one line per
  configuration (A1 light grey → A6 theme red), shared `relative_tool_life` x-axis — this is the
  panel that visualizes the actual mechanism, not just a summary statistic.

## Outputs

- `outputs/fig3_main.png` / `.pdf` / `.svg`

## Validation (see `logs/validation.txt`)

All assertions run inside `plot_fig3.py` and re-verified on every run:
- Recomputed per-config Acc/M-F1/M-Rec from run-level `true_stage`/`pred_stage` match
  `A1_A6_absolute.csv` to `atol=1e-6` for all 6 configurations.
- A1–A4 have byte-identical Acc/Macro-F1/M-F1/M-Rec (confirms "argmax unchanged, only probability
  geometry changes" claim).
- Smooth benefit vs A1: A5 = 42.38% (expected ≈42.4%), A6 = 20.48% (expected ≈20.5%).
- A6 recovery vs A5: ΔAcc = 0.99pp, ΔM-F1 = 1.18pp, ΔM-Rec = 1.55pp (all match the design doc's
  Appendix A numbers within rounding).
- `A1_A6_lifecycle_variation.csv` / `A1_A6_cumulative_variation.csv` each contain exactly 304 rows
  per configuration (identified via their native `ID` column).

## v2: reference-style visual reconstruction

`plot_fig3_v2.py` produces `outputs/fig3_v2_reference_style.{png,pdf,svg}`. **Statistics are
unchanged from v1** — v2 imports v1's `load()`, `recompute_classwise()`, and `validate()` directly
and re-runs the same assertions, so v2 is independently self-validating against the same headline
numbers, not just a visual restyle. Style references:
`reference/reference_mockup.png` (primary, MATLAB-rendered, already has bottom-centered captions
and dual-axis bar+line panels) and `reference/reference_mockup_alt_original.png` (secondary,
earlier Python draft — source of the "mechanism evidence path" flow-chain and "Ablation Pareto
trajectory" ideas). A third mockup was found at `视觉参考效果图/` during this build (a bright
poster-style dashboard with a top banner title and fictional numbers); it was **not** used as a
layout template since it directly conflicts with this round's hard rules (no top title; muted
navy/teal/gold palette), only its A1→A6 mechanism-annotation *idea* overlapped with (and
reinforced) the alt_original mockup. See `reference/SOURCE.md`.

**Layout changes vs. v1** (fig3 is one of the three figures explicitly allowed stronger visual
impact than fig1/fig2, per the task brief):
- No top figure-level title; figure-level caption "消融实验" + English subtitle centered at the
  bottom.
- Two new panels not in v1: (a) a **mechanism evidence-path flow-chain** — six boxes A1→A6 with
  real per-configuration ΔAcc/ΔM-F1/Smooth-benefit vs. A1, built from
  `A1_A6_delta_vs_A1.csv` (loaded by v1's `load()` but never actually plotted there); (e) an
  **ablation Pareto trajectory** — Acc-vs-Smooth scatter with A1→A6 connected by arrows in
  module-progression order, showing the mechanism as a path through score space rather than a bar
  chart.
- Panels (b)/(d) (predictive performance; middle-stage & transition consistency) switched from
  line-only to dual-axis bar+line combos with in-plot callout annotations ("A5: strongest
  smoothing... classification dip" / "A6: balanced... accuracy restored"), matching the primary
  reference's style — annotation text uses live recomputed percentages, not copied from the
  mockup.
- Panels (f)/(g) (lifecycle local/cumulative probability variation) kept from v1 essentially as-is
  — these were already strong and directly match the reference's "trajectory stability
  diagnostics" concept; added an A6-vs-A1 terminal-value annotation on the cumulative panel.
- Colors switched to the shared `ABLATION_COLORS`/`STAGE_COLORS` from `style_v2.py` (grey→teal
  scale with A5 called out in gold), consistent with the other 4 figures.

**Deliberately not copied**: any Smooth/Acc/M-F1 number visible in either reference mockup (the
primary mockup's numbers happen to be structurally similar but are not bit-identical to this
project's frozen data — e.g. its A1 Smooth=0.0236 vs. this project's real Smooth values, which are
recomputed independently in `plot_fig3.py`'s `validate()` and asserted to match the design doc);
the poster-style dashboard's icon call-out boxes and top banner.

**Bugs found and fixed**: same GridSpec-margin-before-captioning bug documented in fig1_v2's
README (margins set in the `GridSpec` constructor, not via a later `subplots_adjust()`); panel
(e)'s `(e)` letter was originally placed upper-left where it collided with the A5 marker (data
happens to start near that corner) — moved to `loc="upper right"`; the A6 trajectory label
originally floated with no visible connection to its marker — tightened its offset to sit
immediately beside the point.

## Open issues

- `A1_A6_absolute.csv` column headers contain literal `→` characters that mis-render as mojibake
  when printed to this Windows cp936 console — cosmetic terminal-display issue only; the CSV
  bytes are correct UTF-8 and the script reads/writes with explicit `encoding="utf-8"`.
- v2 panel (e): the A1/A2 point labels are visually faint against the dense A2/A3/A4 cluster
  (those three configurations have nearly identical Accuracy, so their labels sit close together);
  legible at full resolution but could use a proper label-collision-avoidance pass in a future
  round.
