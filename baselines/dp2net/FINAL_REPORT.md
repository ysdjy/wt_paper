# FINAL_REPORT.md -- DP2Net

Status as of this report: implementation, unit tests, and end-to-end
smoke tests are complete and passing. **Real Protocol A/B-S/B-D1
training has NOT been run yet** -- GPU was occupied by a concurrent
baseline (`baselines/mtf_avitk`) throughout this baseline's build, and
this project's collaboration protocol disallows concurrent GPU use by
more than one Claude instance. Per the user's stated preference, formal
multi-epoch training is left for the user to run manually via the
commands in `README.md`. This report will be updated with real numbers
once those runs complete.

## A. Paper fidelity

**Explicit components**: raw channel (Fx only), low-pass cutoff
(1733Hz), sample length (4608 = 16 revolutions), Stage IV threshold
(mean VB>0.3mm), Vst period L (Eq.6, no missing inputs), MSE constraint
(Eq.7), MMD formula (Eq.9), G's loss direction (`L_MSE - alpha*MMD`,
Eq.10, verified not sign-flipped), alpha=20, task loss (Eq.11), two-stage
Algorithm 1 (100+100 epochs), all Sec 4.3 training hyperparameters
(batch=64, lr's, cosine period=20, kpool=4, PHM2010 k=25), F=WDCNN by
reference to [38], source/target split ratio (70/30).

**Inferable components**: none beyond PAPER_SPEC.md's tabled items.

**Missing components** (documented implementation choices): sampling
frequency for PHM2010 (paper says 5kHz, physically inconsistent with its
own k=25 and Eq.4 -- resolved to 50kHz, native archive rate); S/G's exact
internal layer count/order beyond the stated shared k/kpool and G's
1-4-4 channel counts; AdaIN's style source (random noise, StyleGAN
convention); MMD's gamma (median heuristic); WDCNN's exact
channel/layer counts beyond "consistent with [38]" (canonical
architecture used); exact 4608-window sampling stride/position (uniform
random, fixed seed, recorded in `sample_manifest.csv`).

**Conflicts**: sampling-frequency text ("5kHz") vs. physics-consistent
`k=25` (only holds at 50kHz) -- see Missing above, same underlying issue.

**Critical missing / empirical findings**:
1. Tool diameter D and helix angle beta for PHM2010's `Vst` rise-fraction
   P (Eq.5) -- the paper's Table 1 only gives these for its own
   machining-experiment tool, not PHM2010. Assumed D=6mm (PHM2010
   documented convention), beta=30deg (no source, placeholder).
2. Exact I/II/III stage-boundary rule from ref [41] -- not recoverable
   (paywalled, web search only returned generic non-quantitative
   descriptions). A documented wear-rate-change-point proxy is used
   instead; Protocol A is explicitly an "adapted," not "exact,"
   reproduction on this dimension.
3. **Stage IV (failure, mean VB>0.3mm) empirically never occurs** for
   C1/C4/C6 in this project's real PHM2010 archive (confirmed: max
   mean-VB across all three tools is 216um, well under the 300um
   threshold, under both mean- and max-flute conventions). This is a
   data-driven finding, not an implementation choice -- see
   PAPER_SPEC.md sec 6b. Protocol A is run as an adapted 3-class
   (I/II/III) scheme as a direct consequence.

**Adaptations**: Protocol B-D1's pooled-source (C1+C4) training is a
genuine, explicitly-named departure from the paper's strict single-source
design ("DP2Net-adapted (pooled source)", never called "original
DP2Net"), added specifically to produce a number comparable to DC-PSR's
D1 main table (task instruction #64).

## B. Original reproduction (Protocol A)

| Target | Paper protocol | Paper result | Our result | Difference |
|---|---|---|---|---|
| C1->C4 | Source=C1 (70/30), 4-stage I/II/III/IV, Algorithm 1 (100+100ep) | 90.91% | **TBD -- not yet run on GPU** | -- |
| C1->C6 | (same) | 87.66% | **TBD -- not yet run on GPU** | -- |

**Note on task definition drift**: the paper's own protocol is 4-class;
ours is an adapted 3-class (I/II/III only, Stage IV empirically empty for
these tools). The accuracy numbers above therefore are **not** a strict
apples-to-apples comparison even once real numbers are filled in -- a
3-class task is a priori easier than 4-class, so any measured accuracy
gap must be interpreted with this in mind, not treated as pure
implementation-fidelity signal.

**Confirmed on CPU** (architecture-level sanity): all shape, gradient
(both training stages), MMD-direction, Vst-periodicity/range, and
single-batch (Stage 1) overfit tests pass (15/15,
`tests/test_pipeline.py`). Total S+G+F parameters: 60,956.

## C. Unified protocol

### B-S (native single-source, C1->C6)
- Train/val: C1 only, 70/30 (via `data/label_utils.py::get_single_source_split`).
- Test: C6, run-level aggregated (8 windows/run mean-probability).
- Preserves DP2Net's SSDG character exactly, only the label scheme changes.

### B-D1 (pooled-source adapted, C1+C4->C6) -- enters DC-PSR D1 main table
- Train/val: C1+C4 pooled (via `data/label_utils.py::get_unified_split`,
  identical split logic to every other baseline's D1 task).
- Test: C6, run-level aggregated.
- Named "DP2Net-adapted (pooled source)" throughout outputs -- this is
  explicitly NOT a claim that the paper itself was evaluated this way.

Both: source-domain-only validation for all model-selection decisions;
C6 touched exactly once for the final evaluation.

## D. Full metrics

**Not yet run.** Templates (5 seeds for B-D1, project standard
{42,52,62,72,82}; B-S at seed 42 as a supplementary reference point):

### B-D1 (main table candidate)
| Seed | Acc | Macro-F1 | E-F1 | M-F1 | L-F1 | M-Pre | M-Rec | M->E | M->L | Rev | Jump | Smooth |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 42 | | | | | | | | | | | | |
| 52 | | | | | | | | | | | | |
| 62 | | | | | | | | | | | | |
| 72 | | | | | | | | | | | | |
| 82 | | | | | | | | | | | | |
| mean+-std | | | | | | | | | | | | |

### B-S (supplementary, single-source alignment reference)
| Seed | Acc | Macro-F1 | E-F1 | M-F1 | L-F1 | M-Pre | M-Rec | M->E | M->L | Rev | Jump | Smooth |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 42 | | | | | | | | | | | | |

q-MAE / q-RMSE / q-R2: **N/A** (no q-regression head).

## E. Complexity

| | Value |
|---|---|
| Total parameters (S+G+F) | 60,956 |
| Training time (Protocol A, 100+100 epochs) | TBD (GPU); CPU smoke run: ~0.2-0.5s/epoch on a 12-sample smoke subset, extrapolation to full 2000/class x 3 classes x 3 conditions not meaningful without GPU |
| Training time (Protocol B-D1, per seed) | TBD (GPU) |
| Peak VRAM | TBD (GPU) -- this architecture (1D convs, 60K params) is far lighter than dynamic_gin_tgp's; expect it to fit comfortably on 8GB even at batch=64 |
| Inference time (S+F only, per Algorithm 1's inference stage) | TBD (GPU) |

## F. Leakage audit

- Protocol A: source=C1 only, 70/30 internal split; C4/C6 used only for
  the final target-domain test evaluation, never for any hyperparameter
  or checkpoint-selection decision.
- Protocol B-S/B-D1: source-domain-only internal validation for all
  model-selection decisions (S+F pretraining's best-checkpoint choice,
  and the two-stage schedule length itself, both fixed from
  PAPER_SPEC.md's paper-derived values before any C6 contact); C6 touched
  exactly once.
- **C6 used for tuning: NO** (all three protocol variants).

## G. Reproduction confidence

**Medium.**

Reasoning: the mechanism (S->G->F pipeline, two-stage Algorithm 1, all
loss functions including the easy-to-get-backwards `L_MSE - alpha*MMD`
sign, verified via a dedicated gradient-direction test) is reproduced
with high confidence, and all training hyperparameters are Explicit in
the paper. However, this baseline carries three genuinely unresolved
physical/definitional gaps that directly affect Protocol A's
paper-comparison validity: (1) PHM2010 tool diameter/helix angle for
`Vst`'s shape (assumed, not sourced), (2) ref [41]'s exact I/II/III
boundary rule (proxied, not reproduced), and (3) the empirical
non-occurrence of Stage IV for these specific tools (a real data
constraint, not a choice, but one that changes the task from 4-class to
3-class). None of these affect Protocol B (which uses DC-PSR's own E/M/L
labels throughout, sidestepping items 2 and 3 entirely), so **Protocol
B-D1's number, once measured, should be trusted with higher confidence
than Protocol A's paper-comparison table.**

## Files

```
baselines/dp2net/
    PAPER_SPEC.md              component-by-component paper audit (incl. sec 6b empirical finding)
    README.md                  usage, training commands, results (this file's companion)
    FINAL_REPORT.md            this file
    preprocessing.py           low-pass filter, Vst construction, 4-stage proxy labels, window caches
    model.py                   S, G (+AdaIN), F=WDCNN, MMD
    train.py                   Protocol A/B-S/B-D1/smoke, two-stage Algorithm-1 training
    data/
        label_utils.py         Unified Protocol B-S/B-D1 labels/splits (imports 代码/ read-only)
        windows/                Protocol A cache (sample_manifest.csv-indexed)
        windows_unified/        Protocol B cache (unified_manifest.csv-indexed, 8/run)
    tests/
        test_pipeline.py       15 tests: preprocessing, S/G/F shapes, MMD, both stages' gradients (all pass on CPU)
outputs/dp2net/
    smoke/                              CPU smoke-test outputs
    original_protocol/target_{C4,C6}/   Protocol A outputs (populated after the user runs training)
    unified_protocol_B-S/seed<N>/       Protocol B-S outputs
    unified_protocol_B-D1/seed<N>/      Protocol B-D1 outputs (the DC-PSR D1 main-table candidate)
```

## Remaining uncertainty

1. Whether the model converges to near-paper accuracy on real data --
   only architecture/gradient/single-stage-overfit correctness confirmed
   on CPU so far.
2. True PHM2010 tool diameter/helix angle -- affects Vst's shape (not its
   period), and hence the physical-constraint term's exact target;
   unverifiable without the original PHM2010 CAD/tool documentation.
3. Whether Protocol A's adapted 3-class task is "easier" than the paper's
   4-class task in a way that materially inflates our accuracy numbers
   relative to the paper's own 90.91%/87.66% -- flagged explicitly, not
   resolved (would require reproducing failure-stage data the archive
   doesn't contain).
4. Real GPU training time/VRAM/inference-latency numbers, pending the
   user's manual run.
