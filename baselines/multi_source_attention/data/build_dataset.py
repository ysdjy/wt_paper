# -*- coding: utf-8 -*-
r"""
Builds and caches the full Multi-source Attention image dataset (force +
vibration CWT images) for every C1/C4/C6 cutting pass, plus a metadata
table carrying both label schemes:

  - `stage_original`: Paper A's own EM-derived fixed pass-index partition
    (preprocessing.ORIGINAL_STAGE_RANGES) -- used by Protocol A.
  - `stage_unified` / `stage_unified_id`: this project's condition-relative
    DC-PSR labels (data/label_utils.py) -- used by Protocol B.

Output:
    data/images/{condition}_{run_id:03d}_force.npy   [224,224,3] uint8
    data/images/{condition}_{run_id:03d}_vib.npy     [224,224,3] uint8
    data/metadata.csv

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


def main():
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    unified = L.get_condition_relative_labels(("C1", "C4", "C6"))
    unified_lookup = {(r.condition, int(r.run_id)): r for r in unified.itertuples()}

    rows = []
    t0 = time.time()
    n_total = 0
    for cond in ["C1", "C4", "C6"]:
        for run_id in range(1, 316):
            force_img, vib_img = P.build_sample(cond, run_id)
            np.save(IMG_DIR / f"{cond}_{run_id:03d}_force.npy", force_img)
            np.save(IMG_DIR / f"{cond}_{run_id:03d}_vib.npy", vib_img)

            u = unified_lookup[(cond, run_id)]
            rows.append({
                "condition": cond,
                "run_id": run_id,
                "stage_original": P.original_stage_of(cond, run_id),
                "stage_original_id": P.ORIGINAL_STAGE_TO_ID[P.original_stage_of(cond, run_id)],
                "VB": u.VB,
                "stage_unified": u.stage,
                "stage_unified_id": u.stage_id,
            })
            n_total += 1
            if n_total % 100 == 0:
                print(f"{n_total}/945 done, {time.time()-t0:.1f}s elapsed")

    meta = pd.DataFrame(rows)
    meta.to_csv(DATA_DIR / "metadata.csv", index=False, encoding="utf-8-sig")
    print(f"Wrote {len(meta)} rows to {DATA_DIR / 'metadata.csv'}")
    print(f"Total time: {time.time()-t0:.1f}s")
    print(meta.groupby(["condition", "stage_original"]).size())
    print(meta.groupby(["condition", "stage_unified"]).size())


if __name__ == "__main__":
    main()
