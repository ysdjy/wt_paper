# Fig.2 — Cross-condition / cross-dataset generalization landscape (paper Fig. 4-3)

## Figure purpose

Answers: does method ranking stay stable when the target condition changes (D1→D2→D3 within
PHM2010), and does DC-PSR's mechanism-level advantage (M-F1, trajectory consistency) generalize
across data sources (PHM2010 / NASA Milling / MTW-CM)? Core narrative (validated, not asserted):
**no single method wins every target condition** — Multi-task TCN-GRU tops D1, HTT-Net (adapted)
tops D2, Dynamic GIN + TGP tops D3 on Acc — so cross-condition comparison must be read task-by-task,
never as one pooled absolute-Acc average. Against its direct backbone (Multi-task TCN-GRU →
DC-PSR), DC-PSR trades a small classification cost for a consistent Smooth/M-F1/Jump benefit that
holds in direction (though not magnitude) across PHM2010, NASA Milling, and MTW-CM.

## Input files

Unlike fig1/fig3, this figure draws from **two** on-disk `07_figure_ready` folders because the
on-disk numbering does not match the final figure numbering (see
`paper_data/figure/FIGURE_PROGRESS.md` §1):

- `paper_data/07_figure_ready/fig2/taskwise_absolute.csv` — D1/D2/D3 × 9 methods, absolute
  metrics (27 rows). Source for panels (a) raw-value annotations and (b) paired-delta computation.
- `paper_data/07_figure_ready/fig2/taskwise_normalized.csv` — within-task-and-metric normalized
  scores (Acc/M_F1/Smooth only), already direction-corrected so 1=best regardless of metric
  direction. Used **only** for panel (a) cell color; raw values are always the annotated number.
- `paper_data/07_figure_ready/fig3/cross_dataset_absolute.csv` — PHM2010/NASA Milling/MTW-CM,
  method `B11` (=Multi-task TCN-GRU) vs `B12` (=DC-PSR), absolute Acc/M_F1/Smooth/Jump. Source for
  panel (c). Confirmed dataset labels are exactly `{PHM2010, NASA_MILLING, MILLING_CROSS_MACHINE}`
  — no `MIMII` label present anywhere in this project's data.
- `paper_data/07_figure_ready/fig3/cross_dataset_deltas.csv` — precomputed deltas, read only to
  sanity-check the script's own from-scratch recomputation in panel (c) (not plotted directly).

See `inputs_manifest.csv` for row/column counts and SHA-256 of each file as read.

## Derived data

- `derived/PHM_backbone_to_dcpsr_paired_delta.csv` — Multi-task TCN-GRU → DC-PSR ΔAcc/ΔM-F1/ΔM-Rec
  (percentage points) and Smooth benefit (%) for D1/D2/D3, computed directly from
  `taskwise_absolute.csv` (not from any pre-built delta table — `07_figure_ready/fig2/` has no
  D1/D2/D3 paired-delta file, only fig3's cross-dataset one).

## Plot script

`plot_fig2.py` — run with:

```
python paper_data/figure/fig2/plot_fig2.py
```

Panels:
- (a) Three side-by-side 9-method × {Acc, M-F1, Smooth} heatmaps, one per PHM task (D1/D2/D3).
  Color = within-task-and-metric normalized benefit (1=best); every cell shows the true raw value.
- (b) Multi-task TCN-GRU → DC-PSR paired delta across PHM D1/D2/D3 (ΔAcc, ΔM-F1, ΔM-Rec in pp;
  Smooth benefit in %, defined explicitly in the panel subtitle as
  `Smooth_backbone − Smooth_DC-PSR` so raw Smooth is never itself relabeled "higher is better").
- (c) Cross-dataset B11→B12 delta matrix: PHM2010 D1, NASA Milling N1–N4 average, and MTW-CM
  D1-M/D2-M/D3-M plus their 3-task average. ΔAcc/ΔM-F1 in pp; Smooth/Jump shown as % benefit.
  Color is normalized **per column** (pp-scale and %-scale columns would otherwise share one
  scale and wash out the smaller-magnitude columns) — every cell's raw number is unaffected.

No composite "classification × consistency" score was invented for this round: the task
instructions explicitly warn against fabricating an undefined composite metric, and the design
doc's own panel plan for this figure (three panels: task-wise heatmap, PHM paired-delta,
cross-dataset delta matrix) does not call for one. Raw M-F1/Smooth/Jump stay independently
traceable in every panel.

## Outputs

- `outputs/fig2_main.png` / `.pdf` / `.svg`

## Validation (see `logs/validation.txt`)

- `taskwise_absolute.csv` has exactly 27 rows (3 tasks × 9 methods); `cross_dataset_absolute.csv`
  dataset set is exactly `{PHM2010, NASA_MILLING, MILLING_CROSS_MACHINE}` with no `MIMII`.
- Panel (a): 3 distinct methods top Acc across D1/D2/D3 (Multi-task TCN-GRU / HTT-Net (adapted) /
  Dynamic GIN + TGP) — confirms target-condition dependence quantitatively, not just visually.
- Panel (b): recomputed PHM D1/D2/D3 paired deltas match the design doc's Appendix A narrative
  numbers within tolerance for all 3 tasks (12 individual `np.isclose` checks).
- Panel (c): recomputed NASA and MTW-CM 3-task-average M-F1/Smooth/Jump benefits match the design
  doc's stated ≈5.86pp / ≈35.0% / ≈10.04pp / ≈23.9% / ≈82.5% figures.

## v2: reference-style visual reconstruction

`plot_fig2_v2.py` produces `outputs/fig2_v2_reference_style.{png,pdf,svg}`. **Statistics are
unchanged from v1** — v2 imports v1's `load()` directly and re-derives every panel's numbers with
the exact same formulas v1 uses (copied verbatim, including all of v1's `np.isclose` validation
assertions), so v2 is independently self-validating against the same headline numbers, not just a
visual restyle of v1's output. Style reference: `reference/reference_mockup_a_cross_condition.png`
and `reference/reference_mockup_b_cross_dataset.png` (see `reference/SOURCE.md` for exactly
what was/wasn't learned from them).

**Layout changes vs. v1:**
- No top figure-level title. A figure-level caption ("鲁棒性" + English subtitle) is centered at
  the bottom of the canvas instead (`_shared/style_v2.py::figure_caption`).
- Each panel's descriptive title moved from *above* to a centered caption *below* it
  (`panel_caption`, or a new local `group_caption()` helper in `plot_fig2_v2.py` for panel (a)'s
  three side-by-side per-task heatmaps, which needed a caption centered under the whole group of
  3 axes rather than under a single axis); only a small bold `(a)`/`(b)`/`(c)` letter remains
  inside the top-left corner of the first panel in each group (`panel_letter`).
- Heatmap colormaps switched from generic `RdYlGn` to the shared custom palette: `BENEFIT_CMAP`
  (sequential cream→gold→teal→navy) for panel (a), `DIVERGING_CMAP` (terracotta↔cream↔teal) for
  panel (c) — same family used across fig1/fig3/fig4/fig5 for one coherent look.
- Panel (a): added a vermillion (DC-PSR's accent color) outline around the DC-PSR row in each of
  the 3 per-task heatmaps, borrowed from the reference mockup's own DC-PSR-row emphasis style —
  makes "where does DC-PSR rank on this task" immediately scannable without reading every cell.
- Panel (b) bar colors switched to the shared method-accent palette (Multi-task TCN-GRU blue,
  teal, gold, DC-PSR vermillion for Smooth benefit) instead of v1's ad hoc blue/green/gold/red.

**Deliberately not copied from the reference mockups:** the cross-dataset mockup's "validation
ladder" schematic panel (a flow diagram, not data-driven) — out of scope for a data figure; its
D2-M failure-boundary dot-whisker panel (d) — v1 intentionally left `D2M_failure_distribution.csv`
unused as noted in v1's README (seed-level detail not called for by the current design doc's Fig.
4-3 panel plan); rank-number badges in heatmap cells (kept v1's simpler DC-PSR-row-outline
approach instead, to avoid cluttering already-dense cells that already carry a raw value); any
number/rank/heatmap value/dataset-name/conclusion visible in either mockup — both predate the
current frozen 9-method / PHM2010+NASA+MTW-CM `paper_data`.

## v3: dense 2×2 dashboard reconstruction (视觉参考效果图/ promoted to primary style reference)

`plot_fig2_v3.py` produces `outputs/fig2_v3.{png,pdf,svg}` using the new `_shared/style_v3.py`
module. **Statistics unchanged again** — v3 imports v1's `load()` verbatim and re-derives every
panel's numbers with v1's exact formulas (all of v1's `np.isclose` checks re-run and pass).

This round demoted `reference/` (the muted academic mockups from the v2 round) and promoted
`视觉参考效果图/` (previously set aside per the user's v2-round decision) as the primary
**layout-only** reference — panel proportions and 2×2 arrangement, never its numbers or its
CNN/ResNet18/TCN/GRU/TCN-GRU/Transformer/DANN/MTL method roster (fictional — this project's real
NASA/MTW-CM comparisons only ever cover Multi-task TCN-GRU vs DC-PSR, per `plot_fig2.py`'s own
`B11`/`B12`-only cross-dataset data).

**Layout, ground-up rebuilt as a strict 2×2 dashboard**, canvas 15.5×10.2in:
- (a) top-left: PHM2010 D1/D2/D3 × 9-method robustness as 3 compact mini-heatmaps
  (Acc/M-F1/Smooth, `BENEFIT_CMAP`), replacing v1's one wide 3-heatmap row.
- (b) top-right: Multi-task TCN-GRU → DC-PSR paired gain across PHM D1/D2/D3 + NASA N1–N4 avg +
  MTW-CM D1-M/D2-M/D3-M + 3-task avg (9 rows total) as a **lollipop/dot-range chart**
  (ΔAcc/ΔM-F1 diamonds+circles, Smooth/Jump benefit squares+triangles), replacing v1's grouped-bar
  panel (b) — direction-unified so "right of zero = improvement" for every marker.
- (c) bottom-left: **new panel**, not in v1/v2 — 3 dataset-profile radar cards (PHM2010/NASA
  Milling/MTW-CM), each comparing ONLY Multi-task TCN-GRU vs DC-PSR (never a fictional
  9-method-per-dataset radar — NASA/MTW-CM were never evaluated with all 9 methods). Radar axes:
  Acc↑, M-F1↑, Consistency↑ (`=1/(1+Smooth)`), Stability↑ (`=1/(1+Jump)`) — explicitly documented
  as monotonic display transforms of the real metrics, not new statistics; raw Acc/M-F1/Smooth/Jump
  stay independently visible in panels (a)/(b)/(d).
- (d) bottom-right: **new panel**, not in v1/v2 — classification-consistency balance map with
  exactly 6 real points (B11 and B12 × PHM2010/NASA Milling/MTW-CM 3-task-avg; asserted
  `n_points == 6` in code), connected pairwise by a thin B11→B12 dashed line per dataset. No
  invented cross-dataset method roster.
- No figure-level title anywhere — not even v2's bottom "鲁棒性" caption. Every panel caption is
  "(a)/(b)/(c)/(d) description" via `panel_container()`, below the panel, in the same nested-
  GridSpec pattern as `plot_fig1_v3.py`.

**Bugs found and fixed while building this:**
1. An index bug in the paired-gain rows list (`rows[5]`/`rows[9]` instead of `rows[3]`/`rows[7]`
   for the NASA/MTW-CM-avg validation checks) — caught immediately by the `assert` failing, fixed
   by re-deriving the correct row order (PHM D1/D2/D3, then NASA avg, then MTW D1/D2/D3-M, then
   MTW avg) before indexing.
2. Long single-line panel captions for (a)-(d) visually overflowed past their own GridSpec column
   into the neighboring panel's space at the default caption fontsize — `panel_container()`'s
   text is correctly *centered* under its own column, but a too-long string still visually spills
   sideways. Fixed by shortening each caption to two explicit lines (`\n`-wrapped) at a slightly
   smaller fontsize (8.6pt) rather than one long line — a caption-length lesson `plot_fig1_v3.py`
   didn't hit (its captions were short enough) but which fig3/4/5 should watch for with any wide,
   information-dense caption text.
3. `△` (U+25B3, used in panel (d)'s legend label text) is missing from the Arial font used
   throughout — matplotlib printed a glyph-missing warning and silently dropped the character.
   Fixed by describing marker shapes in plain words ("... (triangle)") in legend text instead of
   embedding a Unicode shape glyph, and reserving actual triangle/square/circle shapes for the
   marker artists themselves (which render as vector paths, not font glyphs, so they were never
   affected).

**Deliberately not copied from `视觉参考效果图/`:** its "任务级迁移鲁棒性热图" showing all 9
methods on PHM/NASA/MTW-CM alike (real data only supports that breadth for PHM2010 — NASA/MTW-CM
are B11-vs-B12-only); its 8-fictional-method legend (CNN/ResNet18/TCN/GRU/TCN-GRU/Transformer/
DANN/MTL); its specific percentage numbers in panel (b); its "高平衡（理想区）" callout box text in
panel (d) (kept the balance *map* idea, dropped the fabricated-conclusion callout box).

## Open issues (v3)

- Same font-size-at-print-scale caveat as fig1_v3: dense at native full-page-thesis size, would
  need enlarging before a strict journal double-column submission.
- Panel (c)'s `1/(1+x)` consistency/stability transform is a reasonable, monotonic, bounded-(0,1]
  display choice but is not a metric used anywhere else in the paper — call out explicitly in any
  caption/text that references panel (c) so readers don't mistake it for a new evaluation metric.

**Note on a second, later-arriving reference set**: after this v2 build was finished, a folder
`视觉参考效果图/` appeared in every `figX/` directory (AI-generated dashboard-style mockups, bright
saturated palette, top banner title, icon badges, highlighted conclusion boxes). Its top-banner
convention directly conflicts with this round's explicit "no top title" rule, and its own method
roster here is fictional (8 generic baselines like CNN/ResNet18/Transformer/DANN, not this
project's real 9-method scheme) — reinforcing that it is style inspiration at most. Asked the user
directly whether to rework all 5 figures to match its brighter dashboard aesthetic; they confirmed
keeping the current academic-journal style. No changes made as a result.

**Bug found and fixed while building this** (same class of bug fig1_v2 first caught): `GridSpec`
margins (`left`/`right`/`top`/`bottom`) are set directly in the constructor, never via a later
`fig.subplots_adjust()` call, so every `panel_caption()`/`group_caption()` position (computed from
`ax.get_position()`) reads the final layout, not a pre-reflow one. Also found and fixed: panel
(b)'s legend at `loc="upper left"` collided with the "b" panel letter in the same corner — moved
to `loc="upper right"` where the bars are shorter.

## Open issues

- `D2M_failure_distribution.csv` and `cross_machine_task_deltas.csv` (both present in
  `07_figure_ready/fig3/`) were inspected but not used: the former is seed-level failure-mode
  detail not called for by any panel in the design doc's Fig. 4-3 plan, and the latter is a subset
  of `cross_dataset_deltas.csv` restricted to MTW-CM rows. Available for a future supplementary
  panel if reviewers ask for seed-level failure breakdown.
