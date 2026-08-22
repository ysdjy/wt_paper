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

## Open issues

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
