# Fig.5 — Shared latent representation geometry and joint evolution (paper Fig. 4-6)

## Figure purpose

The second "hero" figure. Answers: does DC-PSR's internal 64-D shared representation actually
encode continuous degradation structure, or does it just form three disconnected clusters; do
stage, `q`, and uncertainty admit a consistent geometric reading of the same latent space; and how
do stage probability, degradation position, and prediction confidence jointly evolve across one
tool lifecycle.

## Input files

- `paper_data/07_figure_ready/fig5/hidden_representation.csv` (304 rows × 88 columns) — the
  frozen 64-D shared hidden representation (`h_00`..`h_63`) plus `true_stage`, `pred_stage`,
  `q_true`, `q_hat`, `p_E/M/L`, `uncertainty`, `entropy`, `misclassified`. This is already the
  frozen representation; **no network is re-run** to produce it.
- `paper_data/07_figure_ready/fig5/lifecycle_semantics.csv` (304 rows) — `relative_life`,
  `prob_early/middle/late`, `max_prob`, `q_pred`, used for panels (d)/(e).

See `inputs_manifest.csv` for row/column counts and SHA-256 of each file as read.

## Plot script

`plot_fig5.py` — run with:

```
python paper_data/figure/fig5/plot_fig5.py
```

### PCA methodology (panels a/b/c)

sklearn is not installed in this environment, so PCA is implemented directly via numpy SVD
(`_shared/data_utils.py::pca_2d`). **One** PCA is fit on the 64-D representation; the same 2D
`(PC1, PC2)` coordinates are reused for all three panels — only the point color changes. PC1+PC2
explain 98.7% of variance (PC1=60.7%, PC2=38.0%) on this run.

- (a) colored by **true stage** (Early/Middle/Late).
- (b) colored by **q_true** (continuous) — same coordinates as (a).
- (c) colored by **uncertainty** (continuous) — same coordinates as (a)/(b); the 3 misclassified
  samples (`misclassified==1`) are outlined with a black ring.

The resulting geometry is a single continuous curved ("boomerang") manifold, not three
disconnected clusters — Early and Late sit at the two arm-tips, Middle at the vertex, and in
panel (b) the q-color gradient flows continuously along the arm direction rather than jumping
discretely between clusters.

### Panels (d)/(e): why ridge-lines/trajectories, not an interpolated surface

Both panels plot the 304 real observations directly (3D line + scatter), not a `plot_surface`
built from grid-interpolated values. Reason: with only one z-value per real `(x, stage)` or
`(x, y)` combination, a literal continuous surface would require inventing values between real
samples along an axis (stage identity, or the `(life, q_pred)` plane) where interpolation is not
scientifically justified by the task's own instruction against fabricating trends. Ridge-lines
(d) and a colored 3D trajectory + scatter (e) give the same "joint evolution" reading the design
doc asks for while keeping every plotted value traceable to one of the 304 test runs.

- (d) Three stage-probability ridge lines (Early/Middle/Late) over relative life, each filled down
  to zero as a ribbon in its own y-plane — directly shows the sequential dominance
  Early→Middle→Late.
- (e) A single 3D trajectory `(relative_life, q_pred, max_prob)`, colored by predicted stage, with
  a dashed grey floor projection of the `(life, q_pred)` path for spatial context.

## Outputs

- `outputs/fig5_main.png` / `.pdf` / `.svg`

## Validation (see `logs/validation.txt`)

- `hidden_representation.csv` and `lifecycle_semantics.csv` each have exactly 304 rows.
- Exactly 64 `h_*` columns found and used for PCA (asserted).
- Single PCA fit confirmed reused across panels a/b/c (by construction — `scores` computed once
  and passed to all three panel functions).
- 3 misclassified samples identified and outlined in panel (c) (from the `misclassified` column,
  not manually selected "interesting" outliers).
- Panel (e) explicitly logs that no grid interpolation was used.

## v2: reference-style visual reconstruction

`plot_fig5_v2.py` produces `outputs/fig5_v2_reference_style.{png,pdf,svg}`. **Statistics are
unchanged from v1** — v2 imports v1's `load()` and `fit_pca()` directly, so it is the exact same
64-D representation and the exact same single numpy-SVD PCA fit reused across panels a/b/c; only
the visualization layer changed. Style reference:
`reference/reference_mockup_partial_panel_d_only.png` — **only its panel (d)** is relevant (see
`reference/SOURCE.md`); this project has no existing mockup for the 3D surface panels, so those
were designed fresh using the navy/teal/gold palette shared across all 5 figures.

**Layout changes vs. v1:**
- No top figure-level title; figure-level caption "表示几何" + English subtitle centered at the
  bottom.
- Panel captions moved below each panel; small bold `(a)`–`(e)` letters kept in-panel (including
  the two 3D panels, via `panel_letter`'s `text2D` path).
- Panels (a)/(b)/(c): added a **dual visual encoding** — marker *shape* now encodes true stage
  (circle/triangle/square) in addition to color, directly matching the reference panel (d)'s own
  caption ("marker shape encodes the true stage"); added a thin dashed grey connector line
  threading through the points in `q_true` order, matching the reference's visual "manifold
  thread" device. Panel (a) additionally uses stage color (redundant with shape there, useful
  contrast for (b)/(c) where color instead carries q/uncertainty).
- Colors switched from `viridis`/`magma_r`-only to the shared `DEGRADATION_CMAP`
  (navy→teal→gold) for panel (b), keeping `magma_r` for uncertainty in panel (c) since that is a
  genuinely different quantity and borrowing the degradation palette there would be misleading.
- Panels (d)/(e): kept v1's ridge-line / real-trajectory design (no interpolated mesh — see v1's
  README for why), restyled with the shared palette and bottom captions.

**Deliberately not copied from the reference mockup:** its specific PC1/PC2 point positions,
variance-explained percentages (recomputed independently in v2, values differ slightly run-to-run
only in floating point, not in substance), and its 2-panel-only scope — v2 uses 5 panels because
the task brief explicitly asks for stage/q/uncertainty views *plus* two 3D surfaces, which the
mockup's single panel (d) does not cover.

**Bug found and fixed while building this**: a stray leftover `linewidths(1.3) if False else
linewidths(1.3)` fragment from an earlier edit pass was a Python syntax error caught immediately
on first run (not a layout bug) — fixed to the correct `linewidths=1.3` keyword argument before
the first successful run.

**Note on a second, later-arriving reference set**: after this v2 build was finished, a folder
`视觉参考效果图/` appeared in every `figX/` directory (AI-generated dashboard-style mockups, bright
saturated palette, top banner title, icon badges, highlighted conclusion boxes; its fig5 copy shows
a dense continuous "U-shaped" point cloud with far more than 304 points and full interpolated 3D
surfaces — this project's real data is exactly 304 runs and v1/v2 deliberately avoid fabricating
an interpolated surface for that reason, see above). Asked the user directly whether to rework all
5 figures to match its brighter dashboard aesthetic; they confirmed keeping the current
academic-journal style. No changes made as a result.

## v3: dense landscape reconstruction, Python(data)+MATLAB(3D render) split

Unlike fig1-4's pure-Python v3 builds, fig5 v3 is split across two files because the brief calls
for stronger 3D visual quality than `mpl_toolkits.mplot3d` gives (see fig1-4's v3 READMEs for the
shared layout rules/bugs this build also follows: GridSpec-equivalent margins set at construction,
`hspace`-not-`caption_height` for tick-label clearance, captions below not above every panel, no
figure-level title anywhere).

- **`prepare_fig5_v3.py`** (Python): loads the exact same real data v1 uses — `load()` and
  `fit_pca()` imported directly from `plot_fig5.py`, so it is the same 304×64
  `hidden_representation.csv`, the same numpy-SVD PCA fit (confirmed identical explained variance
  to v1/v2: PC1=0.607, PC2=0.380) — and exports three derived, fully real, non-fabricated CSVs for
  MATLAB to read: `derived/pca_scores_v3.csv` (304 rows: PC1/PC2/true_stage/pred_stage/q_true/
  q_hat/uncertainty/entropy/misclassified), `derived/stage_ridges_v3.csv` (304 rows, sorted by
  `relative_life`: prob_early/middle/late from `lifecycle_semantics.csv`), and
  `derived/confidence_trajectory_v3.csv` (304 rows, sorted by `relative_life`: q_pred/max_prob/
  pred_stage). Validated row counts, column counts, and zero NaNs; log in
  `logs/validation_v3_python.txt`.
- **`plot_fig5_v3.m`** (MATLAB, run via
  `"C:\Program Files\Polyspace\R2021a\bin\matlab.exe" -nosplash -nodesktop -batch "cd('<path>\paper_data\figure\fig5'); plot_fig5_v3"`):
  reads the 3 derived CSVs only — never refits PCA, never regenerates or interpolates points.
  `tiledlayout(2,6)`, landscape `15.5×10.2in`: (a) stage-colored PCA / (b) q-colored PCA /
  (c) uncertainty-colored PCA share identical PC1/PC2 axis limits (computed once, applied to all
  three, confirmed in `logs/validation_v3_matlab.txt`); (d) stage-probability 3D ridge ribbons /
  (e) life×q_pred×confidence 3D ribbon span the bottom row. Stage colors are the exact same hex
  values as `_shared/style_v2.py`'s `STAGE_COLORS` (`#1B3A5C`/`#2A8C7A`/`#D9A441`) for cross-figure
  consistency. `set(gca,'Color','none')`, thin light-grey grid, hand-picked `view(-48,26)`,
  `camlight('headlight')`, `lighting gouraud`, `material dull` — no default grey 3D panes.
  Captions use `annotation('textbox', ...)` positioned from each axes' `.Position` (normalized
  figure units) read only after `drawnow`, never `title()` (which MATLAB places above the axes).

**Ribbon/ridge extrusion is visual-only, stated explicitly in-figure and here**: panels (d) and (e)
give the real 1-D trajectories (stage probability vs. relative life; confidence vs. life vs.
q_pred) a narrow perpendicular extrusion purely so they read as a surface at a glance — panel (d)'s
stage-axis ribbon width and panel (e)'s q-direction ribbon width carry **no quantitative meaning**
and must never be interpreted as a measured second dimension. Every z-value plotted is real; the
extrusion direction is not.

**Bugs found and fixed while building this:**
1. MATLAB hex-literal color arrays (`[0x1B 0x3A 0x5C]`) default to `uint8`, which breaks
   `linspace`'s internal division when building the custom colormap — fixed with explicit
   `double([27 58 92])`.
2. `clim(ax, ...)` does not exist in MATLAB R2021a (added in R2022a) — replaced with the
   R2021a-compatible `caxis(ax, ...)`.
3. Forcing `pbaspect(ax, [range(xl) range(yl) 1])` on panels (a)/(b)/(c) to match the data aspect
   ratio shrinks the *rendered* plot box inside `ax.Position` without updating `.Position` itself
   — since `add_caption_below()` reads `.Position` to place captions, this created a large dead
   whitespace band between the shrunk plots and their (correctly-positioned-for-the-unshrunk-box)
   captions. Fixed by dropping the aspect-ratio constraint entirely; identical `xlim`/`ylim` across
   the three panels already gives visual comparability without this side effect — the same root
   cause (decorations/constraints outside an axes' literal box are invisible to layout math) as
   fig1-4's `hspace`-vs-`caption_height` bug, just MATLAB's version of it.

**Deliberately not copied from `视觉参考效果图/fig5`'s mockup**: its thousands-of-points dense point
cloud (real data is exactly 304 samples); its fictional multi-"domain" marker-shape legend (this
project's C6 test set is a single condition, no domain groups exist); its fully-interpolated 3D
surfaces for panels (d)/(e) (replaced with the real-trajectory-plus-visual-ribbon approach above,
consistent with v1/v2's documented refusal to fabricate an interpolated measurement surface).

## v4: publication-grade rework — the round's centerpiece figure

`prepare_fig5_v4.py` + `plot_fig5_v4.m` produce `outputs/fig5_v4.{pdf,svg}`, `fig5_v4_600dpi.png`,
and `fig5_v4_paper_preview.png`, at true 178×132mm master physical size. Full rationale:
`paper_data/figure/V4_DESIGN_AUDIT.md`. Detailed scoring: `VISUAL_QA_V4.md` (status: **DONE**,
scientific faithfulness 10/10).

**Two real content changes this round** (not just restyling):

1. **Panels (a)/(b)/(c) now read `_shared/derived/shared_pca_scores_v4.csv` directly** (via a
   relative path from the MATLAB script, `../_shared/derived/shared_pca_scores_v4.csv` — not a
   local copy, so there is zero risk of drift), instead of `prepare_fig5_v4.py` fitting its own
   PCA as v3 did. This is the *same* file `paper_data/figure/fig4/plot_fig4_v4.py`'s panel (d)
   reads, built once by `_shared/prepare_shared_pca_v4.py` with a deterministic sign convention
   (`corr(PC1, q_true) > 0`). Fig.4 and Fig.5 now provably show geometrically identical latent
   geometry — verified by inspection: the "boomerang" manifold shape in this figure's panels
   (a)/(b)/(c) matches `fig4_v4`'s panel (d) exactly.

2. **Panels (d)/(e) substantially reworked**, per the brief's explicit "too thin, too much like a
   simple ribbon" critique of v3:
   - **(d) stage-probability ridge curtains** (not 2-point-wide ribbons): 21 y-samples per stage
     spanning a ±0.30 visual half-width around each stage's y-level (Early=0, Middle=1, Late=2).
     Every cross-curtain sample at a given x shares the *exact same real* `Z = p_stage(x)` value —
     the y-width is a pure visual extrusion, never a fabricated second dimension (asserted in
     `logs/validation_v4_matlab.txt`). Real 304-point trajectories are PCHIP-interpolated to ~800
     display vertices for rendering smoothness only (documented, not baked into any exported CSV);
     real per-run markers every 12 runs stay visible on top of each curtain to keep the smoothing
     auditable against the underlying observations. The floor (z=0) carries a **real
     probability-mixture color strip** — `pE·Early_color + pM·Middle_color + pL·Late_color`,
     per real x, normalized (since pE+pM+pL=1 this is a true convex blend, not an invented
     texture) — plus a **dominant-stage transition line** from real `argmax(p_E, p_M, p_L)` (this
     specific choice over `true_stage`, documented here: argmax of the *predicted* probabilities
     is what the ridge curtains themselves visualize, so the transition line stays consistent with
     what's actually plotted above it, rather than mixing predicted-probability curtains with a
     ground-truth-derived floor line).
   - **(e) uncertainty-driven confidence ribbon**: ribbon half-width is `w_min + u_norm·(w_max −
     w_min)` where `u_norm = (uncertainty − min)/(max − min)` is real per-run uncertainty from
     `hidden_representation.csv`, joined to the lifecycle trajectory 1:1 by `run_id` in
     `prepare_fig5_v4.py` and **validated as an exact 304↔304 join** before being trusted (asserted
     in `logs/validation_v4_python.txt`). Visual width range ≈0.015–0.060×range(q_pred) — this
     width has **no physical q-magnitude meaning**, stated explicitly in the in-figure caption
     itself ("no physical q-meaning") as well as here. Height (`Z`) is always the real
     `max_prob(x)`, shared identically across the ribbon's width — uncertainty drives *only* the
     width, never the height. Face color by real `max_prob`, using a deliberate purple→teal→yellow
     colormap (not MATLAB's default `jet`/`parula`). Thick white center trajectory + thin dark
     outline over the real 304-point path, real markers every 17 runs, a real floor projection of
     `(relative_life, q_pred)` colored by `max_prob`, and real vertical stems from floor to surface
     every 28 runs. **No `Pmax=0.8` threshold plane** — the method doesn't use that threshold, and
     the brief explicitly says to omit it in that case.
   - Camera/lighting: `view(-52, 25)`, `camproj('perspective')`, `pbaspect([1.7 1.0 0.95])`,
     `camlight('headlight')` + a weak second `camlight('left')`, `lighting('gouraud')`,
     `material('dull')`, transparent axes background (`Color='none'`), light thin grid — matching
     the brief's recipe; view angle chosen from the brief's suggested range after comparing
     `(-52,25)`/`(-58,27)`/`(-45,23)` renders.

**True-physical-size bugs found and fixed** (3 rounds, MATLAB-specific variants of the same bug
class documented across fig1-4's Python builds):
1. Captions for panels (a)/(b)/(c) initially collided with their own "PC1" x-axis label text —
   `add_caption_below`'s `gap` (inherited from v3, `0.026`) was tuned for a taller v3 canvas and
   didn't clear 2D axis-label text at this round's more compact layout. Fixed by raising to `0.075`.
2. That fix then overshot: with `TileSpacing='compact'` (inherited from v3), the tiledlayout left
   almost no real space between row 1 and row 2, so row-1 captions at the larger `gap` collided
   with row-2's *own* captions instead (annotation() overlays aren't part of tiledlayout's spacing
   accounting, so they can only occupy whatever space physically happens to be there). Fixed by
   switching `TileSpacing` to `'loose'`, which creates real inter-row space, combined with settling
   on a more moderate `gap=0.058`.
3. Both fixes needed to be verified together on the actual `paper_preview.png` render — neither one
   alone was sufficient, and the first (gap increase) actively made things worse until paired with
   the second (TileSpacing increase). Recorded as a specific caution: a spacing fix validated in
   isolation can still fail once its side effects on a *different* geometric constraint are
   accounted for; always re-render and re-view after each change, not just reason about it.

**Deliberately not copied from `视觉参考效果图/fig5`**: its multi-thousand-point dense cloud (real
data is exactly 304 C6 test runs); its fully-interpolated 2D-sampled 3D surfaces in (d)/(e) (this
project's real observations are 1-D trajectories over relative life — a literal measured surface
would fabricate a second experimental dimension that was never collected); any of its Spearman/
R²/confidence numbers.

## Open issues (v3, retained for history)

- Panel (d)'s "Early" y-axis tick label sits close to (though does not clearly overlap) its
  caption below — MATLAB 3D axes' tick/label decorations extend beyond `ax.Position`'s nominal box
  in a way that is hard to fully predict, the same general class of issue as fig1-4's `hspace`
  fix, just closer to the edge of acceptable here. Not iterated further this round given
  diminishing returns per ~45s MATLAB round-trip; flagged for a future polish pass.
- SVG export from MATLAB (`print(fig,...,'-dsvg')`) succeeded and is included, but MATLAB's SVG
  backend is generally less mature than matplotlib's — prefer the PDF for print/vector use.
- There is a large vertical gap between the top row (panels a/b/c) and the bottom row (panels
  d/e). This is a `mpl_toolkits.mplot3d` quirk, not a `GridSpec` spacing bug: `Axes3D` reserves a
  fixed internal margin around its 3D bounding box regardless of the GridSpec cell it's placed in,
  so tightening `hspace` further has limited effect. Purely cosmetic; not attempted further this
  round given the "correctness over polish" priority for this task, but flagged for a future pass
  (e.g. via `ax.set_box_aspect` tuning or switching the 3D backend).

- Panels (a)/(b)/(c) intentionally overlap in subject matter with Fig.4's simplex panel (both show
  an ordered Early→Middle→Late geometric structure) but in genuinely different spaces — Fig.4's
  simplex is the raw 3-class probability space, Fig.5's PCA is the 64-D shared hidden
  representation. Caption language in the manuscript should make this distinction explicit to
  avoid readers perceiving the two hero figures as redundant.
- 3D panels (d)/(e) are matplotlib's default 3D renderer (not plotly); viewing angle is fixed at
  `elev=22, azim=-60` for the static PNG/PDF/SVG export. If an interactive version is later wanted
  for a supplementary HTML figure, the same 304-row data supports it directly.
