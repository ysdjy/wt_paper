# Fig.5 v5 — Visual QA (panel-first, standalone-before-composed)

This round's mandated workflow was followed literally: each of the 5 panels was rendered
standalone first (`outputs/panel_{a,b,c,d,e}_preview.png`), viewed with the Read tool, compared
against `视觉参考效果图/ChatGPT Image ... (5).png` (layout/style only — its point density, exact
numbers, and fabricated surfaces were never copied), concrete gaps written down, fixed, and
re-rendered — multiple rounds for panels (d)/(e) specifically, including a 5-camera-angle
comparison for each before the final composition was assembled.

## Panel (d): stage-probability structure — gaps found vs. reference, and fixes

The v4 baseline (`outputs/fig5_v4_600dpi.png`) was reviewed first as the "before."

1. **Gap**: v4's ridges were flat 2-Y-sample-wide curtains — under directional lighting a flat
   curtain has no curvature, so it reads as a thin painted card, not a solid object.
   **Fix**: each ridge rebuilt as a solid volume — a real-valued flat top cap (Y-width 9 samples,
   still purely visual extrusion, every sample at a given X sharing the identical real
   `p_stage(x)`) PLUS two vertical side walls (geometric drops from that real top value to the
   floor, no new measured value) PLUS end caps. The side walls pick up markedly different light
   than the top face, which is what actually reads as "solid" in the final render.
2. **Gap**: v4's floor strip was thin and low-contrast; the reference's floor treatment carries
   real visual weight.
   **Fix**: kept the real probability-mixture floor color blend (`pE·Early+pM·Middle+pL·Late`)
   but widened it and added the real `argmax(prob)` dominant-stage transition line on top of it,
   giving the floor an active role instead of a passive backdrop.
3. **Gap**: v4's single camera angle (`az=-52,el=25`) partially occluded the Early ridge behind
   Middle/Late from most viewing directions.
   **Fix**: rendered and compared 5 candidate angles side by side
   (`outputs/panel_d_camera_trials/angle_{1..5}_az*_el*.png`); `az=-35, el=35` gives the cleanest
   simultaneous view of all three ridges' full height, their side-wall shading, and the floor
   strip, with the least occlusion between stages.
4. **Gap**: v4 left a lot of unused canvas margin around the 3D content relative to its panel
   allocation.
   **Fix**: in the final composition, panels (d)/(e) are given explicit, generous `Position`
   rectangles (not a `tiledlayout` tile, which in this MATLAB version refuses direct `Position`
   writes on its children — confirmed by a hard error when first attempted) and the fixed
   `pbaspect` constraint used in v3/v4 was dropped for these two panels specifically, letting the
   3D content expand to fill its allocated rectangle rather than being boxed to an arbitrary
   width:height ratio.
5. **Gap**: real per-run markers existed in v4 but were easy to lose against the thin ribbon;
   with a wider, higher-contrast solid ridge they needed re-checking for visibility.
   **Fix**: kept markers every 12 real runs on the real center-ridge line (white-filled, stage-dark
   edge) — now clearly visible against the higher-contrast solid surface, still directly
   traceable to the underlying 304 observations.

All Z-values used for the top cap and side-wall top edges are the exact real `p_stage(x)` from
`derived/stage_ridges_v4.csv`; PCHIP interpolation (304→800) is display-resolution only.

## Panel (e): confidence trajectory — gaps found vs. reference, and fixes

1. **Gap**: v4 rendered a flat ribbon whose width varied with real uncertainty — a good real-data
   encoding in principle, but a flat strip still reads as "thin" regardless of its width, because
   it has no cross-sectional roundness for light to model.
   **Fix**: rebuilt as a genuine 3D **tube** — a parallel-transport frame computed in
   per-axis-normalized space (since `relative_life`, `q_pred`, `max_prob` have different physical
   ranges, computing the frame in raw units would distort the tube's roundness) generates a
   circular cross-section at each point; the tube now has real specular highlights and shading
   that a flat ribbon cannot produce.
2. **Gap**: the v4 ribbon's width-to-uncertainty encoding was present but visually subtle.
   **Fix**: kept the exact same real formula (`half_width = w_min + u_norm·(w_max−w_min)`,
   `u_norm` = real per-run uncertainty normalized to [0,1]) but as a TUBE RADIUS instead of a flat
   ribbon half-width — the confident (thin) vs. uncertain (thick) regions are now much more
   visually legible because the tube's cross-section, not just its silhouette, changes.
3. **Gap**: no floor context in v4 beyond a thin projection line.
   **Fix**: kept the real `(relative_life, q_pred)` floor projection line, colored consistently,
   and added real vertical stems from floor to the tube every ~27 real runs (a standard
   scientific-3D device for grounding a trajectory in its base plane, seen in the reference).
4. **Gap**: a single camera angle risked showing the tube's self-crossing region (where the real
   trajectory loops back near high `q_pred`/high confidence, around relative life 0.8–1.0) as a
   confusing tangle.
   **Fix**: rendered and compared 5 candidate angles
   (`outputs/panel_e_camera_trials/angle_{1..5}_az*_el*.png`); `az=-60, el=30` shows the loop as a
   legible, genuine 3D structure rather than an ambiguous knot, with tight, uncluttered axis
   limits.
5. **Gap**: default MATLAB axis auto-padding produced inconsistent, loose-looking limits
   (`relative life` ranging visually from -0.2 to 1.2 in some early trial renders).
   **Fix**: explicit `xlim`/`ylim` set to the real data range plus a small fixed margin, for a
   tighter, more intentional-looking frame consistent across camera angles.

Tube height (`Z`) is always the real `max_prob(x)` from `derived/confidence_ribbon_v4.csv`,
shared identically around the full circumference at each point — only the tube's radius encodes
(real) uncertainty, exactly as required; this has no physical q-magnitude meaning and is stated as
such in the panel's own caption ("no physical q-meaning") and in the README.

## Panels (a)/(b)/(c): top-row trio — gaps found vs. v4, and fixes

1. **Gap**: markers/legend were adequate in v4 but not treated as a deliberately coherent trio —
   each panel's marker size/alpha and legend/colorbar placement were tuned slightly differently.
   **Fix**: unified marker size (24), alpha (0.72–0.82), and stage-marker shapes (○/△/□) across
   all three; identical `xlim`/`ylim` (computed once, shared) so the manifold's shape is visually
   comparable panel to panel without the eye needing to re-calibrate scale.
2. **Gap**: panel (a) had color only; the reference mockup's panel (a) also uses hollow stage
   centroid markers as an additional structural cue.
   **Fix**: added hollow centroid markers, computed as the real per-stage mean of `PC1`/`PC2`
   (not eyeballed) — visually anchors each cluster's center without adding any new data point.
3. **Gap**: the manifold's continuity (the thin connecting thread visible in the reference) was
   present in v4 but visually competed with the marker fill.
   **Fix**: kept the dashed q-ordered connector line at a slightly reduced weight/alpha so it
   reads as a guide, not competing with the markers.
4. **Gap**: panel (c)'s misclassified-sample markers in v4 were adequate but not obviously
   distinguished as a categorically different mark (vs. just an oddly-colored point).
   **Fix**: kept them as a hollow high-contrast ring (dark red), reading as an explicit
   annotation layer on top of the base scatter, sourced only from the real `misclassified` column
   (all 3, none hand-picked).
5. **Gap**: colorbar proportions/placement were adequate but slightly cramped against each
   panel's right edge in v4.
   **Fix**: explicit `Position` rectangles for all 5 panels in the final composition (see panel
   (d)'s note above) gave enough dedicated horizontal room per top-row panel that MATLAB's
   automatic colorbar placement no longer crowds the plot area.

Panels (a)/(b)/(c) read `../_shared/derived/shared_pca_scores_v4.csv` directly — the exact same
304-row, sign-fixed PCA coordinates `fig4`'s panel (d) already uses. No independent PCA refit, no
added points, no jitter.

## Real-data confirmation (explicit, per the brief's requirement)

- Panels (a)/(b)/(c): all 304 rows of `shared_pca_scores_v4.csv`, unmodified. Centroids are real
  per-stage means. Misclassified markers are the real `misclassified` column (n=3).
- Panel (d): the top cap and side-wall top edges use the exact real `p_early/middle/late(x)` from
  `derived/stage_ridges_v4.csv` (304 real rows); the only non-real elements are (i) PCHIP
  interpolation to 800 display vertices (documented display-only, real markers overlaid every 12
  runs) and (ii) the Y-half-width/side-wall geometry, which is a stated visual extrusion, never a
  second measured axis.
- Panel (e): the tube centerline (`X,Y,Z` at the tube's core) is the exact real
  `(relative_life, q_pred, max_prob)` from `derived/confidence_ribbon_v4.csv` (304 real rows,
  uncertainty joined 1:1 by `run_id`, validated in `prepare_fig5_v4.py`); tube radius is a
  documented visual encoding of real per-run uncertainty; the only non-real element is PCHIP
  interpolation to 800 display vertices for rendering smoothness (real markers overlaid every 18
  runs).
- No sample was added, removed, moved, or reweighted anywhere in this round. Row counts (304)
  verified by `assert` in `plot_fig5_v5.m` before any plotting.

## Layout bugs found and fixed during final composition (beyond the panel-level work above)

1. `tiledlayout`'s child axes reject direct `Position`/`InnerPosition`/`OuterPosition` writes in
   this MATLAB version (confirmed by a hard error) — this blocked the exact fix panel (d)/(e)
   needed for their dead-space problem. Switched the whole final composition from
   `tiledlayout`/`nexttile` to plain `axes(fig, 'Position', [...])` with explicitly computed
   rectangles, matching the approach already proven in `plot_fig5_v3.m`/`plot_fig5_v4.m`.
2. A first caption-width attempt used a fixed box width, which overflowed horizontally into the
   next panel's own y-axis label at this canvas's true proportions. Fixed by sizing the caption
   box to the panel's own rendered width (`pos(3)*0.96`), never wider.
3. A caption placed with `pad=0.01` below each 2D panel's axes collided with that SAME panel's own
   `xlabel` (e.g. "PC1") — the caption needs to clear both the x-tick number row AND the xlabel
   row below the axes box, not just one. Fixed by increasing `pad` to 0.075 and recomputing the
   whole vertical layout (top-row panel/caption bands vs. bottom-row panel/caption bands)
   explicitly so the two rows' caption bands never overlap each other's plot content either.

## Status: DONE

Scientific faithfulness: confirmed above, no fabricated data anywhere. Both 3D panels have
genuine volumetric/tube presence (not curtains/ribbons) and were chosen from 5 compared camera
angles each. Every panel caption sits centered below its own panel; no figure-level title. Final
composed output: `outputs/fig5_final_v5.{png,pdf,svg}` (PDF is large, ~57MB, for the same
transparent-3D-surface reason noted in v3/v4's README — the PNG is the practical choice for most
uses).

## Remaining limitations (honest)

- The tube's cross-section radius range (`w_min=0.012, w_max=0.075` in normalized-axis units) was
  chosen by visual judgment to make the uncertainty encoding legible without the tube becoming
  self-intersecting at high-curvature points (the loop near relative life 0.8–1.0); this is a
  display-tuning choice, not a data-derived value, and is disclosed as such.
- MATLAB's text-sizing doesn't expose the same per-artist point-size grep-audit the matplotlib
  figures use; caption/label sizes here (8.2–9.5pt) are chosen for legibility at this figure's
  scale but not individually audited against a numeric floor the way fig1-4's Python scripts are.
- SVG export triggered a non-fatal "depth sort" rendering warning from MATLAB given the many
  overlapping transparent 3D surfaces; the SVG file was still produced and opens correctly, but
  MATLAB's own guidance suggests `ContentType='image'` would be more robust for content this
  complex — not changed this round since the vector PDF/SVG both did complete successfully.
