# Figure Refinement Audit — `paper_data/New_figure/`

Scope: this round is **layout/visual refinement only** — data, panel content, and the experimental
narrative established in `FIGURE_REBUILD_AUDIT.md` are frozen and not revisited. This document
audits the four already-approved first-pass figures against the new CIE-submission-grade
requirements (outer border, block borders, tightened whitespace, unified caption/font/color
system, fixed final filenames) and lays out the per-figure refinement plan before any code changes.

## 0. Current state summary (all four previously built and approved as first-pass drafts)

| Figure | Canvas (mm, W×H) | Rows | Outer border | Block borders | Caption position | Font | Status |
|---|---|---|---|---|---|---|---|
| Fig4-2 主比较 | 178×158 | 3 (a/b/c \| d \| e1-e3) | none | none | below panel, centered ✓ | Times New Roman ✓ | approved, needs border+tightening |
| Fig4-3 鲁棒性 | 178×140 | 2 (a-heatmaps \| b + c1/c2) | none | none | below panel, centered ✓ | Times New Roman ✓ | approved, needs border+tightening |
| Fig4-4 消融实验 | 178×232 | 4 (a/b \| c \| d1/d2 \| e) | none | none | below panel, centered ✓ | Times New Roman ✓ | approved, most whitespace of the three "regular" figures |
| Fig4-5 退化语义与表示几何 | 178×255 | 4 (A \| B \| C/D \| E) | none | none | below panel, centered ✓ | Times New Roman ✓ | approved, longest canvas, loosest block cohesion, priority target |

All four already share: `New_figure/_shared/style.py` (`apply_style()`, `STAGE_COLORS`,
`METHOD_COLORS`, `ABLATION_COLORS`, `add_axis_arrows`/`style_axis`, `panel_caption_below`,
`CONFUSION_CMAP`, `Q_CMAP`/`U_CMAP`, `save_all()`) and `New_figure/_shared/data_utils.py`. This is
good news: the color/font system is **already mostly unified** (verified below) — the main work
this round is geometric (borders, spacing, block cohesion), not a color/font redesign.

## 1. Color-system consistency check (already largely unified, confirmed here not re-derived)

- **Stage colors**: `STAGE_COLORS = {early: #1B9E77, middle: #E6A01A, late: #C44E52}` — defined once
  in `_shared/style.py`, imported and used identically in Fig4-2 (panel legends reference stage
  concepts only indirectly), Fig4-4 panel (c)'s p_E/p_M/p_L lines, and Fig4-5 panels A/B/e2. **No
  divergence found.**
- **Method colors**: `METHOD_COLORS["Multi-task TCN-GRU"] = #0072B2` (blue), `METHOD_COLORS["DC-PSR"]
  = #C44E52` (warm red) — defined once, used identically in Fig4-2 (panel a/b/c/e legends), Fig4-3
  (panel c dumbbell markers). **No divergence found.**
- **Ablation colors**: `ABLATION_COLORS` = A1 `#B7BDC2` (light neutral) → A2 `#93A6B8` → A3
  `#6E93A8` (still muted/neutral) → A4 `#0072B2` (blue, fusion) → A5 `#D55E00` (orange-red,
  strongest ordering) → A6 `#009E73` (teal, final) — already exactly matches this round's requested
  emphasis pattern (A1–A3 restrained, A4/A5/A6 distinct). **No change needed.**
- **Confusion-matrix / heatmap colormap**: `CONFUSION_CMAP` (white→cyan→blue→purple→red, ported
  from `代码/8.2图9.py`) used identically in Fig4-2 panel (d) and Fig4-3 panel (a). **Consistent.**

**Conclusion**: §4.5 of the brief ("配色语义统一") is **already satisfied**. This round's actual
color-related work is limited to Fig4-5's requested "block label" blue-gray tone (new, small) and
verifying no figure has silently drifted (final QA step, not a redesign task).

## 2. Font/caption-hierarchy consistency check

- All four figures call `st.apply_style()` (Times New Roman + STIX mathtext, `font.size=8.5`,
  `axes.labelsize=8.7`, `xtick/ytick.labelsize=7.6`, `legend.fontsize=7.5`) from the same module —
  **no per-figure font override found** in any `panels.py`/`assemble.py` except deliberate small
  panel-specific reductions (e.g. Fig4-5's dense 2D scatter panels at 6.2–6.8pt, Fig4-4's mechanism
  strip at 5.6–8.0pt) which are legitimate density-driven exceptions, not accidental drift.
- All panel captions already use `st.panel_caption_below()` (below-panel, centered) — **the
  brief's §4.4 hard requirement is already met in all four figures**, confirmed by re-reading every
  `panels.py`/`assemble.py` caption call. No panel has an above-axes title anywhere.
- No figure has a top-level figure title (`fig.suptitle` is never called in any `assemble.py`) —
  **§4.4's "no giant top title" requirement already met.**

**Conclusion**: font hierarchy and caption placement need no structural fix. This round's font-related
work is limited to the outer-border/block-border label text (new elements only).

## 3. What is genuinely missing / needs work (the real refinement scope)

### 3.1 Outer border — missing in all four (new work, all four figures)
No figure currently draws a bounding rectangle around the full canvas. `_shared/style.py` has no
`add_outer_border()` helper yet. **Action**: add one shared function (rounded rect, `#4A4A4A` or
similar neutral dark gray, `linewidth≈0.9-1.1pt`, no fill, no shadow) and call it once per
`assemble.py` as the very last drawing step (so it is not overdrawn by any panel).

### 3.2 Block borders — missing in all four (new work, all four figures)
No figure currently groups its rows into a labeled, bordered "block." Each `assemble.py` currently
uses bare `fig.text()` group captions (e.g. Fig4-2's "(d) Representative confusion matrices...",
Fig4-4's "(c) Probability-state formation...") with no visual container. **Action**: add a shared
`add_block_border(fig, bbox, label=None)` helper (very light gray/blue-gray rectangle, rounded,
optional small bold label in the corner) and wrap each figure's logical blocks per §6-9 of the
brief's per-figure block plans (below).

### 3.3 Whitespace — present in all four, worst in Fig4-4 and Fig4-5 (confirmed by re-opening each)
- **Fig4-2**: moderate. Row gaps (`hspace=0.62` at 158mm height) are functional but not tight;
  panel (b)'s Pareto scatter has real empty space in its upper-right quadrant (no data there,
  expected, not a bug) but the axes box itself could shrink slightly. Least urgent of the four.
- **Fig4-3**: moderate. `hspace=0.95`-equivalent row gap between block I (heatmaps) and block II
  (bars+dumbbells) is generous; column (b)'s bar chart has real empty space above the tallest bar
  (Jump-benefit ~82) that's inherent to the data range, not fixable without misleading axis
  compression — flag as acceptable, not a defect.
  block already the tightest-organized of the four.
- **Fig4-4**: significant. Figure height grew to 232mm across this round's iteration specifically
  to solve caption/legend collisions (documented in its own README §10/§12) by adding vertical
  gap rather than tightening geometry — exactly the anti-pattern this round's brief warns against
  ("不要仅仅在 LaTeX 中缩小整张图... 让图内部的 scientific content 占据更多 canvas"). The
  mechanism-progression strip (e) in particular has a large blank area between its module row and
  its caption. **Primary target for height reduction.**
- **Fig4-5**: worst. 255mm tall, four blocks with generous `hspace=0.68` and additional per-block
  `fig.text()` offsets tuned to avoid collisions (documented in its own README §9) rather than
  tightened geometry. The 3D panels (C/D) have a large blank gap between their plotted content and
  their captions, explicitly flagged as an open item in that figure's own README §9. **Highest
  priority for this round**, exactly as the user's brief states.

### 3.4 Cross-panel geometric consistency (new checks, not previously enforced)
- Fig4-2 panel (d)'s 4 confusion matrices: already equal-sized (same `imshow` aspect, same
  GridSpec column width) — **no fix needed**, contrary to a possible assumption; verify only.
- Fig4-3 panel (a)'s 3 heatmaps: already equal width (`width_ratios=[1,1,1,0.07]`) — **no fix
  needed**, verify only.
- Fig4-4 panel (c)'s 4 small multiples (A1/A4/A5/A6): currently each has its **own** legend call
  only on the first axes already (`show_legend=(i==0)` in `panel_c()`) — §8.3's "only one legend on
  the leftmost panel" requirement is **already met**; real remaining work there is tightening
  `wspace` and enforcing identical y-limits (currently `sharey=True` in preview but the assembled
  composite does not explicitly share y — verify and fix if divergent).
- Fig4-5 blocks A/B: already use `_set_same_limits()` per row (each row internally consistent) but
  **rows A and B do not share limits with each other** (raw-feature PCA coordinates and shared-
  representation PCA coordinates are on genuinely different numeric scales, so identical limits
  are not meaningful here — this is a scope decision, not a bug; documented, not silently fixed).

### 3.5 Final filenames — need renaming (new work, all four figures)
Current: `Fig4_2_main_comparison.pdf`, `Fig4_3_robustness.pdf`, `Fig4_4_ablation.pdf`,
`Fig4_5_semantics_geometry.pdf`. Required: `fig4_2_main_comparison.pdf`, `fig4_3_robustness.pdf`,
`fig4_4_ablation.pdf`, `fig4_5_degradation_representation.pdf` (note: Fig4-5's basename changes,
not just case). **Action**: add a fixed-name export as an additional `save_all()` call (or copy)
in each `assemble.py`, written to a top-level location alongside where the main `.tex` file will
live — since that location is not yet established in this repo, write them to
`paper_data/New_figure/final_pdf/` for now and flag the true final destination as a later,
non-figure-drawing task (moving files next to the `.tex` source is a submission-packaging step,
out of scope for this drawing round).

## 4. Per-figure refinement plan (execution order, per the brief's explicit sequencing)

1. **Fig4-2** (layout refinement): add outer border; group into 2 light-bordered blocks (top:
   a/b/c: overall/Pareto/CI; bottom: d/e: confusion matrices + diagnostics); tighten row `hspace`;
   verify confusion-matrix/diagnostic sizing (already consistent, confirm only); re-export fixed
   filename.
2. **Fig4-3** (layout refinement): add outer border; group into 2 blocks (Block I: D1/D2/D3
   heatmap landscape; Block II: paired-change bar + task-level dumbbells); tighten the block-to-
   block gap; align M-F1/Smooth dumbbell axis styling (already close, verify); re-export fixed
   filename.
3. **Fig4-4** (deeper layout refinement): add outer border; reorganize into 3 blocks (Block I:
   a+b performance; Block II: c probability-state formation, 4-panel shared-block with single
   legend + shared y-limits enforced; Block III: d1+d2+e variation/mechanism); rebuild panel (e) as
   a tighter, more formal chevron strip (still chevrons — already redesigned last round — but
   reduce the strip's own vertical padding and tie it geometrically closer to Block III rather than
   floating with a large gap); reduce total canvas height by removing the "solve collisions by
   adding blank space" pattern in favor of geometric fixes; re-export fixed filename.
4. **Fig4-5** (deeper layout refinement, highest priority): add outer border; formalize the
   existing A/B/C/D block structure with actual light blue-gray bordered containers and small
   corner block labels (currently only bare `fig.text()` group captions with no container); tighten
   inter-block spacing significantly (this figure has the most reclaimable whitespace of the four);
   enlarge the semantic block (e1/e2) proportionally since it is currently the smallest block
   relative to its scientific importance; tighten the 3D panels' caption gap; re-export fixed
   filename. Re-attempt or confirm-keep the Python 3D rendering per §9.3's MATLAB-if-needed clause
   (assessed during that figure's own refinement pass, not pre-decided here).

## 5. What this round explicitly does NOT do (guardrails, restated)

- No data recomputation, no new panels, no dropped panels, no re-ranking of methods/configurations.
- No change to any headline number, confidence interval, or statistical claim.
- No change to which figure answers which scientific question.
- Interpolation/envelope disclosures already present in Fig4-5's README/legends are preserved
  verbatim in meaning; only their visual presentation (spacing, ridge prominence, transparency) may
  be tuned per §9.3.

## 6. Shared style additions needed before any figure is touched (Step 2, next)

To be added to `New_figure/_shared/style.py` (not a new file — extending the existing one, per the
brief's "avoid four figures each writing different style code"):
- `add_outer_border(fig, pad_pt=2, color="#4A4A4A", lw=1.0, rounding=0.02)`
- `add_block_border(fig, bbox_axes_fraction, label=None, color="#B9C2CC", lw=0.8, rounding=0.03,
  label_color="#3A5068")`
- `save_all_fixed_name(fig, out_dir, fixed_basename)` — thin wrapper writing exactly the required
  final `.pdf` (and PNG/SVG) alongside the existing versioned outputs, never replacing them.

Implemented next, then applied figure-by-figure in the order fixed in §4.
