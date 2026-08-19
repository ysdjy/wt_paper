# -*- coding: utf-8 -*-
r"""
Builds and caches the MTF-AViTK main (unbalanced) image dataset -- 5
sub-window MTF images per C1/C4/C6 cutting pass (90,000-100,000 stable
region, per PAPER_SPEC.md) -- plus a metadata table carrying both label
schemes:

  - `stage_original`: Paper B's own fixed cut-index thresholds
    (Initial 1-50 / Normal 51-175 / Severe 176-315) -- used by Protocol A.
  - `stage_unified` / `stage_unified_id`: this project's condition-relative
    DC-PSR labels (data/label_utils.py) -- used by Protocol B. Every
    sub-window inherits its parent run's label (run-level granularity);
    Protocol B evaluation aggregates the 5 sub-window predictions per run
    back to one run-level prediction (see train.py).

Output:
    data/images/{condition}_{run_id:03d}_{k}.npy   [384,384,3] uint8, k=0..4
    data/metadata.csv   (one row per sub-window image)

Run with:
    python data/build_dataset.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import preprocessing as P
import label_utils as L

DATA_DIR = Path(__file__).resolve().parent
IMG_DIR = DATA_DIR / "images"

# Explicit (PAPER_SPEC.md "Stage/label definition (original protocol)")
ORIGINAL_STAGE_RANGES = {"initial": (1, 50), "normal": (51, 175), "severe": (176, 315)}
ORIGINAL_STAGE_TO_ID = {"initial": 0, "normal": 1, "severe": 2}


def original_stage_of(run_id: int) -> str:
    for stage, (lo, hi) in ORIGINAL_STAGE_RANGES.items():
        if lo <= run_id <= hi:
            return stage
    raise ValueError(f"run_id {run_id} out of range")


def main():
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    unified = L.get_condition_relative_labels(("C1", "C4", "C6"))
    unified_lookup = {(r.condition, int(r.run_id)): r for r in unified.itertuples()}

    rows = []
    t0 = time.time()
    n_total = 0
    for cond in ["C1", "C4", "C6"]:
        for run_id in range(1, 316):
            images = P.build_main_samples(cond, run_id)  # 5 images
            u = unified_lookup[(cond, run_id)]
            stage_orig = original_stage_of(run_id)
            for k, img in enumerate(images):
                np.save(IMG_DIR / f"{cond}_{run_id:03d}_{k}.npy", img)
                rows.append({
                    "condition": cond,
                    "run_id": run_id,
                    "subwindow": k,
                    "stage_original": stage_orig,
                    "stage_original_id": ORIGINAL_STAGE_TO_ID[stage_orig],
                    "VB": u.VB,
                    "stage_unified": u.stage,
                    "stage_unified_id": u.stage_id,
                })
            n_total += 1
            if n_total % 100 == 0:
                print(f"{n_total}/945 runs done, {time.time()-t0:.1f}s elapsed")

    meta = pd.DataFrame(rows)
    meta.to_csv(DATA_DIR / "metadata.csv", index=False, encoding="utf-8-sig")
    print(f"Wrote {len(meta)} rows (sub-window level) to {DATA_DIR / 'metadata.csv'}")
    print(f"Total time: {time.time()-t0:.1f}s")
    print(meta.groupby(["condition", "stage_original"]).size())
    print(meta.groupby(["condition", "stage_unified"]).size())


if __name__ == "__main__":
    main()
