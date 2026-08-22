# Fig.5 v4 — Visual QA

Reviewed against `outputs/fig5_v4_paper_preview.png`, MATLAB's own render at the true 178×132mm
master size (200 DPI export) — not the 600dpi PNG at screen zoom.

## Scores (0–10)

| Criterion | Score | Notes |
|---|---|---|
| Reference layout similarity | 8 | Top 3-panel PCA row / bottom 2-panel 3D row proportions match `视觉参考效果图/fig5`; panels (d)/(e) now read as broad, confident 3D geometry rather than v3's thin ribbons, closing the gap the brief explicitly flagged. Docked points because the reference's fabricated dense point cloud/full-surface look is (correctly) not reproduced — a deliberate, documented divergence, not a miss. |
| Information density | 9 | 3 PCA views (stage/q/uncertainty, same coordinates) + 2 3D panels each encoding 2 real quantities (height + real per-run color/width) — nothing dropped, and panel (e)'s ribbon width is new real information (uncertainty) beyond what v3 showed. |
| Whitespace efficiency | 8 | `TileSpacing='loose'` (needed to give below-panel captions room to clear axis decorations) adds visible but not excessive inter-row space; no region exceeds ~8% of canvas as pure dead space. |
| Typography consistency | 9 | Times New Roman throughout (`FontName` set on every axes and the caption `annotation`), STIX-equivalent tex interpreter for math labels (`q_{true}`, `q_{pred}`). Smallest text: colorbar labels/tick text at 7pt in MATLAB's own renderer — MATLAB does not expose the exact point-for-point 6.5pt floor control matplotlib's `fontsize=` does, but 7pt at true 178mm print scale is legible and above the spirit of the floor; see Open Issues for the honest caveat on exact-value auditing. |
| Color consistency | 10 | `STAGE_COLORS` hex values converted exactly from `_shared/style_v4.py` (Early `#2F6FB3`, Middle `#2E8B57`, Late `#E76F51`); degradation colormap built from the same 3 stops; confidence colormap is a deliberate purple→teal→yellow build, not MATLAB's default `jet`/`parula`. |
| Scientific faithfulness | **10** | Panels (a)-(c) read `_shared/derived/shared_pca_scores_v4.csv` directly (asserted, not refit) — same coordinates `fig4_v4`'s panel (d) uses. Panel (d): every cross-curtain sample at a given x shares the identical real `p_stage(x)`; only 304→800 PCHIP interpolation for rendering resolution, real markers every 12 runs. Panel (e): ribbon half-width is a documented linear function of real per-run `uncertainty` (joined 304↔304 exact via `run_id`, validated in `prepare_fig5_v4.py`); height is real `max_prob(x)`, never varying across the ribbon's width. No Pmax=0.8 plane (not method-native, omitted per the brief). No fabricated point density anywhere — exactly 304 real samples represented in every panel. |
| A4/178mm-width readability | 8 | Confirmed legible at true preview scale after 3 rounds of caption-spacing fixes (below); two very minor tight-but-legible spots remain (Open Issues), not blocking. |

## Answers to the brief's 8 required questions

1. **Reference elements adopted**: top-3/bottom-2 panel proportions; the general visual weight and
   confidence of the 3D panels being the figure's centerpiece; dual real-quantity encoding in
   panels (d)/(e) (position + color/width) rather than a flat single-encoding ribbon.
2. **Reference elements NOT adopted, and why**: its dense multi-thousand-point cloud (this
   project's real C6 test set is exactly 304 runs — reproducing that density would fabricate data);
   its fully-interpolated 2D-sampled surfaces in (d)/(e) (this project's underlying observations
   are 1-D trajectories — a literal measured surface would invent a second experimental dimension
   that was never collected); any of its numbers.
3. **Any visual interpolation?** Yes, explicitly scoped: PCHIP interpolation of the real 304-point
   trajectories to ~800 display vertices in both 3D panels, for rendering smoothness only. Every
   real observation is also drawn as an explicit marker (every 12 runs in panel d, every 17 in
   panel e) so the underlying 304-point reality stays visually traceable and auditable against the
   smoothed curtain/ribbon surface.
4. **Any change to a real data point?** No. `prepare_fig5_v4.py` and the MATLAB script's own log
   both assert row counts (304) and, for panel (e)'s critical uncertainty join, exact 304↔304
   one-to-one correspondence before writing/using that data.
5. **Smallest text at final size**: ~7pt (colorbar labels, 3D axis tick labels) in MATLAB's font
   system. MATLAB does not offer the same granular per-artist `fontsize=6.5` auditing matplotlib
   scripts used for the ≥6.5pt floor check in fig1-4; 7pt was chosen deliberately above that floor
   as a conservative substitute given the less precise MATLAB layout engine. See Open Issues.
6. **Dead space >8–10% of canvas?** No single region exceeds that threshold; the `TileSpacing`
   increase needed for caption clearance is the largest visible "gap," and it's within bounds.
7. **Legend covering data?** No — panel (a)'s stage legend sits in its own top-left corner over
   sparse/no data at that PC1/PC2 range (verified visually); panels (b)/(c)/(d)/(e) use colorbars
   placed outside the plotted data area by MATLAB's own layout, never overlapping points/surfaces.
8. **Caption/panel visual conflicts?** None remaining after 3 rounds of fixes (below). Two
   very-tight-but-not-merged spots are noted in Open Issues rather than iterated further, matching
   the precedent set in fig2_v4's QA doc for similarly minor tightness.

## Status: **DONE**

Scientific faithfulness = 10/10. All layout collisions found on review were fixed. Two very minor
tightness items remain (below) and are judged not to block DONE, consistent with the bar already
applied to fig2_v4's radar-card tightness.

## Open issues

- Panel (d)'s "Early" y-tick label sits close to the word "curtains" in its caption below (legible,
  not character-merged); panel (e)'s "(raw)" y-axis label sits close to "(e) Confidence ribbon" in
  its caption (same: tight, not merged). Both are a consequence of MATLAB 3D axes' tick/label text
  extending further from the nominal axes box than 2D axes do, at this figure's compact master
  height (132mm); a further-refined per-panel gap (rather than one shared `gap` constant in
  `add_caption_below`) could close this fully in a future pass.
- MATLAB's text-sizing model doesn't give the same per-artist point-size audit trail as the
  matplotlib-based figures (fig1-4 could `grep fontsize=` the whole script and confirm every value
  ≥6.5pt; MATLAB inherits font size from axes/figure defaults more implicitly). All text was set
  ≥7pt as a conservative stand-in for the same intent; flagged honestly rather than claimed as an
  exact-equivalent audit.
- `fig5_v4.pdf` is large (~19MB) due to the vector-rendered 3D surfaces (MATLAB warned about this
  during export, suggesting `ContentType='image'` for performance) — same tradeoff v3's PDF had;
  the 600dpi PNG is the practical choice for most uses, PDF is kept for true vector/print needs.
