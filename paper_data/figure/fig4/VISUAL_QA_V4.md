# Fig.4 v4 — Visual QA

Reviewed against `outputs/fig4_v4_paper_preview.png` (rendered at the true 178×128mm master
size) — not just the 600dpi PNG at screen zoom.

## Scores (0–10)

| Criterion | Score | Notes |
|---|---|---|
| Reference layout similarity | 9 | Top row (lifecycle/simplex/q-agreement) + bottom row (latent manifold/physical wear) proportions (52%/48%) match `视觉参考效果图/`'s spatial organization; distinct from it only where the reference itself is wrong (log VB axis, idealized q cloud — see Scientific faithfulness). |
| Information density | 9 | Full lifecycle trajectory + q strip, simplex, q-agreement stats, shared latent overview, and violin/box/raw-point wear distribution, all real, nothing dropped. |
| Whitespace efficiency | 9 | No dead zone exceeds ~5% of canvas; "increasing degradation →" annotation repositioned with a white backing box specifically to avoid being swallowed by dead space/point overlap. |
| Typography consistency | 10 | Times New Roman + STIX throughout; smallest elements (colorbar ticks, stat-box text) at 6.5–6.6pt, everything else 6.8–8.4pt — grep-audited, nothing under the 6.5pt floor. |
| Color consistency | 10 | `STAGE_COLORS`/`DEGRADATION_CMAP` from `style_v4.py` used identically across panels (a)/(b)/(d); wear violins in panel (e) use the same 3 stage colors. |
| Scientific faithfulness | **10** | R²=0.7478/ρ=0.9635/MAE=0.1132 recomputed live and asserted (coefficient of determination on raw `q_pred`, not squared Pearson r); VB means recomputed live and cross-checked against `wear_by_predicted_stage.csv`; panel (d) reads the shared PCA file rather than fitting its own (asserted no independent fit in this script); VB axis linear 65–245μm (reference's log axis NOT reproduced); q-agreement's real compression at high q_true preserved, not smoothed. No fabricated data anywhere. |
| A4/178mm-width readability | 9 | Confirmed legible at true preview scale after fixing two real issues (below). |

## Answers to the brief's 8 required questions

1. **Reference elements adopted**: 5-panel top-3/bottom-2 spatial proportions; general density and
   visual weight of the lifecycle+simplex+q-agreement trio.
2. **Reference elements NOT adopted, and why**: its idealized near-y=x q-agreement cloud (this
   project's real q_pred saturates/compresses at high q_true — shown as-is); its log-scale
   (10¹–10⁴) VB axis (this project's real VB range is a modest 65–245μm, linear is correct and
   was used); any of its specific numbers.
3. **Any visual interpolation?** None beyond what v1/v2/v3 already used (none, in fact — panel (a)
   plots the raw 304-point trajectory directly, no smoothing).
4. **Any change to a real data point?** No. `logs/validation_v4.txt` reruns v1's R²/ρ/MAE/VB-mean
   checks live and all pass.
5. **Smallest text at final size**: 6.5pt (colorbar tick labels, stat-box numbers) — meets the
   brief's floor.
6. **Dead space >8–10% of canvas?** No.
7. **Legend covering data?** No — panel (a)'s legend has a white background and sits in the
   probability panel's naturally low-value region (bottom-left).
8. **Caption/panel visual conflicts?** None remaining. One real one was found and fixed: panel
   (b)'s original caption (which named the source of its vertex convention directly in-figure,
   including Chinese characters from a filename) both overflowed into panel (c)'s caption AND
   triggered Times-New-Roman missing-glyph warnings since that font has no CJK coverage. Fixed by
   shortening to a plain "(b) Ordered trajectory in the probability simplex" and moving the
   convention-source citation to this README instead — on-canvas text should never depend on a
   font having glyphs the rest of the figure doesn't need.

## Status: **DONE**

Scientific faithfulness = 10, every text element ≥6.5pt, no remaining collisions.

## Content changes this round (not just restyling)

1. **Panel (d) reads shared PCA, not its own fit.** `paper_data/figure/_shared/derived/shared_pca_scores_v4.csv`
   (built once by `_shared/prepare_shared_pca_v4.py`, PC1 sign fixed so `corr(PC1, q_true) > 0`,
   verified 0.933) is now the only PCA fig4(d) uses. This guarantees Fig.4(d) and Fig.5(a)/(b)/(c)
   show geometrically identical latent geometry, closing the sign/rotation-mismatch risk flagged
   in `V4_DESIGN_AUDIT.md`. PCA sign/orientation carries no statistical meaning; this is a display
   convention, not a data change.
2. **Panel (b)'s simplex vertex convention changed.** v1-v3 used Early=left/Late=right/Middle=top.
   v4 switches to **Early=bottom-left, Middle=bottom-right, Late=top** — matching
   `代码/7.3主实验.py::plot_probability_simplex`'s own established convention
   (`x = p_middle + 0.5*p_late, y = (√3/2)*p_late`), confirmed by reading that file this session.
   Same real 304 `(p_E,p_M,p_L)` triples, same trajectory shape — only which corner is labeled
   which stage changed, for visual consistency with the rest of the thesis's own figures.
3. **No significance annotation added to panel (e)** — the brief requires any p-value shown to come
   from a real test run this session, or to be omitted. The real gap between Early/Middle/Late VB
   means (100.6/126.3/205.5 μm, non-overlapping IQRs) is visually self-evident without one, so no
   test was run and none is shown, per the brief's own "宁可不放" (better to omit than force it) guidance.

## Bugs found and fixed (both by independent review after the initial build)

1. Panel (b)'s caption named its convention source directly in-figure, including a Chinese
   filename — this both overflowed horizontally into panel (c)'s caption at 178mm width (same
   overflow class as fig1/fig2/fig3's captions) AND caused Times-New-Roman missing-glyph warnings
   during export (Times has no CJK coverage). Fixed by shortening the caption and moving the
   citation to this README.
2. Panel (d)'s "increasing degradation →" annotation sat directly under a dense point cluster at
   the manifold's vertex, becoming visually swallowed. Fixed by repositioning to the panel's
   emptier lower-right and adding a semi-transparent white backing box.
