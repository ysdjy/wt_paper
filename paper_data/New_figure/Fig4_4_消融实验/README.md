# Fig4-4 消融实验 (Ablation / Probability-State Formation) — first pass, visually reviewed

## 1. Scientific question
How is DC-PSR's final probabilistic state representation formed through the A1→A6 ablation path,
and what is the trade-off between classification performance and trajectory consistency? Headline
(verified against frozen data): A1–A4 have byte-identical hard classification (Acc/Macro-F1/M-F1/
M-Rec) — fine-state assistance, q-prior, and weighted mixture reshape the *probability distribution*,
not the argmax decision. A5 (causal ordered filtering) achieves the strongest smoothing (Smooth
−42.4% vs. A1) at a real classification cost (Acc −1.3pp vs. A1–A4). A6 (final blend) recovers most
of A5's classification loss (+0.99pp Acc, +1.18pp M-F1, +1.55pp M-Rec vs. A5) while keeping Smooth
−20.5% vs. A1. **This is explicitly not a monotonic-improvement story** — panel (a)'s A5 dip and
panel (b)'s A5-then-A6 path both show this honestly.

## 2. Panel list (revised after refinement round — see §12)
- (a) Hard-decision performance (Acc/Macro-F1/M-Rec bars) **+ Smooth on a secondary axis** (line,
  ↓ better, every node value-labeled), A1–A6, natural primary-axis range (not zoomed to exaggerate
  or compressed to hide the A5 dip). This one panel now shows the full classification/consistency
  trade-off on its own.
- (b) **State-wise recognition profile** (E-F1/M-F1/L-F1 line plot, markers, every node
  value-labeled), A1→A6 — replaces the earlier sparse accuracy-smoothness scatter; shows *which*
  stage drives the A5 dip and A6 recovery, complementing rather than duplicating panel (a).
- (c) **Probability-state formation** (main mechanism panel, unchanged): p_E/p_M/p_L over the C6
  lifecycle for 4 representative configurations (A1, A4, A5, A6 — not all 6), stage-shaded
  background, 原 Fig.12 visual language.
- (d1)/(d2) Local and cumulative L1 probability-variation diagnostics (unchanged), all 6
  configurations, A1/A5/A6 emphasized.
- (e) **Redesigned** mechanism-progression strip: chevron/step-module band (not plain circles). A1–A3
  neutral/muted; A4 highlighted as the core-fusion stage (bold outline); A5 visually distinct as the
  strongest-ordering stage (bold outline, saturated accent); A6 rendered as a rounded "final output"
  module rather than a chevron, reading as the pipeline's endpoint. Role labels (input/structure/
  core fusion/strongest ordering/final output) above each module, description below.

## 3. Data source
See `inputs_manifest.csv`. `paper_data/07_figure_ready/fig4/A1_A6_absolute.csv` (6-config
authoritative metrics, panels a/b), `A1_A6_probability_trajectories.csv` (1824 rows = 6×304,
filtered to the 4-config subset for panel c), `A1_A6_lifecycle_variation.csv` /
`A1_A6_cumulative_variation.csv` (1824 rows each, all 6 configs, panel d).

## 4. Original manuscript code reused (visual framework)
- `_shared/style.py`'s arrow-axis/hatched-bar helpers (from `代码/8.2图10.py`), reused for panel (a),
  consistent with Fig4-2/Fig4-3.
- Stage-background shading in panel (c) (`_stage_background()`) is written in the spirit of
  `代码/8.2图12.py`'s `add_stage_background`/`add_true_stage_background` (shade by true stage along
  the life axis) and `代码/7.6消融实验.py::plot_fig13_probability_evolution` (per-config small
  multiples of E/M/L probability with stage shading) — this is the "probability-state formation"
  panel both the audit and this round's brief specifically call out as the mechanism-evidence core.
- Stage colors (Early teal-green `#1B9E77` / Middle warm-orange `#E6A01A` / Late muted-red `#C44E52`)
  match `代码/8.2图17.py`/`8.2图18.py`'s own palette, consistent with Fig4-2/Fig4-3's shared style.

## 5. Previous `paper_data/figure` code reused for data calculation only
- None imported directly. The *data-selection* precedent from the prior `figure/fig3` v4 round
  (panel (d) should read `lifecycle_variation`/`cumulative_variation` content instead of
  near-all-zero Rev/Jump bars, since Rev/Jump carry almost no information at this configuration
  scale) is followed here — panel (d) uses exactly that evidence, per this round's own explicit
  instruction not to waste a panel on meaningless near-zero bars.

## 6. New code written
- `scripts/load_data.py` — loads/validates all 5 source CSVs; explicitly **asserts** A1–A4 are
  byte-identical on Acc/Macro-F1/M-F1/M-Rec (`np.allclose(..., atol=0)`) and that A5's Acc is
  materially below A1–A4 (not just numerically different) — encoding the "not monotonic" claim as
  a hard check, not just a caption note. All 10 headline numbers (A1/A5/A6 Smooth, A5→A1 and
  A6→A1 Smooth reduction %, A5/A6 Acc, A6-vs-A5 Acc/M-F1/M-Rec recovery) verified via `np.isclose`
  against the docx's stated values.
- `scripts/panels.py`, `scripts/assemble.py` — panel-first rendering + final composite.

## 7. Display-only transformations (disclosed)
- None beyond an axis-unit change: panel (b)'s x-axis shows Accuracy ×100 (percentage points)
  instead of the raw 0–1 fraction — a display-only unit conversion, not a data change.
- Panel (d1)/(d2)'s `local_variation_l1_smoothed` and the underlying rolling-mean smoothing were
  already computed upstream in the frozen `07_figure_ready` CSVs (documented there as a 7-run
  centered rolling mean) — not recomputed or altered in this figure's own code.
- No fabricated probability curves, no manual reshaping of any trajectory, no re-ranking of
  configurations. Panel (c) plots the raw per-run `p_E`/`p_M`/`p_L` values directly from the frozen
  304-run trajectories, one line per stage, no smoothing applied by this figure's code.

## 8. Data validation
`logs/validation.txt` — all checks PASS, including the two structural assertions (A1–A4 byte-
identical; A5 materially below A1–A4). See §1 for the numeric values.

## 8b. Refinement round (CIE-submission pass, deeper layout refinement)
Reorganized from 4 floating rows into 3 bordered blocks (Performance: a/b; Probability-state
formation: c; Variation & mechanism: d1/d2/e tied together in one nested block) + outer canvas
border. Canvas height **232mm→196mm** (−36mm, ~15%) achieved by fixing root causes, not cropping:
panel (e)'s `ylim` had a large dead zone below its description labels (`ylim=(0,1.05)` when content
only needed roughly `(0.18,1.05)`) — tightened, and its caption offset shrunk from `y=-0.62` to
`y=-0.30` accordingly; (d1)/(d2)/(e) are now one GridSpec block with a small internal `hspace`
instead of three separate top-level rows each with their own large margin. Two block-label/legend
collisions found by opening the PNG and fixed by computing real clearance (legend height ×
axes-height-fraction) rather than a flat guessed margin: panel (a)'s "Performance" block label
initially overlapped its own 4-item legend (floats above the axes), and the bottom block's
"Variation & mechanism" label initially crowded panel (d1)'s in-axes legend. Added fixed-name
export (`fig4_4_ablation.pdf`/`_600dpi.png`) to `New_figure/final_pdf/`.

## 9. Output path
`outputs/Fig4_4_ablation.{pdf,svg}`, `_600dpi.png`, `_preview.png`. Panel-first review PNGs in
`outputs/panel_previews/`.

## 10. Panel-first review notes (bugs found and fixed by opening the PNGs)
- Panel (e)'s caption originally collided with the "+ weighted fusion" label directly above it —
  fixed by shortening all six labels to single lines and pushing the caption further below the
  label row.
- Panel (c)'s group caption ("(c) Probability-state formation: ...") first collided with the A1/A4/
  A5/A6 sub-captions directly above it, then (after a first fix attempt) collided with panel (d1)'s
  legend, which had been placed *above* its own axes — root cause was the legend extending outside
  its axes into the same inter-row gap the (c) caption occupies. Fixed properly (not by further
  offset-tuning) by moving panel (d1)'s legend to sit *inside* its own axes (in the gap between the
  two local-variation peaks) instead of above it, plus increasing the figure's overall height and
  inter-row spacing.

## 11. Remaining limitations (disclosed)
- Panel (d1)'s in-axes legend sits close to the tallest peak's tip (A5, ~0.18) at the composite's
  true physical scale — legible, very minor visual proximity, not text-on-text overlap.
- Panel (b)'s A6 M-F1 (0.984) and L-F1 (0.994) value labels sit close together at the composite's
  true physical scale — legible, minor visual proximity.
- First full pass: assembled PNG opened and visually reviewed through multiple iterations across
  both the initial build and this refinement round — has not yet had a second-reviewer pass or the
  full ≥6.5pt-at-print-size micro-audit.

## 12. Refinement round (post-initial-review, user-directed)

Three targeted revisions, all other panels/composition held fixed:

- **Panel (a)**: restored the Smooth secondary-axis line (dropped in the initial build's redesign
  from "trajectory panel" to "state-wise profile" panel — the user asked for it back specifically
  in panel (a), with per-node value labels). New `_shared`-free code path: `abs_df["Smooth"]`
  plotted on `ax.twinx()`, each of the 6 nodes annotated with its exact value.
- **Panel (b)**: replaced the accuracy-smoothness scatter entirely with a state-wise E-F1/M-F1/L-F1
  recognition profile, recomputed **directly from sample-level labels** (never hand-entered) in
  `A1_A6_probability_trajectories.csv` via `du.precision_recall_f1_per_class`, one call per
  configuration. Cross-validated: recomputed M-F1 matches `A1_A6_absolute.csv`'s authoritative
  M-F1 exactly (`np.allclose(atol=1e-6)`) for all 6 configs — confirms this is the same underlying
  classification, not a divergent recomputation. Result table: E-F1/M-F1/L-F1 all byte-identical
  across A1–A4 (0.9825/0.9882/1.0000), all three dip at A5 (0.9711/0.9725/0.9889), all three
  partially recover at A6 (0.9825/0.9844/0.9945) — directly shows the A5 dip and A6 recovery are
  not classification-metric artifacts but hold at the per-stage level too.
- **Panel (e)**: redesigned from plain colored circles to a chevron/step-module band using
  `matplotlib.patches.Polygon` (chevrons) and `FancyBboxPatch` (A6's rounded final module), with
  bold outlines on A4/A5 and role-label annotations, per §2 above.

**Bugs found and fixed during this round's panel-first review**:
1. Panel (b)'s E-F1/M-F1 value labels (only ~0.006 apart on A1–A4) collided when both used the
   same "above marker" offset — fixed by giving each series its own offset direction (E-F1 below,
   M-F1/L-F1 above).
2. Panel (e)'s new A6 module (wider than the old circle) was clipped by an `xlim` that hadn't been
   recalculated for the new geometry — fixed by tracing the actual cumulative x-extent of all 6
   modules rather than reusing the old panel's guessed limit.
3. At full composite scale, panel (a)'s new secondary-axis label ("Smooth (↓ better)") and panel
   (b)'s primary-axis label ("Stage-wise F1") — now adjacent across the row-1 column gap — collided
   with each other; fixed by widening row 1's `wspace` (0.32→0.62) and trimming both labels'
   `labelpad`.
