# V4 Design Audit — publication-grade visual refinement

Prepared before any V4 code was written, per the task's explicit instruction. Covers: what's wrong
with V3 today, what to recover from `视觉参考效果图/` (layout only), what science must survive
unchanged, the V4 panel layout, inputs, Python/MATLAB split, and the specific beautification plan
per figure.

## Sources consulted this round

- `paper_data/DCPSR_Chapter4_CN_Detailed.docx` — already fully read in an earlier turn of this
  session (its content is reflected throughout `FIGURE_PROGRESS.md` and every `figX/README.md`);
  not re-read line-by-line again here since nothing about the frozen data or panel plan changed.
- `paper_data/figure/FIGURE_PROGRESS.md` — re-confirmed: figure↔paper mapping (§1), headline
  numbers (§3), method/dataset naming (§4), metric direction (§5). All unchanged from V3; V4 does
  not touch data.
- `paper_data/figure/figX/视觉参考效果图/*.png` (all 5) — re-viewed in the V3 round of this
  session; layout proportions and visual devices already catalogued in each `figX/README.md`'s
  "v3" section. Not re-copied here in full; referenced per-figure below.
- `plot_fig1_v3.py` / `plot_fig2_v3.py` / `plot_fig3_v3.py` / `plot_fig4_v3.py` /
  `prepare_fig5_v3.py` / `plot_fig5_v3.m` / `_shared/style_v3.py` — all authored/reviewed earlier
  this session; current state fully known.
- **New this round**: `代码/1.3.1可视化.py` and `代码/7.3主实验.py` (the original pre-refactor
  visualization code for the underlying experiments). Key findings:
  - Both set `plt.rcParams["font.family"] = "Times New Roman"` and
    `plt.rcParams["mathtext.fontset"] = "stix"` — confirms (not just motivates) this round's
    typography requirement; it's the paper's own established convention, not a new stylistic
    choice. Confirmed both fonts are available in this environment.
  - `plot_3d_stage_probability_trajectory` (x=p_early, y=p_middle, z=p_late, color=cut_index,
    `viridis`, thin gray connecting line, `view_init(elev=24, azim=42)`) and
    `plot_3d_degradation_probability_space` (x=q_hat, y=p_middle, z=VB_true, color=true stage,
    `view_init(elev=24, azim=-52)`) confirm the original paper's visual philosophy: probability
    geometry is drawn as a **continuous connected trajectory in a real coordinate space**, not
    static bars — this is the spirit V4's fig5(d)/(e) should carry further, without adopting
    either function's literal axes (fig5's current science, `hidden_representation.csv` PCA +
    `lifecycle_semantics.csv` life/q/confidence, is authoritative and unchanged).
  - `plot_probability_simplex` in `7.3主实验.py` uses vertex convention **Early=bottom-left,
    Middle=bottom-right, Late=top** (`x = p_middle + 0.5*p_late`, `y = (√3/2)*p_late`). This
    differs from V1-V3's own simplex convention (Early=left, Late=right, Middle=top). **V4 change**:
    fig4(b) adopts the paper's own vertex convention for visual consistency with the rest of the
    thesis (this is a coordinate-labeling choice, not a data change — same 304 real
    `(p_E,p_M,p_L)` triples, same trajectory, just which corner is which).
  - Fine-state 3D panels (`plot_3d_fine_state_summary`, `plot_gmm_3d`) are about a 5-way
    sub-classification (`fine_prob_0..4`) that is **not** part of the current Fig.4/Fig.5 data
    contract (`hidden_representation.csv`, `lifecycle_semantics.csv` carry no fine-state columns).
    Per the task's own instruction ("不能把这些旧变量替代最新Fig5的科学定义"), these are read for
    *visual philosophy* only and are not reproduced as panels.

## Global V4 changes (apply to all 5 figures)

1. **New module** `_shared/style_v4.py` (v1/v2/v3 untouched). Re-exports data/validation logic
   unchanged; replaces color constants with the new hex palette specified in the brief; replaces
   `apply_style()` with Times New Roman + STIX rcParams at the brief's point sizes; keeps v3's
   `panel_container()`/`sub_caption()` GridSpec-based caption mechanism (still correct, still the
   right way to guarantee below-panel captions — the bugs found in V3 were process bugs in
   *how it was called*, not in the mechanism itself, so the mechanism carries forward unchanged;
   only color/font/size constants and the physical-size/export pipeline are new).
2. **Physical paper sizing.** Every figure gets a `MASTER_SIZE_MM` constant (178mm width, height
   per the brief's table below) converted to inches for `plt.figure(figsize=...)`, so text is sized
   correctly at final print scale from the start — never "big canvas + tiny font, shrink later."
   Outputs per figure: `figX_v4.pdf`, `figX_v4.svg`, `figX_v4_600dpi.png` (rendered directly at
   master size, 600 DPI), `figX_v4_paper_preview.png` (same master size, mid-DPI raster meant for
   on-screen readability review at true physical scale — the actual QA artifact this round's
   review step depends on).
3. **No `nature-figure` skill available** in this environment (not among the skills listed for
   this session — checked before starting). Visual QA is therefore performed manually against the
   brief's own §25 checklist in each `figX/VISUAL_QA_V4.md`, substituting for the skill review the
   brief describes; explicitly noted as a substitution, not skipped.
4. Master sizes (from the brief, used as-is):

| Figure | Width | Height |
|---|---|---|
| fig1 | 178mm | 120mm |
| fig2 | 178mm | 125mm |
| fig3 | 178mm | 130mm |
| fig4 | 178mm | 128mm |
| fig5 | 178mm | 132mm |

## Per-figure audit

### Fig.1 — 主比较 (Paper Fig. 4-2)

**V3 problems**: horizontal colorbar under the heatmap takes a visually heavy ~14% of panel (a)'s
height; confusion matrices use the same `BENEFIT_CMAP` as the heatmap (no visual differentiation
between "landscape overview" and "per-method detail"); panel (c)'s 3 blocks read as three
side-by-side mini-charts rather than one connected diagnostic rhythm; Pareto/bootstrap-CI content
was dropped entirely rather than reduced to an inset, and `DCPSR_Chapter4_CN_Detailed.docx` §4.2
does ask for a Pareto/CI view — that's a real content gap to fix this round, not merely a style one.

**Recover from reference**: slim colorbar strip; sequential Blues for confusion matrices (distinct
from the landscape heatmap's benefit palette); one shared vertical colorbar across all 4 confusion
matrices instead of implicit per-cell scaling; a continuous horizontal "diagnostic rhythm" feel in
the bottom panel rather than 3 disconnected blocks.

**Science to preserve**: 9 real methods (no B1-B12 labels); Multi-task TCN-GRU wins raw
classification, DC-PSR is competitive and wins Smooth — this must stay legible, not be visually
buried; bootstrap CI is real (`D1_9methods_bootstrap_CI.csv`) and must reappear, even if only as a
compact inset.

**V4 layout**: same top(56-58%)/bottom(42-44%) split as V3, refined: (a) heatmap with slim
under-heatmap colorbar (~3-4mm at master scale) + thin blue outline on Multi-task TCN-GRU's row +
thin red outline on DC-PSR's row (not just colored tick text); (b) 2×2 confusion matrices, uniform
square aspect, one shared vertical colorbar, sequential Blues; (c) one connected diagnostic panel
for 5 representative methods (RF, TCN-GRU, MTF-AViTK, Multi-task TCN-GRU, DC-PSR) — M-Pre/M-Rec as
main bars, M→E/M→L as narrow warm markers, Smooth as a clearly-labeled "Smooth ↓" lollipop/line,
Rev/Jump as small annotated markers (not full independent axes) — plus a small CI or Pareto inset
in reclaimed corner whitespace, per the brief's explicit instruction not to drop that evidence.

**Inputs**: unchanged from v1/v3 (`D1_main_metrics.csv`, `taskwise_absolute.csv` D1 rows,
`accuracy_consistency_points.csv`, `B11_B12_controlled_comparison.csv`,
`predictions_common_universe/D1_*_304runs.csv`). Python only.

### Fig.2 — 鲁棒性 (Paper Fig. 4-3)

**V3 problems**: 3 mini-heatmaps in panel (a) each carry their own y-axis method labels (redundant,
wastes width, creates visible gaps between the 3 mini-panels); panel (b)'s lollipop already matches
the brief's ask reasonably well but column/metric labeling could be tightened to the brief's exact
ΔAcc/ΔM-F1/Smooth-benefit/Jump-benefit 4-column matrix framing; panel (c)'s radar can read as
over-claiming if axis scaling isn't carefully monotonic-only.

**Recover from reference**: shared y-axis (method labels only on the leftmost mini-heatmap) and
shared colorbar for panel (a)'s 3 task heatmaps; explicit 4-quadrant background tinting in panel
(d) (low/low, classification-dominant, consistency-dominant, balanced) as a **very pale** decision
background, not data.

**Science to preserve**: no fictional 9-method comparison on NASA/MTW-CM (panel c stays
Multi-task-TCN-GRU-vs-DC-PSR only); panel (d) keeps exactly 6 real points; direction-unified radar
axes (Consistency/Stability) stay explicitly labeled as display transforms in-figure and in README.

**V4 layout**: same strict 2×2 as V3, tightened per above. (a)/(b) visually larger than (c)/(d) per
the brief.

**Inputs**: unchanged (`taskwise_absolute/normalized.csv`, `cross_dataset_absolute/deltas.csv`).
Python only.

### Fig.3 — 消融实验 (Paper Fig. 4-4)

**V3 problems**: the biggest structural issue this round explicitly calls out — the mechanism band
is visually oversized relative to the probability-dynamics content above it, and panel (d)
(Rev/Jump) spends a full panel on values that are trivially zero for all 6 configs. That's the
single most wasteful use of panel space in the whole 5-figure set today.

**Recover from reference**: the dual-axis bar+line combo panels' visual density; light warm-color
A5 shading (already good in V3, keep); the 6-node mechanism flow-chain's basic device (already
built in V3, keep and refine node typography/spacing).

**Science to preserve**: A1-A4 must render as visually flat/near-identical (never exaggerated via
y-axis truncation); A5 dip and A6 recovery must be real, not amplified; Smooth is shown as
"improvement vs A1 (%)" explicitly labeled, never raw Smooth flipped silently; Rev=Jump=0 for all
6 configs is real (confirmed in V3's own validation log) and should be stated as a one-line
annotation, not a full wasted panel.

**V4 layout — the one structural (not just cosmetic) change this round**: top 2×2 shrinks to ~76-80%
of the panel area (from V3's roughly 50/50 split with the mechanism band), mechanism band drops to
~20-24%. Panel (d) is repurposed entirely: instead of near-empty Rev/Jump bars, it shows the real
`A1_A6_lifecycle_variation.csv` (local probability variation vs relative life) and
`A1_A6_cumulative_variation.csv` (cumulative variation) — both already loaded by v1's `load()` but
underused in this exact combination — with Rev=Jump=0 reduced to a one-line annotation. This is a
genuine content improvement the brief explicitly calls for ("这比画全零Rev/Jump更符合当前第四章的科学目标"),
not merely restyling.

**Inputs**: unchanged (`A1_A6_absolute.csv`, `A1_A6_probability_trajectories.csv`,
`A1_A6_delta_vs_A1.csv`, `A1_A6_lifecycle_variation.csv`, `A1_A6_cumulative_variation.csv`).
Python only.

### Fig.4 — 退化语义 (Paper Fig. 4-5)

**V3 problems**: panel (a)'s stage-probability curves are already line+fill (not heavy stacked
area, this was fixed in V3) — good, keep. Panel (d) ("latent manifold overview") fits its own
independent PCA, separate from Fig.5's — the brief correctly flags this as a real defect: sign/
rotation could differ between the two figures, undermining the "same shared representation" claim
across the two hero figures. This is the other genuine structural fix this round (not cosmetic).

**Recover from reference**: none of panel (c)'s idealized near-y=x cloud (V3 already correctly
shows the real compression — keep); none of panel (e)'s log-scale VB axis (V3 already uses linear
μm — keep).

**Science to preserve**: R²≈0.748 (coefficient of determination on raw q_pred, not squared Pearson
r), Spearman ρ≈0.963, MAE≈0.113; VB means ≈100.6/126.3/205.5 μm; q_pred's real saturation at high
q_true; 304 real points throughout panels (a)-(c)/(e), no fabricated density.

**V4 layout**: same 3-top/2-bottom (52%/48%) split. **Structural fix**: panel (d) switches from its
own independent PCA fit to reading `_shared/derived/shared_pca_scores_v4.csv` — the *same* PCA
coordinates Fig.5(a)/(b)/(c) will use, generated once by a new `prepare_shared_pca_v4.py`. Sign
convention fixed deterministically: PC1 sign chosen so `corr(PC1, q_true) > 0` (Early tends left,
Late tends right); PC2 sign-flip-only if needed for a stable, documented display convention — never
an arbitrary rotation. This is a coordinate-display convention, not a data change (PCA sign/
orientation has no statistical meaning).

**Inputs**: `lifecycle_semantics.csv`, `simplex_trajectory.csv`, `q_agreement.csv`,
`wear_by_predicted_stage.csv` (unchanged) + **new**: `_shared/derived/shared_pca_scores_v4.csv`
(from `hidden_representation.csv`, via the new shared prep script). Python only.

### Fig.5 — 表示几何 (Paper Fig. 4-6) — the round's main focus

**V3 problems** (the brief is explicit that this is the most important target): the two MATLAB 3D
panels are structurally sound (real lighting, real camera, real data) but visually thin — panel
(d)'s ridges are described by the brief as "too thin, too much like a simple ribbon," and panel
(e)'s constant-width ribbon doesn't encode any additional real information beyond what a 2D line
would. Also: panel (d)/(e)'s current implementation is genuinely defensible (no fabricated data),
but there is real headroom to make the *visual encoding itself* carry more real information without
fabricating anything — which is exactly what the brief's uncertainty-proportional ribbon-width idea
for panel (e) achieves.

**Recover from reference**: broader, more confident-looking 3D ridge/ribbon geometry; a floor
projection that carries real information (not just a shadow); the general sense of "this is the
paper's centerpiece figure" visual weight.

**Science to preserve** (hardest constraint this round): 304 real points, no fabricated density, no
interpolation masquerading as new measurements, no second experimental dimension invented for a
1D observation. The brief's specific, load-bearing requirements: (1) panel (d)'s ridge width is a
*visual extrusion only* — all cross-ribbon Z values must equal the same real `p_stage(x)` value,
never a fabricated second dimension; PCHIP/shape-preserving interpolation is allowed for rendering
resolution only (304→~800 display vertices) and must be documented as display-only, with the
original 304 points still visible as markers; (2) panel (e)'s ribbon half-width must be **driven by
real per-sample uncertainty** (`hidden_representation.csv`'s `uncertainty` column, joined 1:1 by
run_id/sample_id to `lifecycle_semantics.csv` — verify the join is exact 304↔304 before trusting
it), linearly mapped to a visual width range, explicitly documented as a visual encoding with "no
physical meaning" in its absolute width; (3) floor projection in (d) is a real probability-mixture
color blend (`pE*Early + pM*Middle + pL*Late`, normalized), not a texture invented for looks; (4) no
Pmax=0.8 threshold plane unless the method actually uses that threshold (checked: it does not per
current data contract — omit).

**V4 layout**: top (34-38%) unchanged in spirit — 3 PCA panels — but now reading the shared
`shared_pca_scores_v4.csv` fixed in the Fig.4 audit above, guaranteeing Fig.4(d) and Fig.5(a)-(c)
show geometrically identical coordinates. Bottom (62-66%) is where the real rework happens: (d)
stage-probability ridge curtains widened to 15-25 visual y-samples per stage (from 2), real
per-run markers every ~10-15 runs, floor probability-mixture strip, dominant-stage transition line
from real `argmax(prob)` (documented choice vs `true_stage`, pick one); (e) uncertainty-driven
ribbon (15-25 cross-samples, half-width ∝ normalized real uncertainty), colored by real `max_prob`,
thick center trajectory line with real-sample markers, floor projection of the real
`(relative_life, q_pred)` path, a few real vertical stems from floor to surface.

**Inputs**: `_shared/derived/shared_pca_scores_v4.csv` (new, shared with Fig.4), plus
`hidden_representation.csv` (for `uncertainty`/`entropy`, joined to lifecycle data for panel e) and
`lifecycle_semantics.csv` (unchanged). **Python+MATLAB split, same as V3**:
`prepare_fig5_v4.py` (Python: load shared PCA + validate join + export ridge/ribbon derived CSVs
at display resolution, clearly flagging which columns are real-304 vs interpolated-display) →
`plot_fig5_v4.m` (MATLAB: render at master physical size, real lighting/camera per the brief's
specific view-angle/lighting recipe, below-panel captions via post-`drawnow` `annotation()`
positioning — same geometric-lock principle V3 already validated in MATLAB).

## Execution order (strict, per the brief)

Fig.1 first → build V4 → paper-preview → `VISUAL_QA_V4.md` → three-way visual comparison
(视觉参考效果图 vs V3 vs V4) → only proceed to Fig.2 once Fig.1 no longer reads as a "default
matplotlib dashboard." Then Fig.2 → Fig.3 → Fig.4 → Fig.5, each independently reviewed before the
next starts (no batching), consistent with how V3 was built. Fig.5 gets the most iteration time,
consistent with it being explicitly named the round's centerpiece.

---

## Execution journey — what actually happened, in order

This section is the after-the-fact record: what was read, what was built, in what sequence, what
broke and how it was diagnosed and fixed, written once the round finished so the audit above (the
*plan*) and this section (the *execution*) can be read side by side.

### Phase 0 — required reading, before any code

- `paper_data/DCPSR_Chapter4_CN_Detailed.docx` and `paper_data/figure/FIGURE_PROGRESS.md`: not
  re-read line-by-line (both were already fully internalized earlier in this session, across the
  V1-V3 rounds); re-confirmed their content was still current rather than re-deriving it.
- All 5 `figX/视觉参考效果图/*.png`: already viewed in detail during the V3 round; not re-viewed
  pixel-by-pixel here, but each figure's build step re-checked its specific mockup against the
  actual V4 render for the layout devices called for in the brief.
- **New this round**: `代码/1.3.1可视化.py` and `代码/7.3主实验.py`, read specifically because the
  brief named exact function names to check (`plot_3d_stage_probability_trajectory`,
  `plot_3d_degradation_probability_space`, `plot_3d_fine_state_summary` in the first file;
  `plot_probability_simplex`, `plot_gmm_3d`, `plot_q_and_prob` in the second). This produced two
  concrete, load-bearing findings, not just background color: (1) both files — and several other
  sibling scripts in `代码/` — set `plt.rcParams["font.family"]="Times New Roman"` and
  `["mathtext.fontset"]="stix"` as standard practice, which turned this round's typography
  requirement from "a new stylistic ask" into "match what the paper's own code already does,"
  confirmed available in this environment before committing to it; (2) `plot_probability_simplex`
  uses a **different ternary-vertex convention** (Early=bottom-left, Middle=bottom-right, Late=top)
  than v1-v3's own simplex panel (Early=left, Late=right, Middle=top) — surfaced as a deliberate
  fig4(b) change this round, specifically because this reading step was done before touching that
  panel rather than after.
- Confirmed Times New Roman + STIX render correctly in this environment (`matplotlib.font_manager`
  check) before relying on them.

### Phase 1 — design audit (required deliverable before code)

Wrote `paper_data/figure/V4_DESIGN_AUDIT.md` (this file) covering, per figure: the specific V3
visual problems, what to recover from the reference mockup vs. what to reject, the science that
must not move, the new V4 panel layout, the input files, and whether Python or Python+MATLAB. Two
items were flagged here as *structural* (not cosmetic) fixes required this round, and both were
carried through to completion: fig3 panel (d)'s near-all-zero Rev/Jump panel, and fig4/fig5's
independent-PCA inconsistency risk.

### Phase 2 — shared infrastructure

Built `_shared/style_v4.py`: re-exported v3's `panel_container()`/`sub_caption()` caption
mechanism completely unchanged (a deliberate choice — nothing about *how* captions are
geometrically locked was ever the bug source across 3 rounds, only how the `hspace`/`caption_height`
parameters feeding it were tuned), added the brief's exact new hex palette, Times New Roman + STIX
rcParams, `master_figsize_in()` for true-physical-size figure creation, and a `save_all()` that
emits all four required artifacts (`.pdf`, `.svg`, `_600dpi.png`, `_paper_preview.png`).

### Phase 3 — Fig.1, built directly (not delegated), to prove the template

Built by hand rather than forked, since the brief explicitly required Fig.1 to be validated before
any other figure started, and getting the *first* true-physical-size figure right required tight,
fast iteration loops (write → run → view the actual `_paper_preview.png` → fix → repeat) that are
better done directly than relayed through a fork's own back-and-forth. Concretely hit and fixed, in
order: (1) panels (a)/(b)'s single-line captions overflowed horizontally into each other at 178mm
width — first attempt increased `hspace`, which didn't address a horizontal (not vertical) overflow
problem; real fix was wrapping both captions to 2 lines and shortening them; (2) the confusion-matrix
method-name sub-captions, built via `sub_caption()`, still collided after a moderate `hspace`
increase; a much larger `hspace` correction then over-corrected, visibly squashing each 3×3
matrix's own internal content; root-caused as "nested-GridSpec caption overhead compounds when the
absolute cell size is already small" and fixed by abandoning that mechanism for this one case in
favor of `ax.set_title(method, y=-0.34)`, which anchors to the axes' own transform instead of a
separately-computed cell; (3) a final explicit grep-style pass over every `fontsize=`/`labelsize=`
call found several elements (colorbar ticks, CI-inset labels) sitting at 5.2-5.9pt, below the
brief's 6.5pt floor — bumped all of them and re-verified the fix didn't reintroduce any collision.
Result: `VISUAL_QA_V4.md` status DONE, scientific faithfulness 10/10, zero open issues.

### Phase 4 — Fig.2, forked, then 2 post-handoff fixes

Delegated to a forked subagent briefed with the fig1 template and its 3 documented bugs. The fork's
own build already caught and fixed several issues during its own iteration (documented in its
handoff and in the README's v4 section — e.g. it discovered fig1's `set_title(y<0)` trick was
actually the *wrong* tool for one of its own panels and reverted to the simpler pre-existing
`set_xlabel()`, a useful counter-example to not applying prior fixes by blind analogy). On
independent review of the handoff's `_paper_preview.png`, two further real bugs were found and
fixed directly: (1) panel (a)'s 3-metric column labels ("Acc↑"/"M-F1↑"/"Smooth↓") genuinely
overlapped each other in the narrower D2/D3 mini-heatmap columns at 0° rotation — fixed with a 32°
rotation; (2) panel (c)'s radar cards' radial tick labels ("0.5"/"1.0") default to the same spoke as
the "Acc" axis label, crowding that corner — fixed with `ax.set_rlabel_position(45)` plus more
inter-card spacing. Result: DONE, one remaining cosmetic item (radar labels from adjacent cards
sitting close but not merged) explicitly logged rather than force-fixed.

### Phase 5 — Fig.3, forked, then 2 post-handoff fixes

Delegated similarly, briefed with fig1 AND fig2's accumulated bug lessons. The fork completed the
one genuinely structural change this figure needed — panel (d) rebuilt from v3's near-all-zero
Rev/Jump bars into real `A1_A6_lifecycle_variation.csv`/`cumulative_variation.csv` content, with
Rev=Jump=0 kept as a single caption line rather than a wasted panel — plus the 6-node mechanism
flow-chain with real per-node deltas. On independent review, two more true-physical-size bugs were
found and fixed directly: (1) panel (b)'s "A5" x-tick label collided with its own caption (needed
`hspace=1.10`, matching the magnitude panel (d) already needed for the same reason — confirming
this is genuinely a per-panel tuning problem, not a one-time fix); (2) panel (d)'s 6-entry
single-row legend (`ncol=6`) was wider than its own axes and visually overflowed into the
neighboring subplot, since matplotlib legends aren't clipped to their parent axes — fixed by
reflowing to `ncol=3` (2 rows). Result: DONE.

### Phase 6 — shared PCA infrastructure, built directly

Before Fig.4 or Fig.5 could be started, `_shared/prepare_shared_pca_v4.py` was built and run
directly (a small, self-contained, foundational script both figures would depend on — worth getting
right once rather than having two forks independently reason about the same sign-convention
requirement). Fit PCA once via numpy SVD on the real 304×64 hidden representation, applied the
brief's deterministic PC1 sign rule (`corr(PC1, q_true) > 0`), verified the resulting correlation
(0.933 — a strong confirmation of the continuous-ordering narrative, not just a sign-fixing
exercise), and wrote `_shared/derived/shared_pca_scores_v4.csv`.

### Phase 7 — Fig.4, forked, zero post-handoff fixes needed

Delegated with explicit instructions to (a) consume the shared PCA file for panel (d) instead of
fitting independently, and (b) adopt the paper's own simplex vertex convention for panel (b), per
the Phase-0 reading. The fork's own review cycle caught and fixed 2 real issues itself (a
Chinese-filename caption fragment that both overflowed at 178mm width and triggered missing-glyph
warnings in Times New Roman; a degradation-direction annotation visually swallowed by a point
cluster). Independent review of the final handoff found no further issues — the only figure this
round that needed zero post-handoff correction. Result: DONE, confirmed shared-PCA consumption and
convention change both verified in the validation log.

### Phase 8 — Fig.5, forked, MATLAB rework, the round's centerpiece

The longest and most complex build. Briefed with the accumulated bug lessons from all four prior
figures, the exact ribbon-width/floor-strip formulas from the brief's §13-22, and pointers to
`代码/1.3.1可视化.py`/`代码/7.3主实验.py` for the original paper's 3D visual philosophy (continuous
connected trajectories, specific historical view angles) as inspiration without adopting their
literal old variables. The fork: (1) built `prepare_fig5_v4.py`, validating the uncertainty join
(`hidden_representation.csv`'s `uncertainty` to the lifecycle trajectory via `run_id`) as an exact
304↔304 one-to-one match before trusting it for panel (e)'s ribbon-width encoding; (2) built
`plot_fig5_v4.m`, reworking panel (d) from v3's 2-sample-wide ribbons into 21-sample-wide ridge
curtains with a real probability-mixture floor color strip and a real `argmax(prob)` transition
line, and panel (e) into a ribbon whose half-width is driven by real per-run uncertainty
(narrow where confident, wide where uncertain) rather than a constant width; (3) hit and fixed 3
real MATLAB-specific layout bugs across its own iteration (captions colliding with axis-label text;
a fix for that which then caused a *different* row-to-row caption collision because
`TileSpacing='compact'` had no real inter-row gap — fixed by switching to `'loose'`); (4) confirmed
MATLAB R2021a batch-mode rendering worked end-to-end, matching the working invocation pattern
already proven in the V3 round. On independent review, the render was accepted as-is: two very
minor tight-but-legible caption/label spots were left as disclosed open issues (matching the same
"tight but not character-merged" bar already accepted on fig2, rather than demanding a fourth
MATLAB iteration round for a marginal gain). Result: DONE, scientific faithfulness 10/10, MATLAB
text conservatively audited at ≥7pt as an honestly-disclosed stand-in for matplotlib's exact
≥6.5pt-per-artist grep-audit (MATLAB doesn't expose the same granular per-artist control).

### Phase 9 — wrap-up

Updated `FIGURE_PROGRESS.md` §10 and the top-level `figure/README.md` with the full v4 status,
reproduction commands, and shared-infrastructure description. Verified all 20 expected output
files (`figX_v4.{pdf,svg}` + `_600dpi.png` + `_paper_preview.png` × 5 figures) and all 5
`VISUAL_QA_V4.md` files exist. Re-ran the shared-PCA script and all 4 pure-Python v4 scripts fresh
from a clean invocation to confirm end-to-end reproducibility (fig5's MATLAB stage was not
re-run a second time in this final pass, given its ~5-10 minute cost per invocation and having
already been confirmed working end-to-end during Phase 8).

### Net result

5/5 figures at status **DONE**: scientific faithfulness 10/10 on every figure (a hard requirement,
not a target), every text element ≥6.5pt (≥7pt for fig5's MATLAB text, disclosed), zero
fabricated data points anywhere, two genuine structural content improvements (fig3 panel d, fig4/
fig5 shared PCA) beyond pure restyling, and 12 real true-physical-size layout bugs found and fixed
across the round — 3 caught and fixed directly during the Fig.1 template build, 2 more on Fig.2
and 2 more on Fig.3 caught on independent post-handoff review (beyond what each fork already fixed
in its own iteration), 2 caught and fixed inside Fig.4's own fork iteration, 3 caught and fixed
inside Fig.5's own MATLAB iteration — none left unresolved except the handful of explicitly
disclosed, genuinely minor "tight but legible" items logged in each figure's own
`VISUAL_QA_V4.md`.
