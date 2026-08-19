# FINAL_REPORT.md -- Dynamic GIN + TGP

Status as of this report: implementation, unit tests, and end-to-end
smoke tests are complete and passing. **Real Protocol A/B training has
NOT been run yet** -- GPU was occupied by a concurrent baseline
(`baselines/mtf_avitk`) throughout this baseline's build, and per this
project's collaboration protocol GPU use by more than one Claude instance
at a time is disallowed. Per the user's stated preference, formal
multi-epoch training is left for the user to run manually via the
commands in `README.md` rather than run autonomously here. This report
will be updated with real numbers once those runs complete -- everything
below the results tables is final; the results tables themselves are
templates to be filled in.

## A. Paper fidelity

**Explicit components** (paper states unambiguously, high confidence):
dataset/channels (Fx,Fy,Fz,Vx,Vy,Vz, AE discarded), 50kHz native
sampling, first-300-passes-only rule, Initial/Normal/Severe stage
boundaries (1-50/51-210/211-315), stable-cut trim (40k pts each end),
10-portion division, 288-length windows, 5/2/3 stratified sampling
(-> 2520 total samples, verified), D1/D2/D3 split definitions, GASF
formula (Eq.2-4), GIN update rule (Eq.13, up to a typesetting
normalization-exponent slip), eps=0.5, 3-layer GIN+TGP schedule
(24->19->14->10 nodes, channels 32->64->128), output head
(AdaptiveAvgPool2d + Linear(128,3)), training hyperparameters (Adam,
lr=1e-4, L2=0.1, batch=4, epochs=50, LR-halving-on-plateau patience=10).

**Inferable components**: none requiring a distinct "Inferable" (as
opposed to "Explicit") status beyond what PAPER_SPEC.md already tables.

**Missing components** (paper silent, documented implementation choice
made): exact sample-window start-offset within a stable-region portion
(centered, chosen); cross-attention softmax normalization (added, paper
only says scores "weight and filter"); TGP's exact `DimTran`/conv axis
bookkeeping (Eq.14); top-k tie-breaking / per-row-vs-global-flatten
convention (global-flatten, symmetrized).

**Conflicts** (paper's own text/table/figure disagree):
1. Conv2d_1's `Ks=(1,9)` notation vs. its own stated I/O shapes -- only a
   full-channel-height `(6,9)` kernel reproduces `[4,1,6,288]->[4,14,1,288]`.
2. Spatial CNN (Conv2d_3/4) printed output sizes (285/284) are each ~1px
   larger than valid-convolution arithmetic on the stated kernels (5/3)
   gives (284/282, our implementation) -- no effect on trainability.
3. Top-k=144 (Sec 3.4 prose, paper's own selected optimum) vs Topk=288
   (Table 1's "Fusion" row) -- resolved in favor of 144 per task
   instruction #31.
4. Fig.9's "decay rate/factor" plot legend vs. the separately-stated L2
   factor (0.1) and LR-halving factor (0.5) in prose -- resolved by
   treating the two prose statements as authoritative and independent.

**Adaptations**: none beyond the above -- this is a straight
reimplementation of the paper's own described method, with no
DC-PSR-specific additions (no q-head, no fine-state auxiliary head, no
degradation prior) per task instruction #81.

## B. Original reproduction (Protocol A, D1)

| | Paper protocol | Paper result | Our result | Difference |
|---|---|---|---|---|
| D1 (C1+C4->C6) Accuracy | Adam/lr=1e-4/L2=0.1/batch=4/50ep, 2520 stratified samples | 95.71% | **TBD -- not yet run on GPU** | -- |
| Model parameters | -- | 321,002 | 321,950 (confirmed on CPU) | +0.29% |

**Confirmed on CPU** (architecture-level sanity, no full training needed):
parameter count within 0.3% of the paper's reported value; forward pass
shapes exactly match Table 1's I/O sizes throughout the network; gradient
flow verified finite across all trainable parameters except the 5
documented, paper-inherent exceptions (`graph_mlp`'s 4 params, dead due
to Eq.12's non-differentiable hard top-k; `tgp3.s_p`, unused since the
final TGP layer's pooled adjacency is never consumed downstream); a
single real bug (GASF's `sqrt`-at-zero gradient singularity) was found
and fixed by this project's own tests before any training was attempted.

## C. Unified protocol (Protocol B)

- Train conditions: C1+C4 (internal 0.7-stratified train / val split via
  `代码/main_experiment_3_fgds_psi_optimized.py::split_grouped_lifecycle`,
  reused byte-for-byte).
- Test condition: C6, full common run universe (up to 315 runs, not
  Protocol A's paper-native 300-pass truncation).
- Label definition: condition-relative Early/Middle/Late,
  `data/label_utils.py` (identical to every other baseline in this
  project's unified comparison).
- Source validation: model/epoch selection uses only the C1+C4 internal
  validation split's run-level accuracy; C6 is evaluated exactly once,
  after training completes.
- Target visibility: C6 never used for early stopping, hyperparameter
  selection, preprocessing choices, or checkpoint cherry-picking.
- Run-level aggregation: each C6 run's 10 stable-region-portion segment
  predictions are mean-probability-aggregated to one run-level prediction
  before any metric is computed.

## D. Full metrics (Protocol B, unified)

**Not yet run.** Template (5 seeds, project standard {42,52,62,72,82}):

| Seed | Acc | Macro-F1 | E-F1 | M-F1 | L-F1 | M-Pre | M-Rec | M->E | M->L | Rev | Jump | Smooth |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 42 | | | | | | | | | | | | |
| 52 | | | | | | | | | | | | |
| 62 | | | | | | | | | | | | |
| 72 | | | | | | | | | | | | |
| 82 | | | | | | | | | | | | |
| mean+-std | | | | | | | | | | | | |

q-MAE / q-RMSE / q-R2: **N/A** (no q-regression head, per task
instruction #71).

## E. Complexity

| | Value |
|---|---|
| Total parameters | 321,950 |
| Trainable parameters | 321,950 minus 5 dead-gradient params (see Sec A) -- all 321,950 are `requires_grad=True`; "trainable" in the effective-learning sense excludes the 5 documented exceptions |
| Training time (Protocol A, 50 epochs) | TBD (GPU) |
| Training time (Protocol B, per seed) | TBD (GPU) |
| Peak VRAM | TBD (GPU) -- CPU-side dev confirmed batch=16 OOMs even in system RAM; batch=4 (paper's own) is the safe default on an 8GB card |
| Inference time | TBD (GPU) -- paper reports preprocessing~=0.1129s, model compute~=0.0296s, total~=0.6425s/sample as a sanity reference only |

## F. Leakage audit

- Protocol A: source tools (C1,C4) internally split 0.7/0.3 by random
  sample-level permutation (fixed seed 42); target C6 used only for the
  single final test evaluation. No hyperparameter search touched C6.
- Protocol B: C1+C4 internal validation (stage-stratified, from
  `split_grouped_lifecycle`) used for all model-selection/early-stopping
  decisions; C6 touched exactly once. `FROZEN_CONFIG` equivalent: all
  hyperparameters (topk=144, lr=1e-4, batch=4, weight_decay=0.1) were
  fixed from PAPER_SPEC.md's paper-derived values before any C6 contact
  -- none were tuned against C6.
- **C6 used for tuning: NO** (both protocols).

## G. Reproduction confidence

**Medium-High.**

Reasoning: the data pipeline (raw-channel selection, stable-cut,
sample-count, stratified sampling) is Explicit and independently
verified exact (2520/2520 samples, matches paper). The macro-architecture
(temporal->GASF->spatial->cross-attention->graph->GIN->TGP->output) is
Explicit and shape-verified end-to-end against Table 1. Parameter count
matches the paper within 0.3%. The handful of pixel/axis-level
implementation choices (spatial CNN dims, TGP conv-axis bookkeeping,
top-k tie-breaking) are documented and do not affect trainability. The
one confirmed real bug (GASF sqrt-gradient singularity) was caught by
this project's own tests and fixed before any training was attempted --
a good sign for the reimplementation's overall soundness. The rating is
not "High" only because: (1) no real training run has yet confirmed the
model reaches anywhere near the paper's reported 95.71% D1 accuracy --
architecture correctness does not guarantee optimization/convergence
correctness, and (2) several Missing-in-paper implementation choices
(TGP's exact conv-axis bookkeeping, in particular) could not be verified
against the paper's own code (none is public).

**This confidence rating should be revisited once Protocol A's real D1
accuracy is measured** -- if it lands within ~92-98% of the paper's
95.71%, upgrade to High; if it is far outside that range, downgrade and
re-audit per task instruction #37 before trusting any Protocol B number.

## Files

```
baselines/dynamic_gin_tgp/
    PAPER_SPEC.md              component-by-component paper audit
    README.md                  usage, training commands, results (this file's companion)
    FINAL_REPORT.md            this file
    preprocessing.py           stable-cut, portioning, sample construction, window cache
    model.py                   full Table-1 architecture
    train.py                   Protocol A/B/smoke training + evaluation
    data/
        label_utils.py         Unified Protocol B labels/split (imports 代码/ read-only)
        windows/                945 cached [10,6,288] .npy files (all C1/C4/C6 runs)
        metadata.csv            per-run cache index + Protocol A stage_original labels
    tests/
        test_pipeline.py       13 tests: preprocessing, shapes, gradients, overfit (all pass on CPU)
outputs/dynamic_gin_tgp/
    smoke/                     CPU smoke-test outputs (synthetic-scale, not for the main table)
    original_protocol/         Protocol A outputs (populated after the user runs training)
    unified_protocol/seed<N>/  Protocol B outputs per seed (populated after the user runs training)
```

## Remaining uncertainty

1. Whether the model actually converges to near-paper accuracy on real
   data -- not yet tested end-to-end on GPU with real training (only
   architecture/shape/gradient correctness confirmed on CPU).
2. TGP's exact `DimTran` axis semantics (Eq.14) -- our reading is
   internally consistent and shape-correct but not verifiable against
   paper code (none public).
3. Whether `top_k=144` (our choice) or `top_k=288` (Table 1's literal
   value) performs better in practice -- only source-domain (C1<->C4)
   sanity comparison is licensed by the task's no-target-leakage rule;
   not yet run.
4. Real GPU training time/VRAM/inference-latency numbers, pending the
   user's manual run.
